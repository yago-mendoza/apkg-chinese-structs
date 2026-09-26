"""Consulta, validación, audio y compilación del mazo de chino.

Uso:
    python anki.py lookup <hanzi|pinyin|significado>
    python anki.py gaps
    python anki.py check
    python anki.py audio [--dry-run]
    python anki.py build [--allow-missing-audio]
    python anki.py push [--allow-missing-audio] [--no-sync]

No llama a ningún LLM. `audio` usa la red (Azure Speech) y nunca repite audios
ya guardados en 3-data/audio/. `push` compila, importa en Anki desktop (abriéndolo si
hace falta) mediante el complemento AnkiConnect y sincroniza con AnkiWeb.
"""

import argparse
import datetime
import hashlib
import html
import itertools
import json
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "3-data"                    # fuente de verdad, mantenida por el agente
LEXICON = DATA / "lexicon.yaml"
EXERCISES = DATA / "exercises.yaml"
MEDIA = DATA / "audio"                  # MP3 generados; no regenerar
AUDIO_MANIFEST = MEDIA / "index.yaml"
INBOX = ROOT / "1-inbox"                  # apuntes en bruto de YAGO
OUTPUT = ROOT / "5-output"                # lo que sale: mazo y futuras exportaciones
APKG = OUTPUT / "chino-practico.apkg"
ANKI_CONNECT = "http://127.0.0.1:8765"

# Identidades estables: no cambiarlas nunca, o Anki verá un mazo/modelo nuevo.
GUID_NAMESPACE = "apkg-chinese-structs"
DECK_NAME = "🐉 Chino práctico"          # un subdeck por mes: "🐉 Chino práctico::2026-09"
DECK_ID_BASE = 1_758_800_000_000         # ID del subdeck = base + AAAAMM
MODEL_TYPED_ID = 1_758_800_101
MODEL_SELF_ID = 1_758_800_102
AUDIO_PREFIX = "acs_"

AZURE_VOICE = os.environ.get("AZURE_SPEECH_VOICE", "zh-CN-YunyangNeural")
# Más despacio que lo normal: más claro para aprender tonos.
AZURE_RATE = "-30%"
AZURE_FORMAT = "audio-24khz-96kbitrate-mono-mp3"

TONE_MARKS = {
    "a": "āáǎà", "e": "ēéěè", "i": "īíǐì",
    "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ",
}
UNMARK = {m: (v, t + 1) for v, ms in TONE_MARKS.items() for t, m in enumerate(ms)}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- datos

def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load():
    lex = load_yaml(LEXICON)
    exe = load_yaml(EXERCISES)
    return lex.get("entries", []), exe.get("sentences", []), exe.get("exercises", [])


def load_manifest():
    if AUDIO_MANIFEST.exists():
        return load_yaml(AUDIO_MANIFEST).get("audio", {})
    return {}


def save_manifest(manifest):
    MEDIA.mkdir(exist_ok=True)
    with open(AUDIO_MANIFEST, "w", encoding="utf-8") as f:
        f.write("# Procedencia de cada audio. Generado por `anki.py audio`.\n")
        yaml.safe_dump({"audio": manifest}, f, allow_unicode=True, sort_keys=True)


# ---------------------------------------------------------------- pinyin

def numeric_to_marked(text):
    """ni3 hao3 -> nǐ hǎo; xie4 xie5 -> xiè xie. Acepta v o u: para ü."""
    def syllable(m):
        body, tone = m.group(1).replace("u:", "ü").replace("v", "ü"), m.group(2)
        tone = int(tone) if tone else 5
        if tone == 5:
            return body
        low = body.lower()
        if "a" in low:
            i = low.index("a")
        elif "e" in low:
            i = low.index("e")
        elif "ou" in low:
            i = low.index("o")
        else:
            i = max(low.rfind(v) for v in "iouü")
        if i < 0:
            return body
        return body[:i] + TONE_MARKS[low[i]][tone - 1] + body[i + 1:]
    return re.sub(r"([a-zA-Zü:]+)([1-5]?)", syllable, text)


def tones_to_numeric(hanzi, digits):
    """什么 + 25 -> shen2 me5, para comprobar una respuesta de solo tonos."""
    from pypinyin import Style, lazy_pinyin
    chars = "".join(c for c in hanzi or "" if "一" <= c <= "鿿")
    syllables = lazy_pinyin(chars, style=Style.NORMAL, v_to_u=True)
    if not chars or len(syllables) != len(digits):
        return None
    return " ".join(s + d for s, d in zip(syllables, digits))


def strip_tones(text):
    return "".join(UNMARK.get(c, (c,))[0] for c in unicodedata.normalize("NFC", text))


