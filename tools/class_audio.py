"""Transcribe una grabación de clase para usarla como contexto de un lote.

Uso (entorno aparte, no `.venv`; ver docs/owner.md):
    .venv-audio\\Scripts\\python tools/class_audio.py transcribe 1-inbox/<grabación> [--workers 4]

Escribe en private/class-audio/<nombre>/ (fuera de git: el repositorio es público):
    transcript.md    lo que se dijo, con quién habla; primero lo que dijo la profesora en chino
    segments.jsonl   los segmentos con tiempos, palabras y voz, por si hay que volver a ellos

Cómo decide quién habla: cada segmento lleva la huella de su voz (modelo 3D-Speaker de sherpa-onnx).
Se compara con las dos voces guardadas en private/class-audio/voices.json; la primera vez, sin voces
guardadas, se siembran por el tono (la voz alta es la profesora; TEACHER_MIN_HZ y LEARNER_MAX_HZ).
Cada grabación afina las voces guardadas. Lo que dice YAGO se transcribe peor (está aprendiendo):
se muestra, pero marcado como poco fiable y fuera del resumen.

Transcripción: faster-whisper (large-v3) en chino, en trozos paralelos; el inglés sale tal cual.
Todo es local salvo la descarga de modelos la primera vez. No llama a ningún LLM.
"""

import argparse
import datetime
import json
import multiprocessing as mp
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "private" / "class-audio"
VOICES = OUT / "voices.json"
DICTIONARY = ROOT / "5-output" / "dictionary.json"
MODELS = ROOT / ".venv-audio" / "models"
EMBEDDING_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/"
                 "3dspeaker_speech_eres2net_base_sv_zh-cn_3dspeaker_16k.onnx")
WHISPER_MODEL = "large-v3"
LANGID_MODEL = "small"                     # para detectar lo que Whisper tradujo del inglés
PROMPT = "以下是普通话的句子。"          # empuja a Whisper a escribir chino simplificado
SR = 16000
TEACHER_MIN_HZ, LEARNER_MAX_HZ = 165, 150  # solo para sembrar las voces la primera vez
MIN_MARGIN = 0.05                          # diferencia mínima de parecido para decidir quién habla
HAN = re.compile(r"[一-鿿]")


# ---------------------------------------------------------------- audio

def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(path):
    """Audio mono a 16 kHz, como float32."""
    raw = subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", str(path), "-vn", "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def split_points(audio, n):
    """Cortes para n trozos, cada uno en el punto más silencioso a ±5 s del reparto uniforme."""
    hop = SR // 100
    env = np.sqrt(np.convolve(audio ** 2, np.ones(hop * 3) / (hop * 3), mode="same")[::hop])
    cuts = [0.0]
    for k in range(1, n):
        c = int(len(audio) / SR * k / n * 100)
        a, b = max(c - 500, 0), min(c + 500, len(env) - 1)
        cuts.append((a + int(np.argmin(env[a:b + 1]))) / 100)
    return cuts + [len(audio) / SR]


def pitch(audio, a, b):
    """(fracción de tramos sonoros por encima de TEACHER_MIN_HZ, por debajo de LEARNER_MAX_HZ, mediana en Hz)."""
    x = audio[int(a * SR):int(b * SR)]
    n, hop, lmin, lmax = 640, 160, SR // 400, SR // 70
    if len(x) < n * 2:
        return 0.0, 0.0, 0.0
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop]
    e = (fr ** 2).sum(1)
    fr = fr[e > np.percentile(e, 40)]
    fr = fr - fr.mean(1, keepdims=True)
    spec = np.fft.rfft(fr, 2 * n)
    ac = np.fft.irfft(spec * np.conj(spec))[:, :n]
    ac = ac / (ac[:, :1] + 1e-9)
    seg = ac[:, lmin:lmax]
    f = SR / (seg.argmax(1) + lmin)
    f = f[seg.max(1) > 0.5]
    if len(f) < 3:
        return 0.0, 0.0, 0.0
    return float((f >= TEACHER_MIN_HZ).mean()), float((f < LEARNER_MAX_HZ).mean()), float(np.median(f))


# ---------------------------------------------------------------- transcripción

def _transcribe_chunk(args):
    path, start, end, threads = args
    from faster_whisper import WhisperModel
    audio = decode(path)[int(start * SR):int(end * SR)]
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8", cpu_threads=threads)
    segs, _ = model.transcribe(audio, language="zh", initial_prompt=PROMPT, word_timestamps=True, vad_filter=True,
                               beam_size=3, condition_on_previous_text=False)
    out = []
    for s in segs:
        out.append(dict(start=s.start + start, end=s.end + start, text=s.text.strip(), logprob=s.avg_logprob,
                        words=[dict(s=w.start + start, e=w.end + start, w=w.word, p=w.probability) for w in s.words or []]))
    print(f"  trozo {start / 60:.0f}–{end / 60:.0f} min: {len(out)} segmentos", flush=True)
    return out