def compact(text):
    return re.sub(r"[\s'·\-]", "", unicodedata.normalize("NFC", text).lower())


def pypinyin_readings(hanzi):
    """Todas las lecturas con tono que propone pypinyin (combinando heterónimos)."""
    from pypinyin import Style, pinyin
    chars = [c for c in hanzi if "一" <= c <= "鿿"]
    options = pinyin(chars, style=Style.TONE, heteronym=True) if chars else []
    combos = itertools.islice(itertools.product(*options), 64)
    return {"".join(c) for c in combos}


def pinyin_warning(hanzi, reading):
    if not hanzi or not reading:
        return None
    known = pypinyin_readings(hanzi)
    if not known or compact(reading) in known:
        return None
    if compact(strip_tones(reading)) in {strip_tones(k) for k in known}:
        return f"tono de «{reading}» distinto de pypinyin ({' / '.join(sorted(known))})"
    return f"«{reading}» no coincide con pypinyin ({' / '.join(sorted(known))})"


# ---------------------------------------------------------------- consultas

def sentence_text(s):
    return "".join(seg["text"] for seg in s.get("segments", []))


def sentence_pinyin(s):
    return " ".join(seg["pinyin"] for seg in s.get("segments", []) if seg.get("pinyin"))


def standalone(e):
    """yes | rare | no | None. YAML lee yes/no sin comillas como booleanos."""
    v = e.get("standalone")
    return {True: "yes", False: "no"}.get(v, v) if v is not None else None


def free_words_containing(e, entries):
    """Palabras registradas que contienen el hanzi de una entrada ligada."""
    h = e.get("hanzi")
    return [w for w in entries if h and w is not e and w.get("kind") in ("word", "expression")
            and h in (w.get("hanzi") or "")]


def exercise_roles(ex, sentences_by_id, entries_by_id=None):
    """{entry_id: rol} para cada aparición de una entrada en un ejercicio."""
    roles = {}
    group = (entries_by_id or {}).get(ex.get("group"))
    if group:
        roles[group["id"]] = "grupo"
        for m in group.get("members", []):
            roles[m["ref"]] = "contexto"
    for sid in ex.get("reveal", []):
        for seg in sentences_by_id.get(sid, {}).get("segments", []):
            if seg.get("ref"):
                roles.setdefault(seg["ref"], "ejemplo")
    sid = ex.get("sentence")
    if sid:
        for seg in sentences_by_id.get(sid, {}).get("segments", []):
            if seg.get("ref"):
                roles[seg["ref"]] = "contexto"
    for rid in ex.get("refs", []):
        roles.setdefault(rid, "referencia")
    for cid in ex.get("context", []):
        roles[cid] = "contexto"
    for tid in ex.get("targets", []):
        roles[tid] = "objetivo"
    return roles


def cmd_lookup(query):
    entries, sentences, exercises = load()
    sby = {s["id"]: s for s in sentences}
    eby = {e["id"]: e for e in entries}
    q = unicodedata.normalize("NFC", query.strip().lower())
    q_marked = compact(numeric_to_marked(q)) if re.search(r"[a-z][1-5]", q) else compact(q)
    q_plain = compact(strip_tones(q_marked))

    def matches(e):
        if q in (e.get("hanzi") or "") or q == e.get("id"):
            return True
        py = compact(e.get("pinyin") or "")
        if py and (q_marked == py or q_plain == strip_tones(py)):
            return True
        text = " ".join(str(v) for v in (e.get("meaning") or {}).values())
        text += " " + (e.get("title") or "")
        return bool(q) and q in text.lower()

    found = [e for e in entries if matches(e)]
    if not found:
        print(f"Sin entradas para «{query}».")
    for e in found:
        print(f"\n[{e['id']}] {e['kind']}  {e.get('hanzi', e.get('title', ''))}  {e.get('pinyin', '')}")
        if e.get("meaning"):
            print("  " + " | ".join(f"{k}: {v}" for k, v in e["meaning"].items()))
        if standalone(e):
            print(f"  se usa solo: {standalone(e)}")
            if standalone(e) != "yes":
                print("  aparece en: " + (", ".join(w["hanzi"] for w in free_words_containing(e, entries))
                                          or "ninguna palabra registrada"))
        if e.get("relations"):
            print("  relaciones: " + ", ".join(e["relations"]))
        if e.get("kind") == "group":
            print(f"  {e.get('basis')}: {e.get('explanation', '')}")
            for m in e.get("members", []):
                print(f"    {eby.get(m['ref'], {}).get('hanzi', m['ref'])}  {m.get('cue', '')}")
        groups = [g for g in entries if g.get("kind") == "group"
                  and any(m["ref"] == e["id"] for m in g.get("members", []))]
        if groups:
            print("  grupos: " + ", ".join(f"{g['id']} ({g.get('basis')})" for g in groups))
        for c in e.get("comments", []):
            print(f"  comentario ({c.get('kind')}, {'privado' if c.get('private', True) else 'público'}): {c.get('text')}")
        rows = [(ex["type"], ex["id"], exercise_roles(ex, sby, eby)[e["id"]])
                for ex in exercises if e["id"] in exercise_roles(ex, sby, eby)]
        for t, xid, role in sorted(rows):
            print(f"  {t:8} {xid:28} {role}")
        uses = [s["id"] for s in sentences if any(seg.get("ref") == e["id"] for seg in s["segments"])]
        if uses:
            print("  frases: " + ", ".join(uses))
    # Palabras de frases aún no registradas que coinciden.
    loose = {f"{seg['text']} {seg.get('pinyin', '')}".strip() for s in sentences for seg in s["segments"]
             if not seg.get("ref") and seg.get("pinyin") and q and
             (q in seg["text"] or q_plain == compact(strip_tones(seg["pinyin"])))}
    if loose:
        print("\nEn frases, sin entrada: " + ", ".join(sorted(loose)))