def transcribe(path, audio, workers):
    cuts = split_points(audio, workers)
    threads = max(1, (mp.cpu_count() or 4) // workers)
    jobs = [(str(path), cuts[k], cuts[k + 1], threads) for k in range(workers)]
    with mp.get_context("spawn").Pool(workers) as pool:
        parts = pool.map(_transcribe_chunk, jobs)
    return sorted((s for p in parts for s in p), key=lambda s: s["start"])


# ---------------------------------------------------------------- quién habla

def embedder():
    import sherpa_onnx
    model = MODELS / Path(EMBEDDING_URL).name
    if not model.exists():
        MODELS.mkdir(parents=True, exist_ok=True)
        print(f"Descargando el modelo de voz ({model.name})…", flush=True)
        urllib.request.urlretrieve(EMBEDDING_URL, model)
    cfg = sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(model), num_threads=4)
    return sherpa_onnx.SpeakerEmbeddingExtractor(cfg)


def embed(ex, audio, a, b):
    x = audio[int(a * SR):int(b * SR)]
    if len(x) < SR * 0.4:
        return None
    st = ex.create_stream()
    st.accept_waveform(SR, x)
    st.input_finished()
    v = np.array(ex.compute(st))
    return v / (np.linalg.norm(v) + 1e-9)


def label_speakers(segs, audio):
    """Pone a cada segmento who = P (profesora), Y (YAGO) o ? y actualiza las voces guardadas."""
    ex = embedder()
    for s in segs:
        s["hi"], s["lo"], s["f0"] = pitch(audio, s["start"], s["end"])
        s["_emb"] = embed(ex, audio, s["start"], s["end"])
    have = [s for s in segs if s["_emb"] is not None]
    voices = json.loads(VOICES.read_text(encoding="utf-8")) if VOICES.exists() else {}
    if voices:
        cent = {k: np.array(v["centroid"]) for k, v in voices.items()}
    else:  # primera vez: sembrar por el tono
        seed = {"teacher": [s["_emb"] for s in have if s["hi"] >= 0.8 and s["lo"] <= 0.1],
                "learner": [s["_emb"] for s in have if s["lo"] >= 0.8 and s["hi"] <= 0.1]}
        if min(len(v) for v in seed.values()) < 5:
            sys.exit("No hay bastantes segmentos claros de cada voz para sembrar las voces: revisar TEACHER_MIN_HZ.")
        cent = {k: np.mean(v, 0) for k, v in seed.items()}
    for _ in range(3):  # afinar los centros con esta grabación
        for s in have:
            st, sl = float(s["_emb"] @ cent["teacher"]), float(s["_emb"] @ cent["learner"])
            s["who"] = "P" if st - sl > MIN_MARGIN else "Y" if sl - st > MIN_MARGIN else "?"
        for k, w in (("teacher", "P"), ("learner", "Y")):
            members = [s["_emb"] for s in have if s["who"] == w]
            if members:
                c = np.mean(members, 0)
                cent[k] = c / (np.linalg.norm(c) + 1e-9)
    for s in segs:
        s.setdefault("who", "?")
        s.pop("_emb")
    today = datetime.date.today().isoformat()
    new = {}
    for k, w in (("teacher", "P"), ("learner", "Y")):
        n_new = sum(1 for s in have if s["who"] == w)
        old = voices.get(k, {})
        n_old = old.get("segments", 0)
        c = cent[k] if not old else (np.array(old["centroid"]) * n_old + cent[k] * n_new) / max(1, n_old + n_new)
        new[k] = dict(centroid=[round(float(x), 6) for x in c / (np.linalg.norm(c) + 1e-9)],
                      segments=n_old + n_new, updated=today)
    VOICES.parent.mkdir(parents=True, exist_ok=True)
    VOICES.write_text(json.dumps(new, indent=1), encoding="utf-8")


def flag_translated(segs, audio):
    """Marca lang=en lo que la profesora dijo en inglés y Whisper, forzado a chino, tradujo.
    Solo frases de 4 hanzi o más: con menos, el detector (modelo small) confunde 对 o 可以 con inglés."""
    from faster_whisper import WhisperModel
    model = WhisperModel(LANGID_MODEL, device="cpu", compute_type="int8", cpu_threads=mp.cpu_count() or 4)
    for s in segs:
        if s["who"] != "P" or len(HAN.findall(s["text"])) < 4:
            continue
        _, _, probs = model.detect_language(audio[int(s["start"] * SR):int(s["end"] * SR)])
        p = dict(probs)
        if p.get("en", 0) >= 0.8 and p.get("en", 0) > p.get("zh", 0):
            s["lang"] = "en"


# ---------------------------------------------------------------- resumen

def simplified(t):
    import zhconv
    return zhconv.convert(t, "zh-cn")