SKILL_GROUPS = {
    "lectura": {"reading"},
    "escucha": {"listening"},
    "producción": {"production", "speaking"},
    "tonos": {"tones"},
}


def cmd_gaps():
    entries, sentences, exercises = load()
    sby = {s["id"]: s for s in sentences}
    eby = {e["id"]: e for e in entries}
    manifest = load_manifest()
    print("Cobertura registrada (no equivale a aprendido; sin datos de repaso).\n")
    print(f"{'entrada':22} {'lect':>4} {'escu':>4} {'prod':>4} {'tono':>4} {'ctx':>4}")
    for e in entries:
        if e["kind"] not in ("word", "expression"):
            continue
        counts = {k: 0 for k in SKILL_GROUPS}
        contexts = set()
        for ex in exercises:
            role = exercise_roles(ex, sby, eby).get(e["id"])
            if role == "objetivo":
                for k, skills in SKILL_GROUPS.items():
                    counts[k] += bool(skills & set(ex.get("skills", [])))
            if role in ("contexto", "ejemplo") and (ex.get("sentence") or ex.get("reveal")):
                contexts.update([ex.get("sentence")] + ex.get("reveal", []))
        missing = [k for k, v in counts.items() if not v and k != "tonos"]
        flag = "  falta: " + ", ".join(missing) if missing else ""
        print(f"{e['id']:22} {counts['lectura']:>4} {counts['escucha']:>4} "
              f"{counts['producción']:>4} {counts['tonos']:>4} {len(contexts - {None}):>4}{flag}")
    others = [e for e in entries if e["kind"] not in ("word", "expression")]
    for e in others:
        n = sum(e["id"] in exercise_roles(ex, sby, eby) for ex in exercises)
        print(f"{e['id']:22} ({e['kind']}) en {n} ejercicio(s)")
    bound = [e for e in entries if standalone(e) in ("no", "rare")]
    if bound:
        print("\nSentidos que no se usan solos (se aprenden dentro de palabras):")
        for e in bound:
            words = free_words_containing(e, entries)
            where = ", ".join(w["hanzi"] for w in words) if words else "AVISO: ninguna palabra registrada"
            print(f"  {e.get('hanzi')} {e.get('pinyin', '')} ({standalone(e)}) → {where}")
    pending = sorted(t for t in required_audio(entries, sentences, exercises) if t not in manifest)
    print(f"\nAudio pendiente: {len(pending)}" + (f" → {', '.join(pending)}" if pending else ""))
    loose = sorted({seg["text"] for s in sentences for seg in s["segments"]
                    if not seg.get("ref") and seg.get("pinyin")})
    if loose:
        print("Palabras en frases sin entrada: " + ", ".join(loose))
    raw = sorted(f.name for f in INBOX.glob("*.txt")) if INBOX.exists() else []
    print(f"Inbox sin procesar: {len(raw)}" + (f" → {', '.join(raw)}" if raw else ""))


# ---------------------------------------------------------------- validación

def answer_hanzi(ex, sby):
    if ex.get("answer", {}).get("hanzi"):
        return ex["answer"]["hanzi"]
    if ex.get("sentence") in sby:
        return sentence_text(sby[ex["sentence"]])
    return None


def wants_audio(ex, eby):
    """Si la respuesta lleva audio. El contraste visual (大/太/天) se decide mirando la
    forma: no lo necesita. El de homófonos sí, porque el sonido es lo que se contrasta."""
    if ex.get("type") == "components":
        return False
    if ex.get("type") == "contrast":
        return eby.get(ex.get("group"), {}).get("basis") == "homophone"
    return True


def required_audio(entries, sentences, exercises):
    """Textos chinos que necesitan audio: respuestas, frases y pronunciación."""
    sby = {s["id"]: s for s in sentences}
    eby = {e["id"]: e for e in entries}
    texts = set()
    for ex in exercises:
        if answer_hanzi(ex, sby) and wants_audio(ex, eby):
            texts.add(answer_hanzi(ex, sby))
        for sid in ex.get("reveal", []) + ([ex["sentence"]] if ex.get("sentence") else []):
            if sid in sby:
                texts.add(sentence_text(sby[sid]))
    for e in entries:
        if e.get("audio_text"):
            texts.add(e["audio_text"])
    return texts


def validate(entries, sentences, exercises, require_audio=True):
    errors, warnings = [], []
    ids = [x["id"] for x in entries + sentences + exercises if "id" in x]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"ID repetido: {dup}")
    for x in entries + sentences + exercises:
        if "id" not in x:
            errors.append(f"elemento sin id: {x}")
    known = set(ids)
    eby = {e["id"]: e for e in entries if "id" in e}
    sby = {s["id"]: s for s in sentences if "id" in s}

    def ref(owner, rid):
        if rid not in known:
            errors.append(f"{owner}: referencia rota «{rid}»")

    for e in entries:
        for rid in e.get("relations", []):
            ref(e["id"], rid)
        if e.get("kind") in ("word", "expression", "character") and not (e.get("hanzi") and e.get("pinyin")):
            errors.append(f"{e['id']}: falta hanzi o pinyin")
        w = pinyin_warning(e.get("hanzi"), e.get("pinyin"))
        if w and not e.get("accept_pinyin_mismatch"):
            warnings.append(f"{e['id']}: {w}")
        if e.get("kind") in ("word", "expression") and e.get("pinyin") and not e.get("meaning"):
            warnings.append(f"{e['id']}: sin significado")
        if e.get("standalone") is not None and standalone(e) not in ("yes", "rare", "no"):
            errors.append(f"{e['id']}: standalone debe ser yes, rare o no")
        if standalone(e) in ("no", "rare") and not free_words_containing(e, entries):
            warnings.append(f"{e['id']}: no se usa solo y no hay ninguna palabra registrada que lo contenga")
        if e.get("kind") == "group":
            members = e.get("members") or []
            if e.get("basis") not in ("visual", "homophone", "pattern"):
                errors.append(f"{e['id']}: basis debe ser visual, homophone o pattern")
            if len(members) < 2:
                errors.append(f"{e['id']}: un grupo necesita al menos 2 miembros")
            if e.get("basis") in ("visual", "homophone") and len(members) > 4:
                errors.append(f"{e['id']}: máximo 4 miembros en un grupo de contraste")
            for m in members:
                ref(e["id"], m.get("ref"))
                if not m.get("cue"):
                    warnings.append(f"{e['id']}: {m.get('ref')} sin rasgo distintivo (cue)")
            if e.get("piece"):
                ref(e["id"], e["piece"])
    for s in sentences:
        for seg in s.get("segments", []):
            if seg.get("ref"):
                ref(s["id"], seg["ref"])
                target = eby.get(seg["ref"], {})
                if target.get("hanzi") and target["hanzi"] != seg["text"]:
                    warnings.append(f"{s['id']}: «{seg['text']}» enlaza a {seg['ref']} ({target['hanzi']})")
                if target.get("pinyin") and seg.get("pinyin") and not seg.get("sandhi") and \
                        compact(target["pinyin"]) != compact(seg["pinyin"]):
                    warnings.append(f"{s['id']}: pinyin de «{seg['text']}» distinto de {seg['ref']}")
        if not s.get("translation"):
            errors.append(f"{s['id']}: falta traducción")
    types = {"read", "listen", "tones", "cloze", "produce", "speak", "meaning", "components",
             "contrast", "derive", "pinyin-meaning", "build"}
    seen = {}
    for ex in exercises:
        xid = ex["id"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ex.get("added", ""))):
            errors.append(f"{xid}: falta added (AAAA-MM-DD), decide su subdeck mensual")
        # Redundancia: mismo tipo y mismos objetivos. Repetir algo como contexto no cuenta.
        key = (ex.get("type"), tuple(sorted(ex.get("targets", []))))
        if key in seen:
            warnings.append(f"{xid}: evalúa lo mismo que {seen[key]} ({key[0]}); ¿redundante?")
        seen.setdefault(key, xid)
        if ex.get("type") not in types:
            errors.append(f"{xid}: tipo desconocido «{ex.get('type')}»")
        if not ex.get("targets"):
            errors.append(f"{xid}: sin objetivos (targets)")
        if not ex.get("skills"):
            errors.append(f"{xid}: sin capacidades evaluadas (skills)")
        for rid in ex.get("targets", []) + ex.get("context", []) + ex.get("refs", []) + ex.get("reveal", []):
            ref(xid, rid)
        if ex.get("sentence"):
            ref(xid, ex["sentence"])
        ans = ex.get("answer") or {}
        if not (ans.get("typed") or ans.get("pinyin") or ans.get("meaning")):
            errors.append(f"{xid}: falta respuesta")
        if not (ex.get("prompt") or {}).get("text"):
            errors.append(f"{xid}: falta consigna")
        typed = ans.get("typed")
        if typed and re.fullmatch(r"[1-5]+", typed):
            # Solo tonos: un dígito por sílaba (什么 → 25).
            numeric = tones_to_numeric(ans.get("hanzi"), typed)
            if numeric is None:
                errors.append(f"{xid}: typed «{typed}» necesita un tono por sílaba de «{ans.get('hanzi')}»")
            elif ans.get("pinyin") and compact(numeric_to_marked(numeric)) != compact(ans["pinyin"]):
                errors.append(f"{xid}: tonos «{typed}» no equivalen a «{ans['pinyin']}»")
        elif typed and ans.get("pinyin") and compact(numeric_to_marked(typed)) != compact(ans["pinyin"]):
            errors.append(f"{xid}: typed «{typed}» no equivale a «{ans['pinyin']}»")
        if ex.get("type") in ("contrast", "derive"):
            g = eby.get(ex.get("group"), {})
            refs = [m.get("ref") for m in g.get("members", [])]
            if g.get("kind") != "group":
                errors.append(f"{xid}: {ex['type']} necesita un group válido")
            elif not set(ex.get("targets", [])) <= set(refs):
                errors.append(f"{xid}: los objetivos deben ser miembros de {g['id']}")
            elif ex["type"] == "derive" and g.get("basis") != "pattern":
                errors.append(f"{xid}: derive necesita un grupo de tipo pattern")
        elif ex.get("group"):
            ref(xid, ex["group"])
        if ex.get("type") == "cloze":
            segs = sby.get(ex.get("sentence"), {}).get("segments", [])
            if not any(seg.get("ref") == ex.get("gap") for seg in segs):
                errors.append(f"{xid}: el hueco «{ex.get('gap')}» no está en la frase")
        if (ex.get("prompt") or {}).get("audio") and not answer_hanzi(ex, sby):
            errors.append(f"{xid}: escucha sin texto chino que sonorizar")
        w = pinyin_warning(ans.get("hanzi"), ans.get("pinyin"))
        accepted = any(e.get("accept_pinyin_mismatch") and e.get("hanzi") == ans.get("hanzi")
                       for e in entries)
        if w and not accepted:
            warnings.append(f"{xid}: {w}")
    if require_audio:
        manifest = load_manifest()
        for t in sorted(required_audio(entries, sentences, exercises)):
            if t not in manifest:
                errors.append(f"audio requerido sin generar: {t}")
            elif not (MEDIA / manifest[t]["file"]).exists():
                errors.append(f"audio registrado pero ausente: {manifest[t]['file']}")
    return errors, warnings