def deck_words():
    if not DICTIONARY.exists():
        return {}
    d = json.loads(DICTIONARY.read_text(encoding="utf-8"))
    return {e["hanzi"]: e for e in d["entries"] if e.get("hanzi") and e.get("kind") in ("word", "expression")}


def mark_new(text, words):
    """Pone entre 【】 los caracteres que no cubre ninguna palabra del mazo (el más largo primero)."""
    pieces, i = [], 0  # (texto, es_nuevo)
    while i < len(text):
        n = next((n for n in range(min(6, len(text) - i), 0, -1) if text[i:i + n] in words), 0)
        if n:
            pieces.append((text[i:i + n], False)); i += n
        else:
            pieces.append((text[i], bool(HAN.match(text[i])))); i += 1
    out, new, run = [], [], ""
    for piece, is_new in pieces + [("", False)]:
        if is_new:
            run += piece; continue
        if run:
            out.append(f"【{run}】"); new.append(run); run = ""
        out.append(piece)
    return "".join(out), new


def write_transcript(path, segs, dest):
    from collections import Counter
    from pypinyin import pinyin, Style
    words = deck_words()
    ts = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"
    teacher_zh, heard, new = [], Counter(), Counter()
    for s in segs:
        s["text"] = simplified(s["text"])
        han = "".join(HAN.findall(s["text"]))
        if s["who"] == "P" and s.get("lang") != "en" and han and len(han) >= 0.5 * len(re.sub(r"[\W\d_]", "", s["text"])):
            marked, nw = mark_new(s["text"], words)
            teacher_zh.append((s, marked))
            new.update(nw)
            for w in words:
                if w in han:
                    heard[w] += 1
    L = [f"# Clase grabada: {path.name}", "",
         "Transcripción automática (Whisper), local y privada: no se versiona. Contexto para el lote: qué se trabajó "
         "en clase y cómo lo dijo la profesora. Tiene errores; lo que entre al mazo se comprueba como cualquier apunte.",
         "Quién habla, por la voz: **P** profesora, **Y** YAGO (poco fiable: está aprendiendo), **?** sin decidir. "
         "«[inglés]»: lo dijo en inglés y Whisper lo tradujo al chino; no cuenta como chino de clase.", "",
         "## Lo que dijo la profesora en chino", "",
         "Entre 【】, lo que no cubre ninguna palabra del mazo.", ""]
    for s, marked in teacher_zh:
        py = " ".join(x[0] for x in pinyin("".join(HAN.findall(s["text"])), style=Style.TONE))
        L.append(f"- `{ts(s['start'])}` {marked} · {py}")
    L += ["", "## Palabras del mazo que usó la profesora", "",
          ", ".join(f"{w} ({n})" for w, n in heard.most_common()) or "(ninguna)", "",
          "## Lo que no está en el mazo (por frecuencia)", "",
          ", ".join(f"{w} ({n})" for w, n in new.most_common()) or "(nada)", "",
          "## Toda la clase", ""]
    for s in segs:
        who = {"P": "**P**", "Y": "Y ·", "?": "? ·"}[s["who"]]
        text = s["text"] if s["who"] != "Y" else f"_{s['text']}_"
        if s.get("lang") == "en":
            text = f"[inglés] {text}"
        L.append(f"- `{ts(s['start'])}` {who} {text}")
    (dest / "transcript.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(dest / "segments.jsonl", "w", encoding="utf-8") as f:
        for s in segs:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    return len(teacher_zh), sum(1 for s in segs if s["who"] == "P"), sum(1 for s in segs if s["who"] == "Y")


def cmd_transcribe(src, workers):
    path = Path(src).resolve()
    if not path.exists():
        sys.exit(f"No existe {src}")
    dest = OUT / path.stem
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Leyendo {path.name}…", flush=True)
    audio = decode(path)
    print(f"{len(audio) / SR / 60:.0f} min de audio. Transcribiendo en {workers} trozos (tarda)…", flush=True)
    segs = transcribe(path, audio, workers)
    print("Separando voces…", flush=True)
    label_speakers(segs, audio)
    print("Buscando lo que dijo en inglés…", flush=True)
    flag_translated(segs, audio)
    zh, p, y = write_transcript(path, segs, dest)
    print(f"Listo: {len(segs)} segmentos ({p} de la profesora, {y} de YAGO; {zh} frases de la profesora en chino).")
    print(f"→ {(dest / 'transcript.md').relative_to(ROOT).as_posix()}")
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcribe", help="transcribe una grabación de clase a private/class-audio/")
    t.add_argument("audio")
    t.add_argument("--workers", type=int, default=4, help="trozos en paralelo (cada uno carga el modelo: ~2,5 GB de RAM)")
    a = ap.parse_args()
    return cmd_transcribe(a.audio, a.workers)


if __name__ == "__main__":
    sys.exit(main())