def report(errors, warnings):
    for w in warnings:
        print(f"AVISO  {w}")
    for e in errors:
        print(f"ERROR  {e}")
    print(f"\n{len(errors)} error(es), {len(warnings)} aviso(s).")


def cmd_check(require_audio):
    errors, warnings = validate(*load(), require_audio=require_audio)
    report(errors, warnings)
    return 1 if errors else 0


# ---------------------------------------------------------------- audio

def audio_key(text, voice):
    raw = json.dumps([text, voice, AZURE_RATE, AZURE_FORMAT], ensure_ascii=False, sort_keys=True)
    return AUDIO_PREFIX + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16] + ".mp3"


def azure_tts(text, voice, key, region):
    ssml = (f"<speak version='1.0' xml:lang='zh-CN'><voice name='{voice}'>"
            f"<prosody rate='{AZURE_RATE}'>{html.escape(text)}</prosody></voice></speak>")
    req = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": AZURE_FORMAT, "User-Agent": "apkg-chinese-structs"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def cmd_audio(dry_run):
    entries, sentences, exercises = load()
    manifest = load_manifest()
    pending = sorted(t for t in required_audio(entries, sentences, exercises) if t not in manifest)
    print(f"Audio pendiente: {len(pending)}")
    for t in pending:
        print("  " + t)
    if dry_run or not pending:
        return 0
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION")
    if not key or not region:
        print("\nFaltan AZURE_SPEECH_KEY y/o AZURE_SPEECH_REGION (ver .env.example).")
        return 1
    MEDIA.mkdir(exist_ok=True)
    for t in pending:
        name = audio_key(t, AZURE_VOICE)
        path = MEDIA / name
        if not path.exists():
            path.write_bytes(azure_tts(t, AZURE_VOICE, key, region))
        manifest[t] = {"file": name, "provider": "Azure Speech", "voice": AZURE_VOICE, "rate": AZURE_RATE,
                       "date": datetime.date.today().isoformat()}
        save_manifest(manifest)
        print(f"  ✓ {t} → {name}")
    return 0


# ---------------------------------------------------------------- compilación

CSS = """
.card { font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif; font-size: 20px;
        text-align: center; color: #1c1c1c; background: #fdfcf8; }
.nightMode.card, .night_mode .card { color: #eee; background: #1e1e1e; }
.task { font-size: 16px; opacity: .75; margin-bottom: 14px; }
.hanzi { font-size: 48px; line-height: 1.3; }
.pinyin { font-size: 24px; margin-top: 4px; }
.meaning { font-size: 20px; margin-top: 10px; }
.box { margin-top: 18px; font-size: 16px; text-align: left; max-width: 34em;
       margin-left: auto; margin-right: auto; }
.box h4 { margin: 12px 0 4px; font-size: 13px; letter-spacing: .06em; text-transform: uppercase; opacity: .6; }
.sent { display: inline-flex; gap: 4px; align-items: flex-end; flex-wrap: wrap; justify-content: center; }
.seg { display: inline-flex; flex-direction: column; align-items: center; padding: 0 2px;
       border-bottom: 3px solid var(--c, transparent); }
.seg .py { font-size: 15px; }
.seg .hz { font-size: 30px; }
.gap { min-width: 1.6em; border-bottom: 3px dashed #999; }
.c0 { --c: #4e79a7; } .c1 { --c: #f28e2b; } .c2 { --c: #59a14f; } .c3 { --c: #b07aa1; } .c4 { --c: #9c755f; }
"""
# Los colores solo alinean segmentos hanzi↔pinyin; los tonos se leen por sus marcas.

FIELDS = ["ExerciseID", "Task", "Front", "PromptAudio", "Answer", "Back", "AnswerAudio", "Notes"]

FRONT_TYPED = '<div class="task">{{Task}}</div>{{Front}}{{PromptAudio}}<br>{{type:Answer}}'
FRONT_SELF = '<div class="task">{{Task}}</div>{{Front}}{{PromptAudio}}'
BACK = '{{FrontSide}}<hr id="answer">{{Back}}{{AnswerAudio}}{{Notes}}'
BACK_SELF = '{{FrontSide}}<hr id="answer">{{Back}}{{AnswerAudio}}{{Notes}}'


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def render_sentence(s, gap=None, show_pinyin=True):
    parts, color = [], 0
    for seg in s["segments"]:
        if gap and seg.get("ref") == gap:
            parts.append('<span class="seg gap"><span class="py">&nbsp;</span><span class="hz">&nbsp;</span></span>')
            continue
        cls = f"seg c{color % 5}" if seg.get("pinyin") else "seg"
        color += bool(seg.get("pinyin"))
        py = esc(seg.get("pinyin", "")) if show_pinyin else "&nbsp;"
        parts.append(f'<span class="{cls}"><span class="py">{py}</span><span class="hz">{esc(seg["text"])}</span></span>')
    return '<div class="sent">' + "".join(parts) + "</div>"


def sound(text, manifest, media_files):
    item = manifest.get(text)
    if not item or not (MEDIA / item["file"]).exists():
        return ""
    media_files.add(str(MEDIA / item["file"]))
    return f"[sound:{item['file']}]"


def build_note(ex, eby, sby, manifest, media_files, models):
    import genanki
    prompt, ans, lang = ex.get("prompt") or {}, ex.get("answer") or {}, ex.get("lang", "es")
    sent = sby.get(ex.get("sentence"))
    spoken = answer_hanzi(ex, sby) if wants_audio(ex, eby) else None

    group = eby.get(ex.get("group"))
    front = ""
    if ex["type"] == "contrast" and group:
        # Orden barajado pero estable por ejercicio: la posición no delata la respuesta.
        members = sorted(group["members"], key=lambda m: hashlib.sha1((ex["id"] + m["ref"]).encode()).hexdigest())
        front = '<div class="hanzi">' + "　".join(esc(eby[m["ref"]]["hanzi"]) for m in members) + "</div>"
    elif ex["type"] == "cloze" and sent:
        front = render_sentence(sent, gap=ex.get("gap"))
    elif prompt.get("hanzi"):
        front = f'<div class="hanzi">{esc(prompt["hanzi"])}</div>'
    if prompt.get("pinyin"):
        front += f'<div class="pinyin">{esc(prompt["pinyin"])}</div>'
    prompt_audio = sound(spoken, manifest, media_files) if prompt.get("audio") else ""
    if prompt.get("audio") and not prompt_audio:
        # Solo ocurre con --allow-missing-audio: que la tarjeta no parezca rota.
        prompt_audio = '<div class="task">(audio pendiente)</div>'

    if sent:
        back = render_sentence(sent)
        meaning = sent.get("translation", {}).get(lang) if ex["type"] == "cloze" else ans.get("meaning")
    else:
        back = f'<div class="hanzi">{esc(ans.get("hanzi", ""))}</div><div class="pinyin">{esc(ans.get("pinyin", ""))}</div>'
        meaning = ans.get("meaning")
    if meaning:
        back += f'<div class="meaning">{esc(meaning)}</div>'
    # En lectura/producción el audio va tras revelar; en escucha ya sonó en el anverso.
    answer_audio = sound(spoken, manifest, media_files) if spoken and not prompt.get("audio") else ""

    notes = []
    if ex.get("explanation"):
        notes.append(f"<h4>Explicación</h4>{esc(ex['explanation'])}")
    if group:
        rows = "".join(
            f"<div>{esc(eby[m['ref']].get('hanzi'))} {esc(eby[m['ref']].get('pinyin'))} — "
            f"{esc(eby[m['ref']].get('meaning', {}).get(lang))} · {esc(m.get('cue'))}</div>"
            for m in group["members"])
        notes.append(f"<h4>{esc(group.get('title'))}</h4>{esc(group.get('explanation'))}{rows}")
    for tid in ex.get("targets", []):
        t = eby.get(tid, {})
        if standalone(t) in ("no", "rare"):
            words = "、".join(w["hanzi"] for w in free_words_containing(t, list(eby.values())))
            label = "Casi no se usa solo" if standalone(t) == "rare" else "No se usa solo"
            notes.append(f"<h4>{label}</h4>Aparece en: {esc(words)}")
    for rid in ex.get("refs", []):
        p = eby.get(rid, {})
        if p.get("kind") == "pronunciation":
            notes.append(f"<h4>{esc(p.get('title'))}</h4>{esc(p.get('explanation'))} "
                         f"{sound(p.get('audio_text'), manifest, media_files)}")
    for sid in ex.get("reveal", []):
        s = sby.get(sid)
        if s:
            notes.append(f"<h4>Ejemplo</h4>{render_sentence(s)}<div>{esc(s['translation'].get(lang))}</div>"
                         f"{sound(sentence_text(s), manifest, media_files)}")
    # Comentarios: solo los marcados private: false (del ejercicio y de sus objetivos).
    comments = list(ex.get("comments", []))
    for tid in ex.get("targets", []):
        comments += eby.get(tid, {}).get("comments", [])
    labels = {"mnemonic": "Mnemotecnia", "teacher": "Profesora", "linguistic": "Nota", "note": "Apunte"}
    for c in comments:
        if c.get("private", True) is False:
            notes.append(f"<h4>{labels.get(c.get('kind'), 'Comentario')}</h4>{esc(c.get('text'))}")

    typed = ans.get("typed", "")
    model = models["typed"] if typed else models["self"]
    fields = [ex["id"], esc(prompt.get("text")), front, prompt_audio, esc(typed), back, answer_audio,
              f'<div class="box">{"".join(notes)}</div>' if notes else ""]
    return genanki.Note(model=model, fields=fields,
                        guid=genanki.guid_for(GUID_NAMESPACE, ex["id"]),
                        tags=[f"type::{ex['type']}"] + [f"skill::{s}" for s in ex.get("skills", [])])


def cmd_build(allow_missing_audio):
    import genanki
    entries, sentences, exercises = load()
    errors, warnings = validate(entries, sentences, exercises, require_audio=not allow_missing_audio)
    report(errors, warnings)
    if errors:
        print("Compilación detenida por errores.")
        return 1
    fields = [{"name": f} for f in FIELDS]
    models = {
        "typed": genanki.Model(MODEL_TYPED_ID, "Chino práctico (tecleada)", fields=fields, css=CSS,
                               templates=[{"name": "Tarjeta", "qfmt": FRONT_TYPED, "afmt": BACK}]),
        "self": genanki.Model(MODEL_SELF_ID, "Chino práctico (autoevaluación)", fields=fields, css=CSS,
                              templates=[{"name": "Tarjeta", "qfmt": FRONT_SELF, "afmt": BACK_SELF}]),
    }
    # Anki deja cada tarjeta en el deck donde se importó por primera vez: el mes no se reasigna.
    decks = {}
    manifest, media_files = load_manifest(), set()
    eby = {e["id"]: e for e in entries}
    sby = {s["id"]: s for s in sentences}
    for ex in exercises:
        month = str(ex["added"])[:7]
        if month not in decks:
            decks[month] = genanki.Deck(DECK_ID_BASE + int(month.replace("-", "")), f"{DECK_NAME}::{month}")
        decks[month].add_note(build_note(ex, eby, sby, manifest, media_files, models))
    OUTPUT.mkdir(exist_ok=True)
    pkg = genanki.Package(list(decks.values()))
    pkg.media_files = sorted(media_files)
    pkg.write_to_file(APKG)
    print(f"\n{len(exercises)} tarjetas, {len(media_files)} audios → {APKG}")
    if allow_missing_audio:
        print("Compilado sin exigir audio: solo para probar importación y visualización.")
    return 0


# ---------------------------------------------------------------- Anki desktop

def anki_request(action, timeout=120, **params):
    body = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    with urllib.request.urlopen(urllib.request.Request(ANKI_CONNECT, data=body), timeout=timeout) as r:
        out = json.load(r)
    if out.get("error"):
        raise RuntimeError(out["error"])
    return out["result"]


def anki_ready():
    try:
        anki_request("version", timeout=3)
        return True
    except OSError:
        return False


def anki_running():
    if os.name != "nt":
        return False
    import subprocess
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq anki.exe", "/NH"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    return "anki.exe" in out.lower()


def find_anki():
    candidates = [os.environ.get("ANKI_EXE"),
                  os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Anki", "anki.exe"),
                  os.path.join(os.environ.get("ProgramFiles", ""), "Anki", "anki.exe")]
    return next((c for c in candidates if c and os.path.exists(c)), None)


def cmd_push(allow_missing_audio, sync):
    import subprocess
    import time
    if cmd_build(allow_missing_audio):
        return 1
    if not anki_ready():
        if not anki_running():
            exe = find_anki()
            if not exe:
                print("No encuentro Anki desktop. Instalarlo o indicar su ruta en ANKI_EXE.")
                return 1
            print("Abriendo Anki…")
            subprocess.Popen([exe], close_fds=True)
        print("Esperando a AnkiConnect…")
        deadline = time.time() + 90
        while not anki_ready():
            if time.time() > deadline:
                print("AnkiConnect no responde. Comprobar que el complemento 2055492159 está instalado, "
                      "que Anki se reinició después de instalarlo y que hay un perfil abierto.")
                return 1
            time.sleep(1)
    anki_request("importPackage", path=str(APKG.resolve()))
    anki_request("guiDeckBrowser")
    print(f"Importado en Anki: {APKG.name}")
    if not sync:
        return 0
    try:
        anki_request("sync")
        print("Sincronizado con AnkiWeb.")
    except RuntimeError as e:
        if "auth" in str(e):
            print("Sin sincronizar: inicia sesión en AnkiWeb una vez desde Anki (botón Sincronizar).")
        else:
            print(f"Sin sincronizar: {e}")
        return 1
    return 0


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lookup").add_argument("query")
    sub.add_parser("gaps")
    c = sub.add_parser("check")
    c.add_argument("--allow-missing-audio", action="store_true")
    a = sub.add_parser("audio")
    a.add_argument("--dry-run", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("--allow-missing-audio", action="store_true")
    u = sub.add_parser("push")
    u.add_argument("--allow-missing-audio", action="store_true")
    u.add_argument("--no-sync", action="store_true")
    args = p.parse_args()
    if args.cmd == "lookup":
        return cmd_lookup(args.query) or 0
    if args.cmd == "gaps":
        return cmd_gaps() or 0
    if args.cmd == "check":
        return cmd_check(not args.allow_missing_audio)
    if args.cmd == "audio":
        return cmd_audio(args.dry_run)
    if args.cmd == "push":
        return cmd_push(args.allow_missing_audio, not args.no_sync)
    return cmd_build(args.allow_missing_audio)


if __name__ == "__main__":
    sys.exit(main())
