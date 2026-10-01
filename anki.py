"""Consulta, validación, cobertura, audio y compilación del mazo de chino.

Uso:
    python anki.py lookup <hanzi|pinyin|significado>
    python anki.py plan [--doc <lote>]     tarjetas exigidas que faltan; --doc escribe 1-inbox/review-<lote>.md
    python anki.py gaps                    reparto del mazo y pendientes
    python anki.py check
    python anki.py notebook                regenera 4-notebook/ desde 3-data/
    python anki.py attic [<lote>]          el desván: lo que espera y lo que despiertan las entradas del lote
    python anki.py scaffold [--write]      tarjetas estándar para lo que falta (sin --write, solo las lista)
    python anki.py export                  5-output/dictionary.json: diccionario público versionado
    python anki.py close-batch <lote> [--dry-run]  archiva review leído y apuntes; cuaderno; commit y etiqueta
    python anki.py audio [--dry-run]
    python anki.py build [--allow-missing-audio]
    python anki.py push [--allow-missing-audio] [--no-sync] [--prune] [--reset]

No llama a ningún LLM. `audio` usa la red (Azure Speech) y nunca repite audios
ya guardados en 3-data/audio/. `push` compila, importa en Anki desktop (abriéndolo si
hace falta) mediante el complemento AnkiConnect, ajusta plantillas, límites y orden de
nuevas, y sincroniza con AnkiWeb.
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
from dragonmapper.transcriptions import pinyin_to_ipa

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "3-data"                    # fuente de verdad, mantenida por el agente
THEMES = DATA / "themes.yaml"             # temas en orden de aprendizaje
KINDS = {"lexicon": "entries", "sentences": "sentences", "exercises": "exercises"}  # carpeta → clave; un archivo por tema
MEDIA = DATA / "audio"                  # MP3 generados; no regenerar
AUDIO_MANIFEST = MEDIA / "index.yaml"
INBOX = ROOT / "1-inbox"                  # apuntes en bruto de YAGO
HISTORY = INBOX / "history"                # lo que pasó por el inbox, archivado tal cual por lote
CLASS_AUDIO = ROOT / "private" / "class-audio"  # grabaciones de clase y su transcripción: solo local
RECORDING_EXTS = {".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".opus", ".aac", ".flac", ".webm", ".mkv", ".mov"}
DIGESTS = ROOT / "2-digests"              # histórico de cada lote
NOTEBOOK = ROOT / "4-notebook"            # cuaderno de consulta por temas, generado
OUTPUT = ROOT / "5-output"                # lo que sale: mazo y futuras exportaciones
APKG = OUTPUT / "chino-practico.apkg"
ANKI_CONNECT = "http://127.0.0.1:8765"

# Identidades estables: no cambiarlas nunca, o Anki verá un mazo/modelo nuevo.
GUID_NAMESPACE = "apkg-chinese-structs"
DECK_NAME = "🐉 Chino práctico"          # subdecks por nivel y tema: "🐉 Chino práctico::HSK 1::02 Saludos y despedidas"
DECK_ID_BASE = 1_758_800_000_000         # ID del subdeck = base + hash estable del id del tema
MODEL_TYPED_ID = 1_758_800_101
MODEL_SELF_ID = 1_758_800_102
AUDIO_PREFIX = "acs_"
MODEL_TYPED_NAME = "Chino práctico (tecleada)"
MODEL_SELF_NAME = "Chino práctico (autoevaluación)"
DECK_PRESET = "🐉 Chino práctico"          # preset propio: nunca tocar el de otros mazos
NEW_PER_DAY, REVIEWS_PER_DAY = 20, 300
THEME_MAX, THEME_MIN = 60, 3               # entradas por tema: por encima, ¿dividir?; por debajo, ¿juntar?
EXAMPLES_MAX = 2                           # frases de ejemplo al dar la vuelta a una tarjeta de palabra
PRUNE_MAX = 10                             # más huérfanas que esto: `push --prune` se niega sin --force

AZURE_VOICE = os.environ.get("AZURE_SPEECH_VOICE", "zh-CN-YunyangNeural")
# Más despacio que lo normal: más claro para aprender tonos. Las palabras sueltas, aún más.
AZURE_RATE = "-30%"
AZURE_RATE_WORD = "-40%"
AZURE_LEAD_MS = 200        # silencio inicial: algunos reproductores cortan el primer instante
AZURE_FORMAT = "audio-24khz-96kbitrate-mono-mp3"
AZURE_TIER = "S0"          # nivel de pago desde 2026-09-27: el audio generado puede distribuirse

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


def load_themes():
    return load_yaml(THEMES).get("themes", [])


def load():
    """Entradas, frases y ejercicios de todos los temas, en el orden de themes.yaml. El tema de cada
    elemento es el archivo en que vive (3-data/<carpeta>/<tema>.yaml): se añade en memoria como `theme`."""
    out = {key: [] for key in KINDS.values()}
    for th in load_themes():
        for folder, key in KINDS.items():
            path = DATA / folder / f"{th['id']}.yaml"
            if path.exists():
                for item in load_yaml(path).get(key, []):
                    item["theme"] = th["id"]
                    out[key].append(item)
    return out["entries"], out["sentences"], out["exercises"]


def baseline_exercises():
    """Ejercicios en la última etiqueta lote-NNN (el estado tras el último lote), o None si no hay git o etiqueta.
    Sirve para detectar IDs desaparecidos y preguntas cambiadas con el mismo ID."""
    import subprocess
    def git(*args):
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        return r.stdout if r.returncode == 0 else None
    tags = (git("tag", "--list", "lote-*", "--sort=-v:refname") or "").split()
    if not tags:
        return None
    # Las etiquetas anteriores a la renumeración (lote-001) guardan los datos en 4-data/.
    files = []
    for folder in (f"{DATA.name}/exercises", "4-data/exercises"):
        files = (git("ls-tree", "-r", "--name-only", tags[0], folder) or "").split()
        if files:
            break
    out = {}
    for f in files:
        text = git("show", f"{tags[0]}:{f}")
        for ex in (yaml.safe_load(text or "") or {}).get("exercises", []):
            out[ex["id"]] = ex
    return tags[0], out


def stray_data_files():
    """Archivos de datos cuyo nombre no es ningún tema: su contenido no se cargaría."""
    ids = {t["id"] for t in load_themes()}
    return [f.relative_to(ROOT).as_posix() for folder in KINDS for f in (DATA / folder).glob("*.yaml")
            if f.stem not in ids]


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


def syllable_tones(hanzi, reading):
    """[(sílaba, tono)] alineando el pinyin escrito con las sílabas de pypinyin; tono 5 = neutro.
    Un 儿 fundido con la sílaba anterior (哪儿 nǎr) se devuelve como ('r', 'erhua'). None si no alinea."""
    from pypinyin import Style, lazy_pinyin
    chars = "".join(c for c in hanzi or "" if "一" <= c <= "鿿")
    if not chars or not reading:
        return None
    marked, out, pos = compact(reading), [], 0
    for hz, bare in zip(chars, lazy_pinyin(chars, style=Style.NORMAL, v_to_u=True)):
        seg = marked[pos:pos + len(bare)]
        if strip_tones(seg) == bare:
            tone = next((UNMARK[c][1] for c in seg if c in UNMARK), 5)
            out.append((bare, tone))
            pos += len(bare)
        elif hz == "儿" and marked[pos:pos + 1] == "r":
            out.append(("r", "erhua"))
            pos += 1
        else:
            return None
    return out if pos == len(marked) else None


def tone_traps(hanzi, reading):
    """Motivos por los que la pronunciación real se aparta del tono de cita: neutro, 3+3, 不/一."""
    syl = syllable_tones(hanzi, reading)
    if not syl or len(syl) < 2:
        return set()
    chars = [c for c in hanzi if "一" <= c <= "鿿"]
    tones = [t for _, t in syl]
    traps = set()
    if any(t == 5 for t in tones[1:]):
        traps.add("neutro")
    if any(a == 3 and b == 3 for a, b in zip(tones, tones[1:])):
        traps.add("3+3")
    if any(c in "不一" and i + 1 < len(tones) for i, c in enumerate(chars)):
        traps.add("不/一")
    return traps          # el erhua (哪儿 nǎr) lo trata la pista de pronunciación, no la tarjeta de dígitos


def ipa(hanzi, reading):
    """Transcripción fonética (AFI) del tono de cita, calculada del pinyin. Vacía si no alinea."""
    syl = syllable_tones(hanzi, reading)
    if not syl:
        return ""
    parts = [f"{s}{t}" for s, t in syl if t != "erhua"]
    out = pinyin_to_ipa(" ".join(parts))
    if any(t == "erhua" for _, t in syl):                  # 哪儿: la ɻ va dentro de la sílaba, antes del tono
        out = re.sub(r"([˥˦˧˨˩]+)$", r"ɻ\1", out, count=1) if re.search(r"[˥˦˧˨˩]$", out) else out + "ɻ"
    return out


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


# Estructuras: plantillas de frase con huecos visibles, «{S} + 很 + {Adj}». Los huecos son estos; cada uno admite
# unas categorías (para comprobar los ejemplos) y lleva su color en las tarjetas y en la web.
SLOTS = {
    "S": ("sujeto", {"pronombre", "sustantivo", "nombre-propio"}),
    "N": ("sustantivo", {"sustantivo", "pronombre", "nombre-propio"}),
    "V": ("verbo", {"verbo"}),
    "Adj": ("adjetivo", {"adjetivo"}),
    "Num": ("número", {"numero"}),
    "Nombre": ("nombre", {"nombre-propio", "sustantivo"}),
    "Lugar": ("lugar", {"nombre-propio", "sustantivo"}),
    "Tiempo": ("tiempo", {"sustantivo"}),
    "Frase": ("frase", set()),            # una frase entera: cualquier categoría
}
SLOT_RE = re.compile(r"^\{([A-Za-z]+)\}$")


def pattern_tokens(pattern):
    """[(clase, texto)] de una plantilla: ("slot", "Adj"), ("fixed", "很") o ("punct", "？"). Las piezas van
    separadas por « + »; la puntuación final puede ir pegada a la última."""
    out = []
    for raw in (pattern or "").split(" + "):
        raw = raw.strip()
        tail = ""
        while raw and raw[-1] in "？?。！!":
            raw, tail = raw[:-1], raw[-1] + tail
        m = SLOT_RE.match(raw)
        if m:
            out.append(("slot", m.group(1)))
        elif raw:
            out.append(("fixed", raw))
        if tail:
            out.append(("punct", tail))
    return out


def render_pattern(st, eby):
    """HTML de una plantilla: las piezas fijas con su pinyin, los huecos como cajas de color con su nombre."""
    pinyin = {eby[r]["hanzi"]: eby[r].get("pinyin", "") for r in st.get("refs", []) if r in eby}
    parts = []
    for kind, text in pattern_tokens(st.get("pattern")):
        if kind == "slot":
            parts.append(f'<span class="slot slot-{esc(text)}"><span class="py">&nbsp;</span>'
                         f'<span class="hz">{esc(SLOTS.get(text, (text,))[0])}</span></span>')
        elif kind == "fixed":
            parts.append(f'<span class="seg is-fixed"><span class="py">{esc(pinyin.get(text, ""))}</span>'
                         f'<span class="hz">{esc(text)}</span></span>')
        else:
            parts.append(f'<span class="seg"><span class="py"></span><span class="hz">{esc(text)}</span></span>')
    return '<div class="sent pattern">' + '<span class="plus">+</span>'.join(parts) + "</div>"


def han_only(text):
    """Solo los hanzi de un texto (sin puntuación, pinyin ni espacios)."""
    return re.sub(r"[^一-鿿]", "", text or "")


def calque_options(ex, st, sby):
    """[(hanzi, pinyin)] de la frase buena y el calco de una estructura, en orden barajado pero estable."""
    from pypinyin import Style, pinyin
    con = st.get("contrast") or {}
    right = sby.get(con.get("right"))
    opts = []
    if right:
        opts.append((sentence_text(right), " ".join(g["pinyin"] for g in right["segments"] if g.get("pinyin"))))
    if con.get("wrong"):
        hz = con["wrong"]
        opts.append((hz, " ".join(x[0] for x in pinyin(han_only(hz), style=Style.TONE))))
    return sorted(opts, key=lambda o: hashlib.sha1((ex["id"] + o[0]).encode()).hexdigest())


def standalone(e):
    """yes | rare | no | None. YAML lee yes/no sin comillas como booleanos."""
    v = e.get("standalone")
    return {True: "yes", False: "no"}.get(v, v) if v is not None else None


def char_status(e):
    """«palabra», «ligada» o «componente»: cómo se usa un carácter (None si no es un carácter suelto)."""
    if e.get("kind") == "component":
        return "componente"
    if e.get("kind") in ("character", "word") and len(e.get("hanzi") or "") == 1:
        return "ligada" if standalone(e) in ("no", "rare") else "palabra"
    return None


STATUS_TEXT = {"palabra": "Palabra: se usa sola.", "ligada": "Ligada: solo dentro de palabras.",
               "componente": "Componente: solo como parte de otros caracteres; no es una palabra."}


def status_text(e):
    """El «Qué es» de un carácter. Un componente cuyo hanzi también es palabra suelta (口, 女, 月) lo dice, con `as_word`."""
    st = char_status(e)
    w = e.get("as_word")
    if st == "componente" and w:
        return (f"Componente aquí: como parte de otros caracteres. Suelto también es palabra: "
                f"{e.get('hanzi')} {w.get('pinyin') or e.get('pinyin')} «{w.get('es')}».")
    return STATUS_TEXT.get(st)


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


# ---------------------------------------------------------------- trampas fonéticas
#
# Letras del pinyin que un hispanohablante lee mal. Se detectan en cada sílaba y se muestran solas
# en las tarjetas de pronunciar o reconocer por el oído (escucha, voz alta, tonos), como mucho
# PHONETIC_MAX por tarjeta, de más a menos engañosa. Las pistas propias de YAGO van aparte, como
# comentario `sound`.

PHONETIC_MAX = 3
INITIAL = re.compile(r"^(zh|ch|sh|[bpmfdtnlgkhjqxrzcsyw])?(.*)$")
PHONETIC_TRAPS = [  # (clave, condición sobre (inicial, final), texto)
    ("i-muda-retro", lambda i, f: i in ("zh", "ch", "sh", "r") and f == "i",
     "{s}: la i no suena i; se alarga la consonante, con la lengua curvada [{ipa}]"),
    ("i-muda-dental", lambda i, f: i in ("z", "c", "s") and f == "i",
     "{s}: la i no suena i; es un zumbido tras la consonante [{ipa}]"),
    ("u-es-ü", lambda i, f: i in ("j", "q", "x", "y") and f.startswith("u"),
     "{s}: tras j, q, x o y la u es una ü: labios de u y lengua de i [{ipa}]"),
    ("ü", lambda i, f: "ü" in f, "{s}: ü, labios de u y lengua de i [{ipa}]"),
    ("x", lambda i, f: i == "x", "{s}: x suena casi como una sh suave, con la lengua plana y sonriendo [{ipa}]"),
    ("q", lambda i, f: i == "q", "{s}: q es una ch con soplo de aire y la lengua plana, no una k [{ipa}]"),
    ("j", lambda i, f: i == "j", "{s}: j es una ch suave con la lengua plana, no una jota [{ipa}]"),
    ("r", lambda i, f: i == "r", "{s}: r, entre la r inglesa y la y porteña; nunca vibra [{ipa}]"),
    ("zh-ch-sh", lambda i, f: i in ("zh", "ch", "sh"), "{s}: {i} con la punta de la lengua curvada hacia atrás [{ipa}]"),
    ("z-c", lambda i, f: i in ("z", "c"), "{s}: {i} suena ts{aire}, como en «pizza» [{ipa}]"),
    ("e-no-española", lambda i, f: f in ("e", "eng") and i not in ("y",),
     "{s}: esta e no es española: suena hacia atrás, casi como una o sin redondear [{ipa}]"),
    ("en", lambda i, f: f == "en", "{s}: en suena con una e muy breve, casi «ən» [{ipa}]"),
    ("ian", lambda i, f: f in ("ian", "yan") or (i == "y" and f == "an"), "{s}: -ian suena «ien», no «ian» [{ipa}]"),
    ("ui", lambda i, f: f == "ui", "{s}: -ui se lee «uei» [{ipa}]"),
    ("iu", lambda i, f: f == "iu", "{s}: -iu se lee «iou» [{ipa}]"),
    ("un", lambda i, f: f == "un" and i not in ("j", "q", "x", "y"), "{s}: -un se lee «uen» [{ipa}]"),
    ("ong", lambda i, f: f in ("ong", "iong"), "{s}: -ong suena «ung» [{ipa}]"),
    ("h", lambda i, f: i == "h", "{s}: h es una jota suave, rasposa [{ipa}]"),
    ("b-d-g", lambda i, f: i in ("b", "d", "g"), "{s}: {i} sin aire, casi una {sorda} española [{ipa}]"),
    ("p-t-k", lambda i, f: i in ("p", "t", "k"), "{s}: {i} con un soplo de aire claro [{ipa}]"),
]
SORDA = {"b": "p", "d": "t", "g": "k"}


def phonetic_notes(hanzi, reading):
    """Trampas fonéticas de una palabra o frase, sin repetir regla y en orden de importancia."""
    syl = syllable_tones(hanzi, reading)
    if not syl:
        return []
    found = {}
    for bare, tone in syl:
        if tone == "erhua":
            continue
        i, f = INITIAL.match(bare).groups()
        i = i or ""
        for n, (key, cond, text) in enumerate(PHONETIC_TRAPS):
            if key not in found and cond(i, f):
                marked = numeric_to_marked(f"{bare}{tone}")
                phon = pinyin_to_ipa(f"{bare}{tone}")
                found[key] = (n, bare, text.format(s=marked, i=i, ipa=phon, sorda=SORDA.get(i, ""),
                                                   aire=" con aire" if i == "c" else "").replace(" []", ""))
    # Primero una nota por sílaba distinta (la más engañosa de cada una); luego el resto.
    ranked, used, rest = [], set(), []
    for n, bare, t in sorted(found.values()):
        (rest if bare in used else ranked).append(t)
        used.add(bare)
    return (ranked + rest)[:PHONETIC_MAX]


# ---------------------------------------------------------------- cobertura
#
# Cada entrada y frase declara `use`: para qué la necesita YAGO. Escalera read ⊂ hear ⊂ say, o
# excepción con motivo (`use_reason`): lista explícita (`[read]`, `[hear]`…), `context` (solo dentro
# de frases, sin tarjeta propia) o `drop` (descartada). De ahí se derivan las tarjetas exigidas; lo
# que falta lo lista `plan` y `check` lo convierte en error.

USE_LADDER = {"read": {"read"}, "hear": {"read", "hear"}, "say": {"read", "hear", "say"}}
MODALITIES = {"read", "hear", "say"}
ROLES = {"content", "function"}
CARD_LABELS = {
    "read": "lectura", "listen": "escucha", "produce": "producción", "produce-sentence": "producción en frase",
    "tones": "tonos", "speak": "voz alta", "contrast": "contraste", "recognize": "reconocimiento",
    "pattern": "estructura",
}


def use_modalities(item):
    u = item.get("use")
    if isinstance(u, list):
        return set(u)
    return set(USE_LADDER.get(u, ()))


def use_label(item):
    u = item.get("use")
    return "/".join(u) if isinstance(u, list) else str(u)


def groups_by_member(entries):
    out = {}
    for g in entries:
        if g.get("kind") == "group":
            for m in g.get("members", []):
                out.setdefault(m.get("ref"), []).append(g)
    return out


def required_cards(item, groups_of):
    """Tarjetas que exige una entrada o frase según su `use`, su tipo y su rol."""
    kind, mods, req = item.get("kind"), use_modalities(item), set()
    if kind is None:                                    # frase
        if "hear" in mods:
            req.add("listen")
        if "say" in mods:
            req.add("produce")
    elif kind in ("word", "expression"):
        if "read" in mods:
            req.add("read")
        if "hear" in mods:
            req.add("listen")
        if "say" in mods:
            req.add("produce-sentence" if item.get("role") == "function" else "produce")
        if mods & {"hear", "say"} and tone_traps(item.get("hanzi"), item.get("pinyin")):
            req.add("tones")
    elif kind in ("character", "component"):
        in_contrast = any(g.get("basis") in ("visual", "homophone", "soundalike") for g in groups_of.get(item.get("id"), []))
        if mods and not in_contrast:
            req.add("recognize")
    elif kind == "structure":
        if mods & {"hear", "say"}:
            req.add("pattern")
    elif kind == "pronunciation":
        if "hear" in mods:
            req.add("listen")
        if "say" in mods:
            req.add("speak")
    if mods:
        for g in groups_of.get(item.get("id"), []):
            if g.get("basis") in ("visual", "homophone", "soundalike"):
                req.add("contrast")
    return req


def satisfied(ex):
    """Qué exigencias cubre un ejercicio para cada uno de sus objetivos."""
    t, audio = ex.get("type"), (ex.get("prompt") or {}).get("audio")
    return {
        "read": {"read", "recognize"},
        "listen": {"listen"},
        "tones": {"tones", "listen"} if audio else {"tones"},
        "produce": {"produce"},
        "derive": {"produce"},
        "cloze": {"produce", "produce-sentence"},
        "speak": {"speak"},
        "contrast": {"contrast", "recognize"},
        "components": {"recognize"},
        "nuance": {"nuance"},          # matiz o confusión concreta: nunca exigido, lo pide YAGO en el review
        "pattern": {"pattern"},        # decir una frase con una estructura
    }.get(t, set())


def coverage(entries, sentences, exercises):
    """[(elemento, exigidas, cubiertas)] para cada entrada (salvo grupos) y frase."""
    groups_of = groups_by_member(entries)
    have = {}
    for ex in exercises:
        for tid in ex.get("targets", []):
            have.setdefault(tid, set()).update(satisfied(ex))
    return [(it, required_cards(it, groups_of), have.get(it["id"], set()))
            for it in entries + sentences if it.get("kind") != "group"]


def osmosis_gaps(entries, sentences):
    """Palabras `say` o `context` que no aparecen en ninguna frase. Las expresiones no: ya son frases."""
    in_sentence = {seg.get("ref") for s in sentences for seg in s.get("segments", [])}
    return [e for e in entries if e.get("kind") == "word"
            and ("say" in use_modalities(e) or e.get("use") == "context") and e["id"] not in in_sentence]


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
        if e.get("use") or e.get("theme"):
            print(f"  use: {use_label(e)}" + (f" ({e['use_reason']})" if e.get("use_reason") else "")
                  + (f" · {e['role']}" if e.get("role") else "") + f" · tema: {e.get('theme')}")
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
    # El desván: lo que no entró, con su contexto.
    for a in load_attic():
        text = " ".join([a.get("hanzi") or "", (a.get("meaning") or {}).get("es", "")] + a.get("links", []))
        py = compact(a.get("pinyin") or "")
        if (q and q in text.lower()) or (py and (q_marked == py or q_plain == strip_tones(py))):
            print(f"\n[desván {a['id']}] {a['hanzi']}  {a.get('pinyin', '')}  {a['meaning'].get('es', '')} · "
                  f"tema: {a.get('theme')} · despierta con: {', '.join(a.get('links', []))}")
            print(f"  no entró: {a.get('reason')}")
            for n in a.get("notes", []):
                print(f"  nota: {n.get('text')}")
    # Palabras de frases aún no registradas que coinciden.
    loose = {f"{seg['text']} {seg.get('pinyin', '')}".strip() for s in sentences for seg in s["segments"]
             if not seg.get("ref") and seg.get("pinyin") and q and
             (q in seg["text"] or q_plain == compact(strip_tones(seg["pinyin"])))}
    if loose:
        print("\nEn frases, sin entrada: " + ", ".join(sorted(loose)))


PRIMARY = {"read": "lectura", "listen": "escucha", "tones": "tonos", "produce": "producción",
           "derive": "producción", "cloze": "producción", "speak": "voz alta", "contrast": "contraste",
           "components": "componentes", "nuance": "matiz", "pattern": "estructura"}
GENERATED = "<!-- Generado por `anki.py notebook` desde 3-data/. No editar: se rehace en cada lote. -->"
REVIEW_HEADER = ("<!-- REVIEW: para opinar. Debajo de cada punto hay una línea «>»: escribe lo que quieras (sí, no, "
                 "un matiz, una duda, una frase, una corrección). Lo que escribas entra en el siguiente lote; lo que "
                 "dejes vacío se queda como está. Puedes añadir puntos al final. El log completo del lote está en "
                 "2-digests/summary-{batch}.md. -->")
LOG_HEADER = ("<!-- LOG del lote: qué entró, qué no y por qué, correcciones y reorganizaciones. Histórico: no se "
              "reescribe; los cambios posteriores se añaden al final. Para opinar: el review del inbox. -->")


LEVEL_PASS = 0.8     # un nivel se da por superado con el 80 % de su vocabulario (más el juicio sobre las estructuras)


THEORY = DATA / "theory.yaml"
ATTIC = DATA / "attic.yaml"


def load_attic():
    """El desván (3-data/attic.yaml): lo que no entró (avanzado o poco conectado), con todo su contexto, esperando a
    que algo de un lote lo despierte. No genera tarjetas ni se exporta."""
    if not ATTIC.exists():
        return []
    return (yaml.safe_load(ATTIC.read_text(encoding="utf-8")) or {}).get("items", []) or []


ATTIC_NEAR = 0.6     # a partir del 60 % de un nivel, lo que espera de ese nivel en el desván se propone para cerrarlo


def attic_link_hits(link, hanzi):
    """Un enlace de un solo hanzi solo despierta con esa palabra exacta (猫 no despierta con 小猫, 进 no con 请进); uno
    de varios, también dentro de otra palabra (颜色 despierta con 颜色好看)."""
    return bool(link) and (link == hanzi if len(link) == 1 else link in hanzi)


def attic_awake(attic, new_entries, entries=None, snoozed_for=None):
    """[(elemento, motivo)]: lo del desván que despierta en un lote, por tres vías deterministas:
    1. una entrada nueva del lote es uno de sus `links` (ver attic_link_hits);
    2. una entrada nueva contiene su hanzi (日 despierta con 生日);
    3. su nivel está a punto de cerrarse: el mazo cubre ya el ATTIC_NEAR de ese nivel (lo que espera ayuda a cerrarlo).
    `snooze: <lote>` (con `snooze_reason`) lo deja dormir en ese lote: se decidió que aún no, y queda escrito."""
    levels = hsk_levels()
    near = {lv for lv, have, total in level_coverage(entries)
            if have / total >= ATTIC_NEAR} if entries is not None else set()
    out = []
    for a in attic:
        if snoozed_for and a.get("snooze") == snoozed_for:
            continue
        why = None
        for e in new_entries:
            h = e.get("hanzi") or ""
            hit = next((l for l in a.get("links", []) if h and attic_link_hits(l, h)), None)
            if hit:
                why = f"llega {h}"
                break
            if h and a.get("hanzi") and len(h) > len(a["hanzi"]) and a["hanzi"] in h:
                why = f"{h} contiene {a['hanzi']}"
                break
        lv = levels.get(a.get("hanzi")) or a.get("level")
        if not why and lv in near:
            why = f"el HSK {lv} ya pasa del {int(ATTIC_NEAR * 100)} %"
        if why:
            out.append((a, why))
    return out


def batch_attic_awake(batch):
    """Lo que despierta en un lote con sus entradas nuevas (las que llevan source.batch de ese lote)."""
    entries, _, _ = load()
    new = [e for e in entries if (e.get("source") or {}).get("batch") == batch]
    return attic_awake(load_attic(), new, entries, snoozed_for=batch)


def attic_rules(attic, entries, errors, warnings):
    """Cada elemento del desván, completo; nada que ya esté en el mazo."""
    levels = hsk_levels()
    in_deck = {e.get("hanzi") for e in entries if e.get("hanzi")}
    seen = set()
    hanzi_seen = set()
    for a in attic:
        aid = a.get("id") or f"{a.get('hanzi')}"
        if aid in seen:
            errors.append(f"attic.yaml: {aid} repetido")
        seen.add(aid)
        if a.get("hanzi") in hanzi_seen:
            errors.append(f"attic.yaml: {a.get('hanzi')} está dos veces: junta sus notas en un solo elemento")
        hanzi_seen.add(a.get("hanzi"))
        if a.get("snooze") and not a.get("snooze_reason"):
            errors.append(f"attic.yaml: {aid} con snooze sin snooze_reason")
        for c in a.get("notes", []):
            if c.get("text") and (c["text"][:1].islower() or c["text"].rstrip()[-1:] not in ".!?»)"):
                warnings.append(f"attic.yaml: {aid}: nota mal redactada (mayúscula y punto): «{c['text'][:40]}»")
        for f in ("id", "hanzi", "pinyin", "theme", "reason", "source"):
            if not a.get(f):
                errors.append(f"attic.yaml: {aid} sin {f}")
        if not (a.get("meaning") or {}).get("es"):
            errors.append(f"attic.yaml: {aid} sin meaning.es")
        if not a.get("links"):
            errors.append(f"attic.yaml: {aid} sin links (qué palabras lo despiertan)")
        if not levels.get(a.get("hanzi")) and not a.get("level"):
            errors.append(f"attic.yaml: {aid} no está en la lista del HSK: pon level y level_reason")
        if a.get("hanzi") in in_deck:
            warnings.append(f"attic.yaml: {aid} ({a.get('hanzi')}) ya está en el mazo: bórralo del desván")


def load_theory():
    """Términos de teoría (3-data/theory.yaml): se leen en el cuaderno; no generan tarjetas."""
    if not THEORY.exists():
        return []
    return (yaml.safe_load(THEORY.read_text(encoding="utf-8")) or {}).get("terms", [])


def deck_coverage(entries):
    """Por nivel (en el orden de level_coverage): palabras de la lista que están en el mazo, con cualquier `use`."""
    levels = hsk_levels()
    have = {e.get("hanzi") for e in entries if e.get("kind") in ("word", "expression") and e.get("use") != "drop"}
    return [sum(1 for w, lv in levels.items() if lv == level and w in have) for level in LEVELS]


def level_coverage(entries):
    """[(nivel, palabras de la lista que el mazo entrena para oír o decir, total del nivel)], nivel a nivel."""
    levels = hsk_levels()
    trained = {e.get("hanzi") for e in entries if e.get("kind") in ("word", "expression")
               and use_modalities(e) & {"hear", "say"}}
    totals, have = {}, {}
    for hanzi, lv in levels.items():
        totals[lv] = totals.get(lv, 0) + 1
        have[lv] = have.get(lv, 0) + (hanzi in trained)
    return [(lv, have[lv], totals[lv]) for lv in sorted(totals)]


def cmd_gaps():
    """Reparto del mazo: cada tarjeta cuenta una vez, por lo que practica."""
    from collections import Counter
    entries, sentences, exercises = load()
    manifest = load_manifest()
    by_skill = Counter(PRIMARY.get(ex.get("type"), ex.get("type")) for ex in exercises)
    print(f"{len(exercises)} tarjetas (registrado no equivale a aprendido).\n")
    for skill, n in by_skill.most_common():
        print(f"  {skill:12} {n:4}  {100 * n / len(exercises):5.1f} %")
    print()
    print("Cobertura del HSK 3.0 (palabras de la lista que el mazo entrena para oír o decir):")
    for lv, have, total in level_coverage(entries):
        print(f"  {level_label(lv):8} {have:4} de {total:4}  {100 * have / total:5.1f} %")
    uses = Counter(use_label(e) for e in entries if e.get("kind") in ("word", "expression"))
    print("\nPalabras y expresiones por use: " + ", ".join(f"{u} {n}" for u, n in uses.most_common()))
    missing = sum(len(req - have) for _, req, have in coverage(entries, sentences, exercises))
    print(f"Tarjetas exigidas que faltan: {missing}" + ("  (ver `plan`)" if missing else ""))
    osm = osmosis_gaps(entries, sentences)
    print(f"Sin frase de contexto (ósmosis): {len(osm)}" + (f" → {', '.join(e['hanzi'] for e in osm)}" if osm else ""))
    pending = sorted(t for t in required_audio(entries, sentences, exercises) if t not in manifest)
    print(f"Audio pendiente: {len(pending)}" + (f" → {', '.join(pending)}" if pending else ""))
    loose = sorted({seg["text"] for s in sentences for seg in s["segments"]
                    if not seg.get("ref") and seg.get("pinyin")})
    if loose:
        print("Palabras en frases sin entrada: " + ", ".join(loose))
    # Cualquier archivo cuenta como apunte pendiente, con o sin extensión; salvo el README y lo que deja el agente.
    raw = sorted(f.name for f in INBOX.iterdir() if f.is_file() and f.name != "README.md"
                 and not f.name.startswith(("summary-", "review-"))) if INBOX.exists() else []
    print(f"Inbox sin procesar: {len(raw)}" + (f" → {', '.join(raw)}" if raw else ""))
    attic, lv = load_attic(), hsk_levels()
    if attic:
        from collections import Counter
        by = Counter(lv.get(x.get("hanzi")) or x.get("level") for x in attic)
        oldest = min(str((x.get("source") or {}).get("date", "")) for x in attic)
        print(f"Desván: {len(attic)} esperando (" + ", ".join(f"HSK {k}: {n}" for k, n in sorted(by.items()))
              + f"); lo más antiguo, del {oldest}")
    for g in sorted(INBOX.glob("review-*.md")) if INBOX.exists() else []:
        print(f"Review: {g.name} (editable; entra en el próximo lote junto con los apuntes)")



# ---------------------------------------------------------------- scaffold
#
# Tarjetas estándar para lo que `plan` dice que falta, siempre con el mismo formato. El agente revisa y
# ajusta después lo que pide criterio (consignas ambiguas, explicaciones). Lo que no es mecánico
# (pronunciación, componentes, frases que aún no existen) se lista como «a mano».

TONE_PROMPT = "Escribe el tono de cada sílaba (1–4, 5 = neutro)."


def to_numeric(hanzi, reading):
    """你好 + nǐ hǎo -> ni3 hao3; 哪儿 + nǎr -> nar3. None si no alinea."""
    syl = syllable_tones(hanzi, reading)
    if not syl:
        return None
    out = []
    for bare, tone in syl:
        if tone == "erhua":
            out[-1] = out[-1][:-1] + "r" + out[-1][-1]
        else:
            out.append(f"{bare}{tone}")
    return " ".join(out)


def cloze_sentence(iid, candidates, sby, eby, exercises):
    """La frase de una tarjeta de hueco, por regla fija: ninguna otra tarjeta de hueco la usa ya; su nivel no pasa del
    de la palabra; primero las frases para decir (say) y, entre ellas, la más corta; a igualdad, la de ID menor."""
    levels = hsk_levels()
    used = {x.get("sentence") for x in exercises if x.get("type") == "cloze"}
    mine = level_of(iid, eby, sby, levels) or 99

    def rank(sid):
        lv = level_of(sid, eby, sby, levels) or 0
        return (sid in used, lv > mine, sby[sid].get("use") != "say", len(sentence_text(sby[sid])), sid)
    return min(candidates, key=rank)


def scaffold_exercises(entries, sentences, exercises, today):
    """([(tema, ejercicio)], [(id, exigencia, motivo)]): tarjetas estándar para lo que falta, y lo que pide criterio."""
    sby = {x["id"]: x for x in sentences}
    eby_all = {e["id"]: e for e in entries}
    ids = {x["id"] for x in exercises}
    base = baseline_exercises()
    if base:
        ids |= set(base[1])
    containing = {}
    for sent in sorted(sentences, key=lambda t: t.get("use") != "say"):
        for seg in sent.get("segments", []):
            if seg.get("ref"):
                containing.setdefault(seg["ref"], []).append(sent["id"])

    def new_id(base):
        cand, n = base, 2
        while cand in ids:
            cand, n = f"{base}-{n}", n + 1
        ids.add(cand)
        return cand

    def make(base, theme, **kw):
        ex = {"id": new_id(base), "added": today, "lang": "es"}
        ex.update(kw)
        ex["comments"] = []
        return theme, ex

    def answer(it, typed=None):
        a = {"hanzi": it["hanzi"], "pinyin": it["pinyin"], "meaning": (it.get("meaning") or {}).get("es", "")}
        return ({"typed": typed} | a) if typed else a

    groups_of = groups_by_member(entries)
    made, manual = [], []
    for it, req, have in coverage(entries, sentences, exercises):
        iid, kind, theme = it["id"], it.get("kind"), it.get("theme")
        short = iid.split(".", 1)[1]
        for need in sorted(req - have):
            if kind is None:                                            # frase
                ctx = list(dict.fromkeys(g["ref"] for g in it["segments"] if g.get("ref")))
                es = it["translation"]["es"]
                if need == "listen":
                    made.append(make(f"x.listen.{short}", theme, type="listen", sentence=iid, targets=[iid], context=ctx,
                                     skills=["listening", "comprehension"],
                                     prompt={"text": "Escucha. ¿Qué significa?", "audio": True}, answer={"meaning": es}))
                elif need == "produce":
                    made.append(make(f"x.produce.{short}", theme, type="produce", sentence=iid, targets=[iid],
                                     context=ctx, skills=["production", "speaking"],
                                     prompt={"text": f"Dilo en chino, en voz alta: «{es}»"}, answer={"meaning": es}))
                continue
            if kind == "structure":
                # Frase buena frente a calco erróneo (YAGO, 2026-10-01: nada de «di una frase como quieras»).
                con = it.get("contrast") or {}
                right = sby.get(con.get("right"))
                if not right:
                    manual.append((iid, need, "falta contrast (frase buena y calco erróneo): se redacta a mano"))
                    continue
                made.append(make(f"x.calque.{short}", theme, type="pattern", targets=[iid],
                                 context=list(it.get("refs", [])), sentence=right["id"],
                                 reveal=[x for x in it.get("examples", []) if x != right["id"]][:EXAMPLES_MAX],
                                 skills=["grammar", "discrimination"],
                                 prompt={"text": f"¿Cuál se dice así en chino? «{right['translation']['es']}»"},
                                 answer={"meaning": (con.get("why") or {}).get("es", "")}))
                continue
            if kind in ("pronunciation", "character", "component") or need == "recognize":
                manual.append((iid, need, "tarjeta de pronunciación o de componentes: se redacta a mano"))
                continue
            numeric = to_numeric(it.get("hanzi"), it.get("pinyin"))
            if need in ("produce", "produce-sentence", "tones") and not numeric:
                manual.append((iid, need, "el pinyin no se alinea con los hanzi: revisar la entrada"))
                continue
            if need == "read":
                made.append(make(f"x.read.{short}", theme, type="read", targets=[iid], skills=["reading", "pinyin"],
                                 prompt={"text": "Léelo en voz alta; luego, pinyin y significado.", "hanzi": it["hanzi"]}, answer=answer(it)))
            elif need == "listen":
                if not numeric:
                    manual.append((iid, need, "el pinyin no se alinea con los hanzi: revisar la entrada"))
                    continue
                made.append(make(f"x.dictation.{short}", theme, type="listen", targets=[iid],
                                 skills=["listening", "pinyin", "tones"],
                                 prompt={"text": "Escucha y escribe el pinyin.", "audio": True},
                                 answer=answer(it, numeric)))
            elif need == "produce":
                made.append(make(f"x.produce.{short}", theme, type="produce", targets=[iid], skills=["production", "pinyin"],
                                 prompt={"text": f"¿Cómo se dice «{(it.get('meaning') or {}).get('es', '')}»? Escribe el pinyin."},
                                 answer=answer(it, numeric)))
            elif need == "produce-sentence":
                if not containing.get(iid):
                    manual.append((iid, need, "no hay ninguna frase que la contenga: pedirla en el review"))
                    continue
                sid = cloze_sentence(iid, containing[iid], sby, eby_all, exercises + [x for _, x in made])
                sent = sby[sid]
                made.append(make(f"x.cloze.{short}", theme, type="cloze", sentence=sid, gap=iid, targets=[iid],
                                 context=[r for r in dict.fromkeys(g.get("ref") for g in sent["segments"]) if r and r != iid],
                                 skills=["production", "pinyin"],
                                 prompt={"text": f"Completa en pinyin: «{sent['translation']['es']}»"},
                                 answer=answer(it, numeric)))
            elif need == "tones":
                syl = syllable_tones(it["hanzi"], it["pinyin"])
                traps = tone_traps(it["hanzi"], it["pinyin"])
                made.append(make(f"x.tones.{short}", theme, type="tones", targets=[iid], skills=["tones", "pinyin"],
                                 refs=(["p.neutral-tone"] if "neutro" in traps else [])
                                 + (["p.third-tone-sandhi"] if "3+3" in traps else []),
                                 prompt={"text": TONE_PROMPT, "hanzi": it["hanzi"],
                                         "pinyin": " ".join(b for b, t in syl if t != "erhua")},
                                 answer=answer(it, "".join(str(t) for _, t in syl if t != "erhua"))))
            elif need == "contrast":
                grp = next((g for g in groups_of.get(iid, []) if g.get("basis") in ("visual", "homophone", "soundalike")), None)
                meaning = (it.get("meaning") or {}).get("es", "")
                if grp.get("basis") == "soundalike":
                    # Se parecen al oído: se oye una y se elige cuál es; el tono o la sílaba deciden.
                    prompt, skills = {"text": "Escucha: ¿cuál de estas es?", "audio": True}, ["listening", "tones", "discrimination"]
                else:
                    prompt, skills = {"text": f"¿Cuál es {it['pinyin']}, «{meaning}»?"}, ["reading", "discrimination"]
                made.append(make(f"x.contrast.{short}", theme, type="contrast", group=grp["id"], targets=[iid],
                                 skills=skills, prompt=prompt,
                                 answer={"hanzi": it["hanzi"], "pinyin": it["pinyin"], "meaning": meaning}))
    return made, manual


class _Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def append_exercises(theme, items):
    """Añade ejercicios al final de 3-data/exercises/<tema>.yaml (lo crea si no existe)."""
    path = DATA / "exercises" / f"{theme}.yaml"
    body = yaml.dump(items, Dumper=_Dumper, allow_unicode=True, sort_keys=False, default_flow_style=None, width=120)
    block = "\n".join("  " + line if line else line for line in body.splitlines()) + "\n"
    if path.exists():
        # Una lista vacía (`exercises: []`) se abre para poder añadir debajo.
        text = re.sub(r"^exercises: \[\]\s*$", "exercises:", path.read_text(encoding="utf-8"), flags=re.M)
        path.write_text(text.rstrip("\n") + "\n" + block, encoding="utf-8")
    else:
        title = next((t["title"] for t in load_themes() if t["id"] == theme), theme)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Ejercicios · {title}. Esquema: 3-data/README.md\n\nexercises:\n{block}", encoding="utf-8")


def cmd_scaffold(write):
    entries, sentences, exercises = load()
    made, manual = scaffold_exercises(entries, sentences, exercises, datetime.date.today())
    for theme, ex in made:
        print(f"{'+' if write else '·'} {theme:12} {ex['id']:32} {ex['type']:8} {ex['targets'][0]}")
    for iid, need, why in manual:
        print(f"a mano  {iid:32} {CARD_LABELS.get(need, need)}: {why}")
    if write:
        by_theme = {}
        for theme, ex in made:
            by_theme.setdefault(theme, []).append(ex)
        for theme, items in by_theme.items():
            append_exercises(theme, items)
    print(f"\n{len(made)} tarjeta(s) {'escritas' if write else 'por escribir (repetir con --write)'}; "
          f"{len(manual)} a mano. Después: revisar consignas, `check`, `audio`.")
    return 0


def label(item):
    return item.get("hanzi") or item.get("title") or item.get("pattern") or ("".join(seg["text"] for seg in item.get("segments", [])))


def cmd_plan(doc=None):
    """Lo que falta según la especificación: tarjetas exigidas ausentes y ósmosis."""
    entries, sentences, exercises = load()
    rows = [(it, sorted(req - have)) for it, req, have in coverage(entries, sentences, exercises) if req - have]
    for it, miss in rows:
        role = f", {it['role']}" if it.get("role") else ""
        print(f"{it['id']:28} {label(it):10} ({use_label(it)}{role}): falta {', '.join(CARD_LABELS[m] for m in miss)}")
    osm = osmosis_gaps(entries, sentences)
    for e in osm:
        print(f"{e['id']:28} {e['hanzi']:10} (ósmosis): no aparece en ninguna frase")
    print(f"\n{sum(len(m) for _, m in rows)} tarjeta(s) exigida(s) que faltan; {len(osm)} entrada(s) sin frase.")
    if doc:
        write_review_doc(doc, osm)
    return 0


MAINTENANCE_EVERY = 4       # cada cuántos lotes el review recuerda el mantenimiento de Anki


def write_review_doc(batch, osm):
    """Deja en 1-inbox/ el review del lote: lo que falta (calculado) y los apartados que completa el agente.
    Cada punto lleva debajo una línea «>» para que YAGO escriba."""
    INBOX.mkdir(exist_ok=True)
    if (INBOX / f"review-{batch}.md").exists():      # el del lote anterior se archiva al cerrar este
        print(f"AVISO  ya existe review-{batch}.md: no se sobrescribe.")
        return
    lines = [REVIEW_HEADER.format(batch=batch), "", f"# Review del lote {batch}", "",
             "## Cómo vas", "",
             "<!-- lo completa el agente, igual que «Seguimiento» en el log: nivel, las clases, tu método "
             "(mirando los lotes anteriores) y avisos -->", "", "> ", "",
             "## Huecos y propuestas", "",
             "<!-- lo completa el agente: huecos temáticos, lo básico del nivel que falta, caracteres con historia, "
             "qué investigar después; cada uno con su línea «>» -->", "",
             "## Falta", "", "Palabras que quieres decir y aún no aparecen en ninguna frase. Trae una frase de clase "
             "o de tu día a día que las use, o escríbela aquí.", ""]
    for e in osm:
        lines += [f"- {e['hanzi']} {e.get('pinyin', '')} · {e.get('meaning', {}).get('es', '')}", "  > ", ""]
    if not osm:
        lines += ["- (nada)", ""]
    lines += ["## ✅ Entró, con matices para ahondar", "",
              "<!-- lo completa el agente: solo los ✅ que traen relación, mnemotecnia, registro o corrección -->", "",
              "## Pendiente: ✅ sin tarjeta todavía", "", "<!-- lo completa el agente -->", "",
              "## Del desván", "", "<!-- lo completa el agente: lo que entró en este lote desde el desván "
              "(`anki.py attic <lote>`) y por qué despertó -->", "",
              "## No entró, y por qué", "", "<!-- lo completa el agente: 🟡 y ❌, cada uno con su motivo; lo que "
              "se guarda va al desván -->",
              "", "## Por verificar", "", "<!-- lo completa el agente: transcripciones dudosas y glosas corregidas -->", ""]
    if int(batch[:3]) % MAINTENANCE_EVERY == 0:     # cada pocos lotes, el mantenimiento de Anki (docs/owner.md)
        lines += ["## Mantenimiento", "", "Toca el repaso periódico de Anki (docs/owner.md, «Mantenimiento»):", "",
                  "- En Anki desktop: Herramientas → Comprobar multimedia → Borrar no utilizados (sincroniza antes "
                  "y después). Quita los audios que ya no usa ninguna tarjeta; no toca tarjetas ni progreso.",
                  "  > ", ""]
    lines += ["## Tus notas", "", "> ", ""]
    path = INBOX / f"review-{batch}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito {path.relative_to(ROOT)}")


def cmd_attic(batch=None):
    """El desván: todo lo que espera y, con un lote, lo que sus entradas nuevas despiertan (entra en ese lote)."""
    entries, _, _ = load()
    attic, levels = load_attic(), hsk_levels()
    awake = batch_attic_awake(batch) if batch else []
    woken = {a["id"] for a, _ in awake}
    for a in sorted(attic, key=lambda a: (a.get("theme") or "", a["id"])):
        lv = levels.get(a.get("hanzi")) or a.get("level")
        flag = "DESPIERTA" if a["id"] in woken else "espera   "
        print(f"{flag} {a['id']:18} {a['hanzi']:6} {a.get('pinyin', ''):14} HSK {lv}  {a.get('theme')}: "
              f"{a['meaning'].get('es', '')}")
    for a, why in awake:
        print(f"\n→ {a['hanzi']} despierta ({why}): entra en el lote con sus notas y sale del desván.")
    print(f"\n{len(attic)} en el desván" + (f"; {len(awake)} despierta(n) con {batch}." if batch else "."))
    return 0


def mark(item, has_cards):
    u, mods = item.get("use"), use_modalities(item)
    m = "❌" if u == "drop" else "✅" if (mods & {"hear", "say"} or u == "context") else "🟡"
    return m + ("🃏" if has_cards else "")


def cmd_notebook():
    """Regenera 4-notebook/: todo lo aprendido, un archivo por tema, desde 3-data/."""
    entries, sentences, exercises = load()
    themes = load_themes()
    targeted = {t for ex in exercises for t in ex.get("targets", [])}
    eby = {e["id"]: e for e in entries}
    NOTEBOOK.mkdir(exist_ok=True)
    for old in NOTEBOOK.glob("*.md"):
        if old.read_text(encoding="utf-8").startswith("<!-- Generado por `anki.py "):
            old.unlink()
    index = [GENERATED, "", "# Cuaderno", "", "Todo lo aprendido, por temas. ✅ aprender · 🟡 reconocer · ❌ descartado · 🃏 en el mazo.", ""]
    for n, th in enumerate(themes, 1):
        name = f"{n:02d}-{th['id']}.md"
        items = [e for e in entries if e.get("theme") == th["id"]]
        sents = [s for s in sentences if s.get("theme") == th["id"]]
        out = [GENERATED, "", f"# {th['title']}", ""]
        words = [e for e in items if e.get("kind") in ("word", "expression", "character", "component")]
        if words:
            out += ["## Vocabulario", ""]
            for e in words:
                meaning = (e.get("meaning") or {}).get("es", "")
                notes = " · ".join(c["text"] for c in e.get("comments", []) if c.get("private", True) is False)
                phon = ipa(e.get("hanzi"), e.get("pinyin")) if e.get("kind") in ("word", "expression") else ""
                out.append(f"- {mark(e, e['id'] in targeted)} {e['hanzi']} {e.get('pinyin', '')}"
                           + (f" [{phon}]" if phon else "") + f" · {meaning}"
                           + (f" · _{POS_LABEL[pos_of(e)]}_" if pos_of(e) in POS_LABEL else "")
                           + (f" · {notes}" if notes else ""))
            out.append("")
        for g in (e for e in items if e.get("kind") == "group"):
            out += [f"## {g['title']}", "", g.get("explanation", ""), ""]
            out += [f"- {eby[m['ref']]['hanzi']} {eby[m['ref']].get('pinyin', '')} · {m.get('cue', '')}"
                    for m in g.get("members", []) if m["ref"] in eby]
            out.append("")
        structs = [e for e in items if e.get("kind") == "structure"]
        if structs:
            out += ["## Estructuras", ""]
            for st in structs:
                ex = [sentence_text(x) for x in sentences if x["id"] in st.get("examples", [])]
                out.append(f"- {mark(st, st['id'] in targeted)} `{st['pattern']}` · {(st.get('meaning') or {}).get('es', '')}"
                           + (f" · {' / '.join(ex)}" if ex else ""))
            out.append("")
        for pr in (e for e in items if e.get("kind") == "pronunciation"):
            out += [f"## {pr['title']}", "", " ".join(pr.get("explanation", "").split()), ""]
            out += [f"- {c['text']}" for c in pr.get("comments", []) if c.get("private", True) is False]
            out.append("")
        if sents:
            out += ["## Frases", ""]
            out += [f"- {mark(s, s['id'] in targeted)} {sentence_text(s)} · {sentence_pinyin(s)} · "
                    f"{s['translation'].get('es', '')}" for s in sents]
            out.append("")
        (NOTEBOOK / name).write_text("\n".join(out), encoding="utf-8")
        index.append(f"- [{th['title']}]({name}) · {len(items)} entradas, {len(sents)} frases")
    (NOTEBOOK / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Cuaderno regenerado: {len(themes)} temas en {NOTEBOOK.relative_to(ROOT)}/")
    return 0


# ---------------------------------------------------------------- validación

def answer_hanzi(ex, sby):
    if ex.get("answer", {}).get("hanzi"):
        return ex["answer"]["hanzi"]
    if ex.get("sentence") in sby:
        return sentence_text(sby[ex["sentence"]])
    return None


def wants_audio(ex, eby):
    """Si la respuesta lleva audio. El contraste visual (大/太/天) se decide mirando la
    forma: no lo necesita. El de homófonos y el de palabras que se parecen al oído sí, porque el
    sonido es lo que se contrasta."""
    if ex.get("type") in ("components", "nuance", "pattern"):
        return False
    if ex.get("type") == "contrast":
        return eby.get(ex.get("group"), {}).get("basis") in ("homophone", "soundalike")
    return True


def required_audio(entries, sentences, exercises):
    """Textos chinos que necesitan audio: respuestas, frases y pronunciación."""
    sby = {s["id"]: s for s in sentences}
    eby = {e["id"]: e for e in entries}
    texts = set()
    for ex in exercises:
        if answer_hanzi(ex, sby) and wants_audio(ex, eby):
            texts.add(answer_hanzi(ex, sby))
    for s in sentences:                   # toda frase puede salir como ejemplo en cualquier tarjeta
        texts.add(sentence_text(s))
    for e in entries:
        if e.get("audio_text"):
            texts.add(e["audio_text"])
    return texts


NOTE_MARKS = re.compile(r"→|←|>>>|<<<|\bw/|♡|\+ ?intenso")


def comment_style(c):
    """Por qué el texto visible de un comentario no está bien redactado (docs/design.md, «Comentarios»), o None.
    Las pistas de sonido (`sound`) se escriben tal cual y no se comprueban."""
    text = (c.get("text") or "").strip()
    if c.get("kind") == "sound" or not text:
        return None
    first = next((ch for ch in text if ch.isalpha()), "")
    if first and first.islower():
        return "empieza en minúscula"
    if text[-1] not in ".!?»)":
        return "no termina en punto"
    if NOTE_MARKS.search(text):
        return "lleva símbolos de apunte (flechas, w/, ♡, + intenso)"
    return None


HAN = re.compile(r"[\u3400-\u9fff]+")
PRIVATE_GUARD = ROOT / "private" / "forbidden.txt"   # solo en local: nombres de fuentes que no pueden aparecer


def private_terms():
    if not PRIVATE_GUARD.exists():
        return []
    return [t.strip() for t in PRIVATE_GUARD.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")]


def unmarked_levels(text, own_level, known_hanzi, levels):
    """Palabras de la lista del HSK (de dos caracteres o más) que una nota menciona sin estar en el mazo, de nivel
    superior al de su entrada y sin «[HSK n]» antes del final de la oración. Se corta el texto dando prioridad a las
    palabras del mazo (两个人 es 两 + 个 + 人, no 个人); basta con marcar la primera mención, o una marca al final de
    una lista. Los hanzi sueltos de una nota son piezas de un carácter: su estatus lo cubre otra regla."""
    out, marked = [], set()
    for m in HAN.finditer(text or ""):
        run, i = m.group(), 0
        while i < len(run):
            size = next((k for k in range(min(len(run) - i, 4), 0, -1) if run[i:i + k] in known_hanzi), 0)
            if size:
                i += size
                continue
            size = next((k for k in range(min(len(run) - i, 4), 1, -1) if run[i:i + k] in levels), 0)
            if not size:
                i += 1
                continue
            w, lv = run[i:i + size], levels[run[i:i + size]]
            rest = re.split(r"[。;]|\.\s", text[m.start() + i + size:], maxsplit=1)[0]
            if w not in marked and lv > (own_level or 1):
                if "[HSK" in rest:
                    marked.add(w)
                else:
                    out.append(f"{w} [HSK {lv}]")
                    marked.add(w)
            i += size
    return out


def grammar_rules(entries, sentences, eby, sby, errors, warnings):
    """Categoría gramatical de cada palabra y estructuras bien formadas, con ejemplos que las cumplen."""
    for e in entries:
        if e.get("kind") in ("word", "expression"):
            p = pos_of(e)
            if not p:
                errors.append(f"{e['id']}: sin categoría gramatical: la lista del HSK no la da; pon pos ({', '.join(POS_LABEL)})")
            elif p not in POS_LABEL:
                errors.append(f"{e['id']}: pos «{p}» no es ninguna de {', '.join(POS_LABEL)}")
            off = official_pos(e.get("hanzi")) if e.get("kind") == "word" else None
            if e.get("pos") and off and e["pos"] != off and not e.get("pos_reason"):
                warnings.append(f"{e['id']}: pos «{e['pos']}» distinto del de la lista («{off}»): pon pos_reason")
        if e.get("kind") != "structure":
            continue
        sid = e["id"]
        toks = pattern_tokens(e.get("pattern"))
        if not toks:
            errors.append(f"{sid}: estructura sin pattern")
            continue
        for kind, text in toks:
            if kind == "slot" and text not in SLOTS:
                errors.append(f"{sid}: hueco {{{text}}} desconocido (valen {', '.join(SLOTS)})")
        fixed = [t for k, t in toks if k == "fixed"]
        refs = [r for r in e.get("refs", []) if r in eby]
        if [eby[r].get("hanzi") for r in refs] != fixed:
            errors.append(f"{sid}: refs deben ser, en orden, las entradas de las piezas fijas {fixed}")
            continue                     # sin piezas bien enlazadas no se pueden comprobar los ejemplos
        if not e.get("examples"):
            errors.append(f"{sid}: una estructura necesita al menos una frase de ejemplo (examples)")
        if not (e.get("meaning") or {}).get("es"):
            errors.append(f"{sid}: falta meaning.es (qué expresa la estructura)")
        if use_modalities(e) & {"hear", "say"}:
            con = e.get("contrast") or {}
            if con.get("right") not in sby or not con.get("wrong") or not (con.get("why") or {}).get("es"):
                errors.append(f"{sid}: falta contrast {{right: frase del mazo, wrong: calco erróneo, why: {{es, en}}}}: "
                              f"la tarjeta opone la frase buena al calco")
            elif han_only(con["wrong"]) == han_only(sentence_text(sby[con["right"]])):
                errors.append(f"{sid}: el calco erróneo es igual que la frase buena")
        for xid in e.get("examples", []):
            x = sby.get(xid)
            if not x:
                errors.append(f"{sid}: ejemplo «{xid}» no existe")
                continue
            segs = [g for g in x.get("segments", []) if g.get("ref")]
            ids = [g["ref"] for g in segs]
            # Las piezas fijas, en orden, en la frase; y a su lado, palabras de la categoría del hueco.
            pos_i, at = 0, []
            for r in refs:
                while pos_i < len(ids) and ids[pos_i] != r:
                    pos_i += 1
                if pos_i == len(ids):
                    break
                at.append(pos_i)
                pos_i += 1
            if len(at) != len(refs):
                errors.append(f"{sid}: el ejemplo {xid} no contiene {fixed} en ese orden")
                continue
            ti = [i for i, (k, _) in enumerate(toks) if k == "fixed"]
            for n, i in enumerate(ti):
                for side, j in ((-1, i - 1), (1, i + 1)):
                    if 0 <= j < len(toks) and toks[j][0] == "slot" and toks[j][1] in SLOTS:
                        k = at[n] + side
                        if 0 <= k < len(segs):
                            got = pos_of(eby.get(segs[k]["ref"], {}))
                            if got and SLOTS[toks[j][1]][1] and got not in SLOTS[toks[j][1]][1]:
                                warnings.append(f"{sid}: en {xid}, «{segs[k]['text']}» ({POS_LABEL.get(got, got)}) ocupa el hueco "
                                                f"{{{toks[j][1]}}}; ¿ejemplo o plantilla equivocados?")


def is_erhua(e):
    """Una palabra con 儿 fundido con la sílaba anterior (哪儿 nǎr): forma del norte, no del estándar."""
    hz, py = e.get("hanzi") or "", strip_tones(e.get("pinyin") or "").lower()
    return len(hz) > 1 and hz.endswith("儿") and py.endswith("r") and not py.endswith("er")


def standard_rules(entries, sentences, eby, errors, warnings):
    """Mandarín estándar y contrastes (docs/goal.md, 2026-10-01): nada de erhua ni regionalismos en el mazo,
    y aviso de palabras que suenan igual y aún no se contrastan."""
    for e in entries:
        if is_erhua(e) and e.get("use") != "drop":
            errors.append(f"{e['id']} ({e['hanzi']}): erhua, forma del norte: se descarta con use: drop y se usa la "
                          f"estándar (哪里, no 哪儿)")
    for s in sentences:
        for seg in s.get("segments", []):
            if eby.get(seg.get("ref"), {}).get("use") == "drop":
                errors.append(f"{s['id']}: usa {seg['text']}, descartada (use: drop)")
    together = set()
    for g in entries:
        if g.get("kind") == "group":
            refs = [m["ref"] for m in g.get("members", [])]
            together |= {(a, b) for a in refs for b in refs}
    sound = {}
    for e in entries:
        if e.get("kind") in ("word", "expression") and use_modalities(e) & {"hear", "say"} and e.get("pinyin"):
            sound.setdefault(compact(strip_tones(e["pinyin"])), []).append(e)
    for same in sound.values():
        for i, a in enumerate(same):
            for b in same[i + 1:]:
                if a.get("hanzi") != b.get("hanzi") and (a["id"], b["id"]) not in together:
                    warnings.append(f"{a['id']} {a['hanzi']} y {b['id']} {b['hanzi']} suenan igual (sin tonos) y no están "
                                    f"en ningún grupo: ¿contrastarlos (homophone o soundalike)?")


def quality_rules(entries, sentences, exercises, eby, sby, errors, warnings):
    """Reglas de calidad que no dependen del criterio de nadie (docs/design.md y docs/goal.md)."""
    grammar_rules(entries, sentences, eby, sby, errors, warnings)
    standard_rules(entries, sentences, eby, errors, warnings)
    levels = hsk_levels()
    known_hanzi = {e.get("hanzi") for e in entries if e.get("hanzi")}
    for e in entries:
        if e.get("kind") in ("group", "structure"):
            continue
        official = levels.get(e.get("hanzi")) if e.get("kind") != "pronunciation" else 1
        # Niveles: oficial si está en la lista; si no, estimado con su motivo.
        if not official and not e.get("level"):
            errors.append(f"{e['id']}: sin nivel. No está en la lista del HSK: pon level (1–7) y level_reason (Niveles)")
        if e.get("level") and not e.get("level_reason"):
            errors.append(f"{e['id']}: level sin level_reason")
        if official and e.get("level") and e.get("level") != official and e.get("kind") != "pronunciation":
            warnings.append(f"{e['id']}: level {e['level']} distinto del oficial HSK {official}; manda el oficial")
        lv = official or e.get("level")
        mods = use_modalities(e)
        if e.get("kind") in ("word", "expression") and not e.get("use_reason"):
            if lv == 1 and mods == {"read"}:
                warnings.append(f"{e['id']}: es HSK 1 y solo de lectura; ¿hear o say? (o use_reason)")
            if lv == 7 and "say" in mods:
                warnings.append(f"{e['id']}: es HSK 7 y para decir; necesita use_reason")
        # Estatus de cada carácter: palabra, ligada o componente.
        if e.get("kind") == "character" and e.get("standalone") is None:
            errors.append(f"{e['id']}: carácter sin standalone (yes = palabra; no o rare = ligada)")
        if e.get("kind") == "component" and mods & {"hear", "say"}:
            errors.append(f"{e['id']}: un componente no se oye ni se dice: use context o read")
        if e.get("kind") == "component" and not e.get("as_word") and (
                levels.get(e.get("hanzi")) or e.get("hanzi") in {x.get("hanzi") for x in entries if x.get("kind") == "word"}):
            errors.append(f"{e['id']}: {e.get('hanzi')} también es palabra suelta: añade as_word {{es: …}} para no decir que no lo es")
        # Notas: las palabras de otros niveles que no están en el mazo llevan su marca.
        for c in e.get("comments", []):
            miss = unmarked_levels(c.get("text"), lv, known_hanzi, levels)
            if miss:
                warnings.append(f"{e['id']}: la nota menciona {', '.join(miss)} sin marcarlo; añade la marca tras la palabra")
    # Frases completas: todo trozo en chino enlaza a una entrada.
    for x in sentences:
        for g in x.get("segments", []):
            if HAN.search(g.get("text", "")) and not g.get("ref"):
                errors.append(f"{x['id']}: «{g['text']}» no enlaza a ninguna entrada (añádela o quítala de la frase)")
    # El pinyin por delante: lo que se oye o se produce de una palabra se escribe.
    for ex in exercises:
        first = eby.get((ex.get("targets") or [None])[0]) or {}
        if first.get("kind") in ("word", "expression") and ex.get("type") in ("listen", "produce") \
                and not (ex.get("answer") or {}).get("typed"):
            errors.append(f"{ex['id']}: {ex['type']} de una palabra sin respuesta escrita (typed): se escribe lo oído o lo producido")
    # Huecos: una frase por tarjeta de hueco, de nivel no superior al de la palabra.
    seen = {}
    for ex in exercises:
        if ex.get("type") != "cloze" or not ex.get("sentence"):
            continue
        if ex["sentence"] in seen:
            warnings.append(f"{ex['id']}: usa la misma frase que {seen[ex['sentence']]}; elige otra (cloze_sentence)")
        seen.setdefault(ex["sentence"], ex["id"])
        gap = level_of(ex.get("gap"), eby, sby, levels) or 0
        if (level_of(ex["sentence"], eby, sby, levels) or 0) > gap > 0:
            warnings.append(f"{ex['id']}: la frase es de un nivel superior al de {ex.get('gap')}")
    # Teoría: cada término, con título y texto en los dos idiomas.
    seen_t = set()
    for t in load_theory():
        if t.get("id") in seen_t:
            errors.append(f"theory.yaml: {t.get('id')} repetido")
        seen_t.add(t.get("id"))
        for f in ("title", "text"):
            if not all((t.get(f) or {}).get(l) for l in ("es", "en")):
                errors.append(f"theory.yaml: {t.get('id')} sin {f} en es y en")
    # Fuentes privadas: nada versionado las nombra (lista local en private/forbidden.txt).
    terms = private_terms()
    if terms:
        paths = list(DATA.rglob("*.yaml")) + list(HISTORY.rglob("*")) + list(DIGESTS.glob("*.md"))
        for path in paths:
            if path.is_file() and path.suffix in (".yaml", ".md", ".txt"):
                text = path.read_text(encoding="utf-8", errors="ignore")
                for t in terms:
                    if t.lower() in text.lower():
                        errors.append(f"{path.relative_to(ROOT).as_posix()}: nombra una fuente privada («{t}»)")


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
            if e.get("basis") not in ("visual", "homophone", "soundalike", "pattern", "set", "phonetic"):
                errors.append(f"{e['id']}: basis debe ser visual, homophone, soundalike, pattern, set o phonetic")
            if len(members) < 2:
                errors.append(f"{e['id']}: un grupo necesita al menos 2 miembros")
            if e.get("basis") in ("visual", "homophone", "soundalike") and len(members) > 4:
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
    types = {"read", "listen", "tones", "cloze", "produce", "speak", "components", "contrast", "derive", "nuance",
             "pattern"}
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
    for t in load_themes():
        if not {"id", "title"} <= set(t) <= {"id", "title", "keep"} or not isinstance(t.get("title"), str):
            errors.append(f"themes.yaml: tema mal formado {t} (¿una coma sin comillas en el título?)")
    # Disparadores de reorganización: avisos para que el agente decida con criterio (docs/design.md).
    per_theme = {}
    for e in entries:
        if e.get("kind") != "group":
            per_theme[e["theme"]] = per_theme.get(e["theme"], 0) + 1
    for t in load_themes():
        n = per_theme.get(t["id"], 0)
        if t.get("keep"):          # decisión tomada y anotada: no se vuelve a avisar
            continue
        if n > THEME_MAX:
            warnings.append(f"tema {t['id']}: {n} entradas (más de {THEME_MAX}); ¿dividirlo? (Reorganización)")
        elif n < THEME_MIN:
            warnings.append(f"tema {t['id']}: {n} entrada(s) (menos de {THEME_MIN}); ¿juntarlo con otro? (Reorganización)")
    # Protección ante lotes disruptivos: comparar con el estado del último lote.
    base = baseline_exercises()
    if base:
        tag, old = base
        now = {x["id"]: x for x in exercises}
        gone = sorted(set(old) - set(now))
        if gone:
            warnings.append(f"{len(gone)} ejercicio(s) de {tag} ya no existen (sus tarjetas quedarían huérfanas y "
                            f"perderían el progreso con --prune): {', '.join(gone[:10])}{' …' if len(gone) > 10 else ''}")
        for xid in sorted(set(old) & set(now)):
            a, b = old[xid].get("answer") or {}, now[xid].get("answer") or {}
            if (a.get("hanzi"), a.get("typed")) != (b.get("hanzi"), b.get("typed")) or \
                    old[xid].get("type") != now[xid].get("type"):
                warnings.append(f"{xid}: cambió la respuesta o el tipo respecto a {tag}. Si ya no es la misma "
                                "pregunta, necesita ID nuevo (si no, hereda un progreso que no le corresponde).")
    theme_of = {it["id"]: it["theme"] for it in entries + sentences}
    for ex in exercises:
        first = (ex.get("targets") or [None])[0]
        if first in theme_of and ex.get("theme") and theme_of[first] != ex["theme"]:
            warnings.append(f"{ex['id']}: está en exercises/{ex['theme']}.yaml pero su objetivo {first} es del tema "
                            f"{theme_of[first]}; moverlo para que vaya al subdeck correcto")
    for f in stray_data_files():
        errors.append(f"{f}: el nombre no es ningún tema de 3-data/themes.yaml; su contenido no se carga")
    quality_rules(entries, sentences, exercises, eby, sby, errors, warnings)
    attic_rules(load_attic(), entries, errors, warnings)
    # Lo que se muestra de un comentario va redactado; el apunte literal vive en `original`.
    for it in entries + sentences + exercises:
        for c in it.get("comments", []):
            why = comment_style(c)
            if why:
                warnings.append(f"{it['id']}: comentario {why}: «{c['text'][:50]}». Redactarlo en `text` y guardar "
                                "lo escrito en `original` (Comentarios)")
    # Especificación de cobertura: use, rol, tema y tarjetas exigidas.
    theme_ids = {t["id"] for t in load_themes()}
    for it in entries + sentences:
        iid, kind, u = it["id"], it.get("kind"), it.get("use")
        if kind != "group":
            if isinstance(u, list):
                if not u or not set(u) <= MODALITIES:
                    errors.append(f"{iid}: use en lista solo admite {sorted(MODALITIES)}")
            elif u not in (*USE_LADDER, "context", "drop"):
                errors.append(f"{iid}: falta use (read | hear | say, o excepción con use_reason)")
            if (isinstance(u, list) or u in ("context", "drop")) and not it.get("use_reason"):
                errors.append(f"{iid}: use «{use_label(it)}» es una excepción y necesita use_reason")
        if kind in ("word", "expression") and it.get("role") not in ROLES:
            errors.append(f"{iid}: role debe ser content o function")
        if it.get("theme") not in theme_ids:
            errors.append(f"{iid}: theme «{it.get('theme')}» no está en themes")
    for ex in exercises:
        for tid in ex.get("targets", []):
            if ex.get("type") == "produce" and eby.get(tid, {}).get("role") == "function":
                warnings.append(f"{ex['id']}: producción suelta de {tid}, palabra gramatical: se practica en frase (cloze)")
    dropped = {it["id"] for it in entries + sentences if it.get("use") == "drop"}
    for ex in exercises:
        for tid in set(ex.get("targets", [])) & dropped:
            errors.append(f"{ex['id']}: evalúa {tid}, que está descartada (use: drop)")
    for it, req, have in coverage(entries, sentences, exercises):
        for m in sorted(req - have):
            errors.append(f"{it['id']} ({label(it)}): falta tarjeta de {CARD_LABELS[m]} (ver `plan`)")
    for e in osmosis_gaps(entries, sentences):
        warnings.append(f"{e['id']} ({e['hanzi']}): use {use_label(e)} sin ninguna frase que la contenga (ósmosis)")
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

def audio_rate(text):
    """Palabra suelta (hasta 3 hanzi, sin puntuación): más lenta. Frases: velocidad general."""
    hanzi = [c for c in text if "一" <= c <= "鿿"]
    return AZURE_RATE_WORD if len(hanzi) == len(text) and len(hanzi) <= 3 else AZURE_RATE


def audio_key(text, voice):
    raw = json.dumps([text, voice, audio_rate(text), AZURE_LEAD_MS, AZURE_FORMAT, AZURE_TIER], ensure_ascii=False, sort_keys=True)
    return AUDIO_PREFIX + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16] + ".mp3"


def azure_tts(text, voice, key, region):
    ssml = (f"<speak version='1.0' xml:lang='zh-CN'><voice name='{voice}'><break time='{AZURE_LEAD_MS}ms'/>"
            f"<prosody rate='{audio_rate(text)}'>{html.escape(text)}</prosody></voice></speak>")
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
        manifest[t] = {"file": name, "provider": "Azure Speech", "voice": AZURE_VOICE, "rate": audio_rate(t),
                       "lead_ms": AZURE_LEAD_MS, "tier": AZURE_TIER,
                       "date": datetime.date.today().isoformat()}
        save_manifest(manifest)
        print(f"  ✓ {t} → {name}")
    return 0


# ---------------------------------------------------------------- compilación

CSS = """
/* Tarjeta: papel claro o noche cálida (como el cuaderno web), una cabecera con tipo y nivel, la respuesta en su
   bloque y las notas en secciones. CSS sencillo, sin color-mix ni trucos: AnkiDroid, AnkiMobile y escritorio. */
.card { font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 20px; line-height: 1.4;
        text-align: center; color: #1f1a16; background: #faf7ef; padding: 10px 8px 28px;
        --muted: rgba(31,26,22,.55); --line: rgba(31,26,22,.13); --panel: rgba(31,26,22,.045); --lv: #b3301d; }
.nightMode.card, .night_mode .card, .card.nightMode { color: #ececec; background: #1b1b1b;
        --muted: rgba(236,236,236,.55); --line: rgba(236,236,236,.13); --panel: rgba(255,255,255,.045); }
.meta { display: flex; justify-content: space-between; align-items: center; max-width: 30em; margin: 0 auto 14px;
        padding-top: 7px; border-top: 3px solid var(--lv); font: 700 11px/1 Menlo, Consolas, monospace;
        letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.lv-1 { --lv: #b3301d; } .lv-2 { --lv: #d0632f; } .lv-3 { --lv: #df9340; } .lv-4 { --lv: #cdb35c; }
.lv-5 { --lv: #8fa972; } .lv-6 { --lv: #5f9590; } .lv-7 { --lv: #557aa3; }
.task { font-size: 17px; line-height: 1.45; max-width: 26em; margin: 0 auto 14px; color: var(--muted); }
.task .meta { font-size: 11px; }
.front { margin: 6px 0; }
.hanzi { font-size: 54px; line-height: 1.2; }
.pinyin { font-size: 24px; margin-top: 4px; }
.meaning { font-size: 20px; margin-top: 10px; }
.ipa { font-size: 15px; color: var(--muted); margin-top: 2px; }
.legend { font-size: 13px; color: var(--muted); margin-top: 10px; }
.pos { font-style: italic; }
hr#answer { border: 0; border-top: 1px solid var(--line); max-width: 30em; margin: 20px auto 16px; }
.answer { max-width: 30em; margin: 0 auto; padding: 14px 12px 16px; border-radius: 16px; background: var(--panel);
          border: 1px solid var(--line); }
.box { max-width: 30em; margin: 14px auto 0; text-align: left; font-size: 15px; line-height: 1.55; }
.note { margin-top: 10px; padding: 10px 12px 11px; border-radius: 12px; border: 1px solid var(--line); background: var(--panel); }
.note h4 { margin: 0 0 6px; font-size: 11px; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; color: var(--muted); }
.note--group .note-body > div { padding: 5px 8px; margin: 0 -8px; border-radius: 8px; }
.note--group .note-body > div + div { border-top: 1px solid var(--line); }
.note--group .is-target { font-weight: 700; background: rgba(179,48,29,.13); }
.note--example { text-align: center; }
.note--mnemonic { border-style: dashed; }
.note--mnemonic .note-body { font-style: italic; }
.note--teacher { border-left: 3px solid var(--lv); }
.example + .example { margin-top: 14px; }
.option { margin: 10px 0; }
.option .hanzi.small, .hanzi.small { font-size: 32px; }
.wrong { margin: 12px 0; color: var(--muted); }
.wrong .hz { text-decoration: line-through; font-size: 22px; }
.sent { display: inline-flex; gap: 4px; align-items: flex-end; flex-wrap: wrap; justify-content: center; }
.seg { display: inline-flex; flex-direction: column; align-items: center; padding: 0 2px;
       border-bottom: 3px solid var(--c, transparent); }
.seg .py { font-size: 15px; }
.seg .hz { font-size: 30px; }
.box .seg .hz { font-size: 24px; }
.gap { min-width: 1.6em; border-bottom: 3px dashed #999; }
.c0 { --c: #4e79a7; } .c1 { --c: #f28e2b; } .c2 { --c: #59a14f; } .c3 { --c: #b07aa1; } .c4 { --c: #9c755f; }
.acs-in { font-size: 20px; padding: 10px 14px; width: 12em; max-width: 90%; margin-top: 14px; text-align: center;
          border: 1px solid var(--line); border-radius: 12px; background: var(--panel); color: inherit; outline: none; }
#acs-result { font-size: 20px; font-weight: 700; margin-bottom: 10px; }
.acs-ok { color: #2e7d32; } .acs-bad { color: #c62828; }
.nightMode .acs-ok, .night_mode .acs-ok { color: #7cc36f; } .nightMode .acs-bad, .night_mode .acs-bad { color: #e8845a; }
.pattern { align-items: flex-end; gap: 6px; }
.pattern .plus { align-self: center; color: var(--muted); font-size: 18px; }
.slot { display: inline-flex; flex-direction: column; align-items: center; padding: 2px 8px 4px; border-radius: 8px;
        border: 2px dashed var(--s); }
.slot .hz { font-size: 16px; font-style: italic; color: var(--s); }
.slot-S { --s: #4e79a7; } .slot-N { --s: #59a14f; } .slot-V { --s: #e15759; } .slot-Adj { --s: #f28e2b; }
.slot-Num { --s: #b07aa1; } .slot-Nombre { --s: #76b7b2; } .slot-Lugar { --s: #9c755f; }
.slot-Tiempo { --s: #edc948; } .slot-Frase { --s: #8c8c8c; }
"""
# Los colores solo alinean segmentos hanzi↔pinyin; los tonos se leen por sus marcas.

FIELDS = ["ExerciseID", "Task", "Front", "PromptAudio", "Answer", "Back", "AnswerAudio", "Notes"]

# Respuesta escrita sin la comparación literal de Anki: la tarjeta guarda lo escrito (sessionStorage)
# y el reverso lo compara normalizado. Vale pinyin (tildes o dígitos, v = ü, sin importar espacios,
# mayúsculas ni puntuación) o hanzi (teclado chino). Lo esperado viaja en el campo Back como
# #acs-exp-py y #acs-exp-hz. En las tarjetas de autoevaluación la caja solo aparece si el anverso
# lleva .acs-typable (frases para decir en voz alta: escribir es opcional). Si el cliente no
# conserva sessionStorage entre anverso y reverso, la tarjeta queda como autoevaluación.
INPUT_JS_FRONT = """<script>
setTimeout(function () {
  var i = document.getElementById('acs-in'); if (!i) return;
  var allowed = i.getAttribute('data-always') === '1' || document.querySelector('.acs-typable');
  if (!allowed || document.getElementById('answer')) { i.style.display = 'none'; return; }
  var save = function () { try { sessionStorage.setItem('acs-typed', i.value); } catch (e) {} };
  try { sessionStorage.removeItem('acs-typed'); } catch (e) {}
  i.addEventListener('input', save);
  i.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { save(); try { pycmd('ans'); } catch (x) {} }
  });
  if (i.getAttribute('data-always') === '1') i.focus();
}, 0);
</script>"""

INPUT_JS_BACK = """<script>
setTimeout(function () {
  var M = {a:'āáǎà', e:'ēéěè', i:'īíǐì', o:'ōóǒò', u:'ūúǔù', 'ü':'ǖǘǚǜ'};
  var PUNCT = /[\\s'’·,.\\-，。？！、：；“”‘’「」?!:;]/g;
  function mark(s) {
    return s.replace(/([a-zü]+)([1-5]?)/g, function (_, b, t) {
      if (!t || t === '5') return b;
      var i = b.indexOf('a') >= 0 ? b.indexOf('a') : b.indexOf('e') >= 0 ? b.indexOf('e')
            : b.indexOf('ou') >= 0 ? b.indexOf('o') : -1;
      if (i < 0) for (var k = b.length - 1; k >= 0; k--) if ('iouü'.indexOf(b[k]) >= 0) { i = k; break; }
      return i < 0 ? b : b.slice(0, i) + M[b[i]][t - 1] + b.slice(i + 1);
    });
  }
  function norm(s) {
    s = (s || '').normalize('NFC').toLowerCase().replace(/u:/g, 'ü').replace(/v/g, 'ü').replace(PUNCT, '');
    return /^[1-5]+$/.test(s) ? s : mark(s);
  }
  function text(id) { var el = document.getElementById(id); return el ? el.textContent : ''; }
  var out = document.getElementById('acs-result'); if (!out) return;
  var typed = null; try { typed = sessionStorage.getItem('acs-typed'); } catch (e) {}
  if (typed === null || typed.trim() === '') return;
  var ok = /[\\u3400-\\u9fff]/.test(typed)
    ? typed.replace(PUNCT, '') === text('acs-exp-hz').replace(PUNCT, '') && text('acs-exp-hz') !== ''
    : norm(typed) === norm(text('acs-exp-py') || text('acs-expected'));
  out.className = ok ? 'acs-ok' : 'acs-bad';
  out.textContent = (ok ? '✓ ' : '✗ ') + typed;
}, 0);
</script>"""

INPUT = ('<br><input id="acs-in" class="acs-in" data-always="{always}" autocomplete="off" autocapitalize="off" '
         'autocorrect="off" spellcheck="false" placeholder="{hint}">')
FRONT_TYPED = ('<div class="task">{{Task}}</div><div class="front">{{Front}}{{PromptAudio}}</div>'
               + INPUT.format(always="1", hint="pinyin o hanzi") + INPUT_JS_FRONT)
FRONT_SELF = ('<div class="task">{{Task}}</div><div class="front">{{Front}}{{PromptAudio}}</div>'
              + INPUT.format(always="0", hint="escríbelo si quieres (pinyin o hanzi)") + INPUT_JS_FRONT)
BACK = ('{{FrontSide}}<hr id="answer"><div id="acs-result"></div>'
        '<div id="acs-expected" style="display:none">{{Answer}}</div>'
        '<div class="answer">{{Back}}{{AnswerAudio}}</div>{{Notes}}' + INPUT_JS_BACK)
BACK_SELF = ('{{FrontSide}}<hr id="answer"><div id="acs-result"></div><div class="answer">{{Back}}{{AnswerAudio}}</div>'
             '{{Notes}}' + INPUT_JS_BACK)


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


def examples_for(ex, sby, eby=None):
    """Frases de ejemplo para el reverso de una tarjeta de palabra: primero las de `reveal` (elegidas a mano) y,
    hasta EXAMPLES_MAX, las frases que contienen el objetivo (por ID de entrada, así que respetan el sentido).
    Frases modelo (say) primero; entre varias, cada tarjeta toma otras distintas según su ID, para que las
    tarjetas de una misma palabra no repitan siempre la misma. Una frase nueva enriquece sola las tarjetas
    antiguas de sus palabras."""
    chosen = [sid for sid in ex.get("reveal", []) if sid in sby]
    targets = [t for t in ex.get("targets", []) if t not in sby]      # las tarjetas de frase ya son la frase
    if not targets or ex.get("type") in ("cloze", "nuance"):
        return chosen[:EXAMPLES_MAX]
    own = ex.get("sentence")
    pool = [s["id"] for s in sby.values()
            if s["id"] != own and s["id"] not in chosen
            and any(seg.get("ref") in targets for seg in s.get("segments", []))]
    # Nivel: una frase de ejemplo nunca trae vocabulario de un nivel superior al de la tarjeta.
    if eby is not None:
        levels = hsk_levels()
        card = max([lv for lv in (level_of(t, eby, sby, levels) for t in targets) if lv] or [0])
        if card:
            pool = [sid for sid in pool if (level_of(sid, eby, sby, levels) or 0) <= card]
    say = [sid for sid in pool if sby[sid].get("use") == "say"]
    pool = say if len(say) >= EXAMPLES_MAX - len(chosen) else say + [sid for sid in pool if sid not in say]
    if pool:
        k = int(hashlib.sha1(ex["id"].encode("utf-8")).hexdigest()[:8], 16) % len(pool)
        pool = pool[k:] + pool[:k]
    out = (chosen + pool)[:EXAMPLES_MAX]
    # Lo que se confunde aparece junto (YAGO, 2026-10-01): si el objetivo tiene pareja en un grupo de contraste
    # o de serie, el último ejemplo es una frase de la pareja, si hay alguna de nivel no superior.
    if eby is not None and not chosen:
        partners = {m["ref"] for g in eby.values() if g.get("kind") == "group"
                    and g.get("basis") in ("visual", "homophone", "soundalike", "set")
                    and any(m["ref"] in targets for m in g.get("members", []))
                    for m in g["members"]} - set(targets)
        has = lambda sid: any(seg.get("ref") in partners for seg in sby[sid].get("segments", []))
        if partners and not any(has(sid) for sid in out):
            levels = hsk_levels()
            card = max([lv for lv in (level_of(t, eby, sby, levels) for t in targets) if lv] or [0])
            extra = sorted(sid for sid in sby if sid != own and has(sid)
                           and (not card or (level_of(sid, eby, sby, levels) or 0) <= card))
            if extra:
                k = int(hashlib.sha1(ex["id"].encode("utf-8")).hexdigest()[:8], 16) % len(extra)
                out = out[:EXAMPLES_MAX - 1] + [extra[k]]
    return out


def card_fields(ex, eby, sby, manifest, media_files):
    """Lo que muestra una tarjeta, campo a campo, en HTML: lo usan Anki (build_note) y la exportación pública."""
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
    elif ex["type"] == "pattern":
        st = eby.get((ex.get("targets") or [None])[0], {})
        front = "".join(f'<div class="option"><div class="hanzi small">{esc(hz)}</div><div class="pinyin">{esc(py)}</div></div>'
                        for hz, py in calque_options(ex, st, sby))
    elif prompt.get("hanzi"):
        front = f'<div class="hanzi">{esc(prompt["hanzi"])}</div>'
    if prompt.get("pinyin"):
        front += f'<div class="pinyin">{esc(prompt["pinyin"])}</div>'
    if ex["type"] == "tones":
        front += ('<div class="legend">1 ā alto y plano · 2 á sube · 3 ǎ baja (y sube) · 4 à baja fuerte · '
                  '5 a neutro, corto</div>')
    prompt_audio = sound(spoken, manifest, media_files) if prompt.get("audio") else ""
    if prompt.get("audio") and not prompt_audio:
        # Solo ocurre con --allow-missing-audio: que la tarjeta no parezca rota.
        prompt_audio = '<div class="task">(audio pendiente)</div>'

    if ex["type"] == "pattern":
        st = eby.get((ex.get("targets") or [None])[0], {})
        con = st.get("contrast") or {}
        right = sby.get(con.get("right"))
        back = ""
        if right:
            back += (f'<div class="example">✓ {render_sentence(right)}<div>{esc(right["translation"].get(lang))}</div>'
                     f'{sound(sentence_text(right), manifest, media_files)}</div>')
        if con.get("wrong"):
            back += (f'<div class="wrong">✗ <span class="hz">{esc(con["wrong"])}</span> '
                     f'{esc((con.get("why") or {}).get(lang, ""))}</div>')
        back += render_pattern(st, eby) + f'<div class="legend">{esc((st.get("meaning") or {}).get(lang, ""))}</div>'
        back += "".join(f'<div class="example">{render_sentence(sby[sid])}<div>{esc(sby[sid]["translation"].get(lang))}</div>'
                        f'{sound(sentence_text(sby[sid]), manifest, media_files)}</div>'
                        for sid in ex.get("reveal", []) if sid in sby)
        meaning = None
    elif sent:
        back = render_sentence(sent)
        meaning = sent.get("translation", {}).get(lang) if ex["type"] == "cloze" else ans.get("meaning")
    else:
        back = f'<div class="hanzi">{esc(ans.get("hanzi", ""))}</div><div class="pinyin">{esc(ans.get("pinyin", ""))}</div>'
        phon = ipa(ans.get("hanzi"), ans.get("pinyin"))
        if phon:
            back += f'<div class="ipa">[{esc(phon)}]</div>'
        meaning = ans.get("meaning")
    if meaning:
        back += f'<div class="meaning">{esc(meaning)}</div>'
    # En lectura/producción el audio va tras revelar; en escucha ya sonó en el anverso.
    answer_audio = sound(spoken, manifest, media_files) if spoken and not prompt.get("audio") else ""

    notes = []
    if ex.get("explanation"):
        notes.append(f"<h4>Explicación</h4>{esc(ex['explanation'])}")
    # Grupos: el del ejercicio y los de sus objetivos (se recuerda mejor por contraste). Si un objetivo
    # está en un conjunto (set) y en un patrón, basta el conjunto.
    shown_groups = [group] if group else []
    for tid in ex.get("targets", []):
        member_of = [g for g in eby.values() if g.get("kind") == "group"
                     and any(m.get("ref") == tid for m in g.get("members", []))]
        if any(g.get("basis") == "set" for g in member_of):
            member_of = [g for g in member_of if g.get("basis") != "pattern"]
        shown_groups += [g for g in member_of if g not in shown_groups]
    targets = set(ex.get("targets", []))
    for g in shown_groups:
        def status_tag(e):
            st = char_status(e)
            return f" <i>({st})</i>" if st in ("ligada", "componente") else ""
        rows = "".join(
            f"<div{' class=\"is-target\"' if m['ref'] in targets else ''}>{esc(eby[m['ref']].get('hanzi'))}"
            f"{status_tag(eby[m['ref']])} {esc(eby[m['ref']].get('pinyin'))} — "
            f"{esc(eby[m['ref']].get('meaning', {}).get(lang))} · {esc(m.get('cue'))}</div>"
            for m in g["members"])
        notes.append(f"<h4>{esc(g.get('title'))}</h4>{esc(g.get('explanation'))}{rows}")
    for tid in ex.get("targets", []):
        t = eby.get(tid, {})
        st = char_status(t)
        if st == "componente":
            notes.append(f"<h4>Qué es</h4>{esc(status_text(t))}")
        elif standalone(t) in ("no", "rare"):
            words = "、".join(w["hanzi"] for w in free_words_containing(t, list(eby.values())))
            label = "Casi no se usa solo" if standalone(t) == "rare" else "No se usa solo"
            notes.append(f"<h4>{label}</h4>Ligada: aparece en {esc(words)}.")
        elif st == "palabra" and t.get("kind") == "character":
            notes.append(f"<h4>Qué es</h4>{STATUS_TEXT[st]}")
    for rid in ex.get("refs", []):
        p = eby.get(rid, {})
        if p.get("kind") == "pronunciation":
            example = (f"<div>Ejemplo del fenómeno: {esc(p.get('audio_text'))} "
                       f"{sound(p.get('audio_text'), manifest, media_files)}</div>") if p.get("audio_text") else ""
            notes.append(f"<h4>{esc(p.get('title'))}</h4>{esc(p.get('explanation'))}{example}")
    # Trampas fonéticas en las tarjetas de pronunciar o reconocer por el oído.
    if ex["type"] in ("listen", "speak", "tones"):
        spoken_text = sentence_text(sent) if sent else ans.get("hanzi")
        spoken_pinyin = " ".join(seg["pinyin"] for seg in sent["segments"] if seg.get("pinyin")) if sent \
            else ans.get("pinyin")
        traps = phonetic_notes(spoken_text, spoken_pinyin) if spoken_text and spoken_pinyin else []
        if traps:
            notes.append("<h4>Pronunciación</h4>" + "".join(f"<div>{esc(t)}</div>" for t in traps))
    # La categoría de la palabra que se responde, en pequeño bajo el significado.
    first = eby.get((ex.get("targets") or [None])[0], {})
    if not sent and ex["type"] not in ("pattern", "contrast") and pos_of(first) and first.get("hanzi") == ans.get("hanzi"):
        back += f'<div class="legend pos">{esc(POS_LABEL[pos_of(first)])}</div>'
    examples = [] if ex["type"] == "pattern" else examples_for(ex, sby, eby)
    if examples:
        notes.append(f"<h4>{'Ejemplo' if len(examples) == 1 else 'Ejemplos'}</h4>" + "".join(
            f"<div class=\"example\">{render_sentence(sby[sid])}<div>{esc(sby[sid]['translation'].get(lang))}</div>"
            f"{sound(sentence_text(sby[sid]), manifest, media_files)}</div>" for sid in examples))
    # Comentarios: solo los marcados private: false (del ejercicio y de sus objetivos).
    comments = list(ex.get("comments", []))
    for tid in ex.get("targets", []):
        comments += eby.get(tid, {}).get("comments", [])
    labels = {"mnemonic": "Mnemotecnia · imagen para recordar, no su origen", "teacher": "En clase", "linguistic": "Nota", "note": "Apunte",
              "sound": "Cómo suena"}
    for c in comments:
        if c.get("private", True) is False:
            notes.append(f"<h4>{labels.get(c.get('kind'), 'Comentario')}</h4>{esc(c.get('text'))}")

    typed = ans.get("typed", "")
    # Lo esperado para comparar lo escrito: tecleadas y frases para decir (en estas, escribir es opcional).
    if typed:
        exp_py, exp_hz = typed, ans.get("hanzi", "")
    elif ex["type"] == "produce" and sent:
        exp_py, exp_hz = sentence_pinyin(sent), sentence_text(sent)
        front += '<span class="acs-typable" style="display:none"></span>'
    else:
        exp_py = exp_hz = ""
    if exp_py or exp_hz:
        back = (f'<span id="acs-exp-py" style="display:none">{esc(exp_py)}</span>'
                f'<span id="acs-exp-hz" style="display:none">{esc(exp_hz)}</span>') + back
    return {"typed": typed, "task": esc(prompt.get("text")), "front": front, "prompt_audio": prompt_audio,
            "back": back, "answer_audio": answer_audio,
            "notes": f'<div class="box">{"".join(note_section(n) for n in notes)}</div>' if notes else ""}


NOTE_KIND = (("ejemplo", "example"), ("mnemotecnia", "mnemonic"), ("en clase", "teacher"), ("cómo suena", "sound"),
             ("pronunciación", "sound"), ("qué es", "status"), ("no se usa solo", "status"),
             ("casi no se usa solo", "status"))


def note_section(html_note):
    """Una nota del reverso («<h4>título</h4>cuerpo») como sección con su clase: grupo de palabras, ejemplo,
    mnemotecnia, profesora, sonido, estatus o texto. La misma estructura sirve a Anki y a la web."""
    m = re.match(r"<h4>(.*?)</h4>(.*)", html_note, re.S)
    if not m:
        return f'<section class="note note--text"><div class="note-body">{html_note}</div></section>'
    title, body = m.groups()
    t = title.lower()
    kind = next((k for prefix, k in NOTE_KIND if t.startswith(prefix)), None)
    if not kind:
        kind = "group" if "<div" in body else "text"
    return f'<section class="note note--{kind}"><h4>{title}</h4><div class="note-body">{body}</div></section>'


TYPE_ES = {"read": "Leer", "listen": "Escuchar", "produce": "Decir", "speak": "En voz alta", "tones": "Tonos",
           "cloze": "Hueco", "contrast": "Contraste", "components": "Componentes", "derive": "Deducir",
           "nuance": "Matiz", "pattern": "Estructura"}


def card_meta(ex, eby, sby):
    """Cabecera de la tarjeta en Anki: el tipo y el nivel, con el color del nivel. La web pinta la suya."""
    lv = exercise_level(ex, eby, sby)
    kind = "Dictado" if ex["type"] == "listen" and (ex.get("answer") or {}).get("typed") else TYPE_ES.get(ex["type"], ex["type"])
    return f'<div class="meta lv-{lv}"><span>{esc(kind)}</span><span>{esc(level_label(lv))}</span></div>'


def build_note(ex, eby, sby, manifest, media_files, models):
    import genanki
    f = card_fields(ex, eby, sby, manifest, media_files)
    model = models["typed"] if f["typed"] else models["self"]
    fields = [ex["id"], card_meta(ex, eby, sby) + f["task"], f["front"], f["prompt_audio"], esc(f["typed"]), f["back"], f["answer_audio"],
              f["notes"]]
    return genanki.Note(model=model, fields=fields,
                        guid=genanki.guid_for(GUID_NAMESPACE, ex["id"]),
                        tags=[f"tema::{ex.get('theme')}", f"mes::{str(ex.get('added'))[:7]}",
                              f"nivel::{exercise_level(ex, eby, sby)}"]
                        + (["nivel::estimado"] if any(not hsk_levels().get((eby.get(t) or {}).get("hanzi"))
                                                     and (eby.get(t) or {}).get("level") for t in ex.get("targets", [])) else [])
                        + [f"use::{use_label(eby[t]) if t in eby else use_label(sby[t])}".replace("/", "+")
                           for t in ex.get("targets", [])[:1] if t in eby or t in sby]
                        + [f"type::{ex['type']}"] + [f"skill::{s}" for s in ex.get("skills", [])]
                        + [f"pos::{pos_of(eby[t])}" for t in ex.get("targets", [])[:1] if t in eby and pos_of(eby[t])])


LEVELS = range(1, 8)


def level_label(level):
    return "HSK 7-9" if level == 7 else f"HSK {level}"


def deck_name(level, theme_id, themes=None):
    """Subdeck de una tarjeta: el nivel primero y el tema dentro (🐉 Chino práctico::HSK 1::02 Saludos y despedidas)."""
    themes = themes or load_themes()
    n, t = next((n, t) for n, t in enumerate(themes, 1) if t["id"] == theme_id)
    return f"{DECK_NAME}::{level_label(level)}::{n:02d} {t['title']}"


def deck_id(level, theme_id):
    return DECK_ID_BASE + int(hashlib.sha1(f"{level}:{theme_id}".encode("utf-8")).hexdigest()[:8], 16) % 1_000_000_000


def exercise_level(ex, eby, sby, levels=None):
    """Nivel de una tarjeta: el de su objetivo más difícil (1 si ninguno lo tiene)."""
    levels = levels or hsk_levels()
    found = [lv for lv in (level_of(t, eby, sby, levels) for t in ex.get("targets", [])) if lv]
    return max(found) if found else 1


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
        "typed": genanki.Model(MODEL_TYPED_ID, MODEL_TYPED_NAME, fields=fields, css=CSS,
                               templates=[{"name": "Tarjeta", "qfmt": FRONT_TYPED, "afmt": BACK}]),
        "self": genanki.Model(MODEL_SELF_ID, MODEL_SELF_NAME, fields=fields, css=CSS,
                              templates=[{"name": "Tarjeta", "qfmt": FRONT_SELF, "afmt": BACK_SELF}]),
    }
    # Un subdeck por tema. Anki no mueve al reimportar: `push` recoloca las tarjetas que ya existían.
    decks = {}
    manifest, media_files = load_manifest(), set()
    eby = {e["id"]: e for e in entries}
    sby = {s["id"]: s for s in sentences}
    themes, levels = load_themes(), hsk_levels()
    for ex in exercises:
        key = (exercise_level(ex, eby, sby, levels), ex["theme"])
        if key not in decks:
            decks[key] = genanki.Deck(deck_id(*key), deck_name(*key, themes))
        decks[key].add_note(build_note(ex, eby, sby, manifest, media_files, models))
    OUTPUT.mkdir(exist_ok=True)
    pkg = genanki.Package(list(decks.values()))
    pkg.media_files = sorted(media_files)
    pkg.write_to_file(APKG)
    print(f"\n{len(exercises)} tarjetas, {len(media_files)} audios → {APKG}")
    if allow_missing_audio:
        print("Compilado sin exigir audio: solo para probar importación y visualización.")
    return 0


# ---------------------------------------------------------------- exportación pública
#
# Contrato con quien publique el diccionario (InfraPhysics): un JSON versionado con una lista explícita de
# campos publicables. Nunca comentarios privados, IDs de ejercicio ni detalles internos. El audio se
# referencia por ruta dentro del repositorio: con el repositorio fijado a una versión (etiqueta o commit),
# jsDelivr lo sirve en https://cdn.jsdelivr.net/gh/yago-mendoza/apkg-chinese-structs@<versión>/<ruta>.

EXPORT_PATH = OUTPUT / "dictionary.json"
EXPORT_SCHEMA = 2
HSK_LIST = ROOT / "sources" / "hsk" / "hsk3.tsv"


_HSK_CACHE = {}
_HSK_POS = {}


def hsk_levels():
    """hanzi → nivel oficial del HSK 3.0 (1–7; el 7 agrupa 7–9), desde sources/hsk/. Se lee una vez."""
    if _HSK_CACHE:
        return _HSK_CACHE
    out = _HSK_CACHE
    for line in HSK_LIST.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.split("\t")
        level, hanzi = parts[0], parts[2]
        out.setdefault(hanzi, int(level))
        if len(parts) > 4:
            _HSK_POS.setdefault(hanzi, [t for t in parts[4].split(",") if t])
    return out


def hsk_pos():
    """hanzi → etiquetas de categoría gramatical de la lista (notación de corpus: v, n, a, d, q, r…), la principal primero."""
    hsk_levels()
    return _HSK_POS


# ---------------------------------------------------------------- categoría gramatical (pos)
# Cada palabra tiene una: la primera etiqueta de la lista del HSK que tenga equivalente, salvo los interrogativos
# (la lista los da como pronombres o números) y lo que la entrada fije con `pos` (otro sentido; con `pos_reason`).
# Las expresiones son `expresion`. Solo las palabras y expresiones: un carácter ligado o un componente no son palabras.
POS_LABEL = {
    "pronombre": "pronombre", "sustantivo": "sustantivo", "nombre-propio": "nombre propio", "verbo": "verbo",
    "adjetivo": "adjetivo", "adverbio": "adverbio", "clasificador": "clasificador", "numero": "número",
    "particula": "partícula", "conjuncion": "conjunción", "preposicion": "preposición",
    "interrogativo": "interrogativo", "interjeccion": "interjección", "expresion": "expresión",
}
POS_TAGS = {
    **dict.fromkeys(["v", "vd", "vi", "vn", "vf", "vx"], "verbo"),
    **dict.fromkeys(["n", "ng", "t", "tg", "s", "f"], "sustantivo"),
    **dict.fromkeys(["nr", "ns", "nt", "nz"], "nombre-propio"),
    **dict.fromkeys(["a", "ad", "an", "ag", "b", "z"], "adjetivo"),
    **dict.fromkeys(["d", "dg"], "adverbio"),
    **dict.fromkeys(["m", "mq", "Mg"], "numero"),
    **dict.fromkeys(["q", "qv", "qt"], "clasificador"),
    **dict.fromkeys(["r", "rr", "rz", "Rg"], "pronombre"),
    "p": "preposicion", "c": "conjuncion", "cc": "conjuncion", "u": "particula", "y": "particula",
    "e": "interjeccion", "o": "interjeccion", "l": "expresion", "i": "expresion",
}
INTERROGATIVES = {"什么", "谁", "哪", "哪儿", "哪里", "几", "多少", "怎么", "怎么样", "为什么", "什么时候"}


def official_pos(hanzi):
    """La categoría que dice la lista (con la regla de los interrogativos), o None."""
    if hanzi in INTERROGATIVES:
        return "interrogativo"
    return next((POS_TAGS[t] for t in hsk_pos().get(hanzi, []) if t in POS_TAGS), None)


def pos_of(e):
    """Categoría gramatical de una palabra o expresión (None para lo demás, o si falta)."""
    if e.get("kind") not in ("word", "expression"):
        return None
    if e.get("pos"):
        return e["pos"]
    if e.get("kind") == "expression":
        return "expresion"
    return official_pos(e.get("hanzi"))


def level_of(item_id, eby, sby, levels):
    """Nivel de una entrada o frase: el oficial si está en la lista del HSK; si no, el estimado (`level`). Las reglas de
    pronunciación son de nivel 1; una frase toma el nivel más alto de sus palabras. Un carácter ligado (solo dentro de
    palabras) se aprende con la palabra más básica del mazo que lo contiene: 入 es HSK 6 como verbo suelto, pero se
    aprende en 入口 (HSK 2)."""
    if item_id in sby:
        known = [level_of(g["ref"], eby, sby, levels) for g in sby[item_id].get("segments", []) if g.get("ref")]
        known = [k for k in known if k]
        return max(known) if known else None
    e = eby.get(item_id) or {}
    if e.get("kind") == "pronunciation":
        return 1
    if e.get("kind") == "structure":
        known = [level_of(r, eby, sby, levels) for r in e.get("refs", [])]
        known = [k for k in known if k]
        return max(known) if known else e.get("level")
    own = levels.get(e.get("hanzi")) or e.get("level")
    h = e.get("hanzi") or ""
    if len(h) == 1 and standalone(e) in ("no", "rare"):
        inside = [levels.get(w.get("hanzi")) or w.get("level") for w in eby.values()
                  if w.get("kind") in ("word", "expression") and h in (w.get("hanzi") or "")]
        inside = [lv for lv in inside if lv]
        if inside:
            return min([own or 99] + inside)
    return own


def level_estimated(e, levels):
    """True si el nivel de la entrada no sale de la lista oficial (lo estimó el agente, con `level_reason`)."""
    return e.get("kind") != "pronunciation" and not levels.get(e.get("hanzi"))


def deck_history(exercises, card_level, cache=None):
    """Día a día, desde git: tarjetas añadidas (por nivel), editadas y retiradas. Devuelve (días, caché). La caché
    ({upTo, days}) resume lo ya calculado hasta un commit, y viaja en la propia exportación: la siguiente solo lee los
    commits nuevos. El estado actual, si difiere del último commit, cuenta como hoy y nunca entra en la caché (así
    `close-batch` exporta el lote que está cerrando)."""
    import copy
    import subprocess

    def git(*args):
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        return r.stdout if r.returncode == 0 else ""

    def snapshot(commit):
        found = {}
        for path in git("ls-tree", "-r", "--name-only", commit).split("\n"):
            if re.search(r"(^|/)exercises(\.yaml|/[^/]+\.yaml)$", path):
                for x in (yaml.safe_load(git("show", f"{commit}:{path}")) or {}).get("exercises", []):
                    found[x["id"]] = x
        return found

    def key(x):
        return json.dumps({k: v for k, v in x.items() if k not in ("theme", "added")}, sort_keys=True, default=str)

    def apply(days, date, prev, cur):
        d = days.setdefault(date, {"date": date, "added": {}, "edited": 0, "removed": 0})
        for i in cur.keys() - prev.keys():
            lvl = str(card_level(cur[i]) or "unlisted")
            d["added"][lvl] = d["added"].get(lvl, 0) + 1
        d["removed"] += len(prev.keys() - cur.keys())
        d["edited"] += sum(1 for i in cur.keys() & prev.keys() if key(cur[i]) != key(prev[i]))

    commits = [line.split() for line in git("log", "--reverse", "--date=short", "--format=%H %ad", "--",
                                             "*exercises*").split("\n") if line.strip()]
    hashes = [c for c, _ in commits]
    if cache and cache.get("upTo") in hashes:
        start = hashes.index(cache["upTo"]) + 1
        days = {d["date"]: copy.deepcopy(d) for d in cache.get("days", [])}
        prev = snapshot(cache["upTo"])
    else:
        start, days, prev = 0, {}, {}
    for commit, date in commits[start:]:
        cur = snapshot(commit)
        apply(days, date, prev, cur)
        prev = cur
    new_cache = {"upTo": hashes[-1] if hashes else None, "days": copy.deepcopy(sorted(days.values(), key=lambda d: d["date"]))}
    now = {x["id"]: x for x in exercises}
    if {i: key(x) for i, x in prev.items()} != {i: key(x) for i, x in now.items()}:
        apply(days, datetime.date.today().isoformat(), prev, now)
    return sorted(days.values(), key=lambda d: d["date"]), new_cache


def export_dictionary(entries, sentences, exercises, history_cache=None):
    manifest = load_manifest()

    def audio(text):
        item = manifest.get(text) if text else None
        return (MEDIA / item["file"]).relative_to(ROOT).as_posix() if item else None

    def public_notes(item):
        return [{"kind": c.get("kind"), "text": c.get("text")} for c in item.get("comments", [])
                if c.get("private", True) is False]

    groups_of = groups_by_member(entries)
    eby, sby, levels = {e["id"]: e for e in entries}, {x["id"]: x for x in sentences}, hsk_levels()
    out_entries, out_groups = [], []
    for e in entries:
        if e.get("use") == "drop":
            continue
        if e.get("kind") == "group":
            out_groups.append({"id": e["id"], "basis": e.get("basis"), "title": e.get("title"),
                               "explanation": e.get("explanation"), "theme": e.get("theme"),
                               "members": [{"ref": m["ref"], "cue": m.get("cue")} for m in e.get("members", [])]})
            continue
        row = {"id": e["id"], "kind": e.get("kind"), "theme": e.get("theme"), "use": use_label(e),
               "level": level_of(e["id"], eby, sby, levels), "levelEstimated": level_estimated(e, levels),
               "status": char_status(e), "pos": pos_of(e), "notes": public_notes(e)}
        if e.get("as_word"):
            row["asWord"] = {"es": e["as_word"].get("es"), "pinyin": e["as_word"].get("pinyin") or e.get("pinyin")}
        if e.get("kind") == "structure":
            row |= {"pattern": e.get("pattern"), "tokens": [{"kind": k, "text": t} for k, t in pattern_tokens(e.get("pattern"))],
                    "meaning": e.get("meaning") or {}, "refs": e.get("refs", []), "examples": e.get("examples", []),
                    "contrast": e.get("contrast")}
        elif e.get("kind") == "pronunciation":
            row |= {"title": e.get("title"), "explanation": " ".join((e.get("explanation") or "").split()),
                    "example": e.get("audio_text"), "audio": audio(e.get("audio_text"))}
        else:
            row |= {"hanzi": e.get("hanzi"), "pinyin": e.get("pinyin"),
                    "ipa": ipa(e.get("hanzi"), e.get("pinyin")) if e.get("kind") in ("word", "expression") else None,
                    "meaning": e.get("meaning") or {}, "role": e.get("role"), "standalone": standalone(e),
                    "audio": audio(e.get("hanzi")), "groups": [g["id"] for g in groups_of.get(e["id"], [])],
                    "relations": e.get("relations", [])}
        out_entries.append(row)
    out_sentences = [{"id": x["id"], "theme": x.get("theme"), "use": use_label(x), "text": sentence_text(x),
                      "pinyin": sentence_pinyin(x),
                      "segments": [{"text": g["text"], "ref": g.get("ref"), "pinyin": g.get("pinyin")}
                                   for g in x.get("segments", [])],
                      "translation": x.get("translation") or {}, "audio": audio(sentence_text(x))}
                     for x in sentences if x.get("use") != "drop"]
    def card_level(x):
        return level_of((x.get("targets") or [None])[0], eby, sby, levels)

    def web_html(html):
        # [sound:archivo] de Anki pasa a un botón que la web conecta con el audio; lo oculto para el corrector, fuera.
        html = re.sub(r'<span id="acs-exp-(py|hz)" style="display:none">.*?</span>', "", html)
        html = html.replace('<span class="acs-typable" style="display:none"></span>', "")
        return re.sub(r"\[sound:([^\]]+)\]", lambda m: f'<button class="zh-sound" type="button" '
                      f'data-audio="{(MEDIA / m.group(1)).relative_to(ROOT).as_posix()}" aria-label="Play"></button>',
                      html)

    history, new_cache = deck_history(exercises, card_level, history_cache)
    manifest_cards = load_manifest()
    cards = []
    for x in exercises:
        f = card_fields(x, eby, sby, manifest_cards, set())
        # Lo esperado al escribir (pinyin y hanzi), como lo compara Anki: `typed` obliga a escribir; `typable`,
        # frases para decir, lo deja opcional.
        exp = {k: html.unescape(m.group(1)) for k in ("py", "hz")
               if (m := re.search(rf'<span id="acs-exp-{k}" style="display:none">(.*?)</span>', f["back"]))}
        cards.append({"id": x["id"], "type": x["type"], "theme": x.get("theme"), "level": card_level(x),
                      "typed": bool(f["typed"]), "typable": "acs-typable" in f["front"],
                      "expected": {"pinyin": exp.get("py", ""), "hanzi": exp.get("hz", "")} if exp else None,
                      "task": f["task"],
                      "front": web_html(f["front"] + f["prompt_audio"]),
                      "back": web_html(f["back"] + f["answer_audio"]), "notes": web_html(f["notes"])})
    return {
        "schemaVersion": EXPORT_SCHEMA,
        "exportedAt": datetime.date.today().isoformat(),
        "source": "https://github.com/yago-mendoza/apkg-chinese-structs",
        "license": "CC BY 4.0",
        "attribution": "Yago Mendoza, «apkg-chinese-structs», https://github.com/yago-mendoza/apkg-chinese-structs, CC BY 4.0",
        "audio": {"provider": "Azure AI Speech", "voice": AZURE_VOICE, "synthetic": True},
        "counts": {"entries": len(out_entries), "sentences": len(out_sentences), "cards": len(exercises)},
        "themes": [{"id": t["id"], "title": t["title"], "order": n} for n, t in enumerate(load_themes(), 1)],
        "entries": out_entries, "groups": out_groups, "sentences": out_sentences,
        "cards": cards, "history": history, "historyCache": new_cache,
        "coverage": [{"level": lv, "total": total, "trained": have, "inDeck": in_deck}
                     for (lv, have, total), in_deck in zip(level_coverage(entries), deck_coverage(entries))],
        "theory": load_theory(),
        "posLabels": POS_LABEL,
        "slots": {k: v[0] for k, v in SLOTS.items()},
        # El mismo CSS que lleva el modelo de Anki: la web lo aplica a las tarjetas y no copia estilos a mano.
        "cardCss": CSS.strip(),
        "deck": {"file": APKG.relative_to(ROOT).as_posix(), "cards": len(exercises)},
    }


def cmd_export():
    if cmd_build(allow_missing_audio=False):
        return 1
    entries, sentences, exercises = load()
    errors, _ = validate(entries, sentences, exercises)
    if errors:
        print(f"`check` tiene {len(errors)} error(es): no se exporta.")
        return 1
    OUTPUT.mkdir(exist_ok=True)
    previous = {}
    if EXPORT_PATH.exists():
        try:
            previous = json.loads(EXPORT_PATH.read_text(encoding="utf-8"))
        except ValueError:
            previous = {}
    cache = previous.get("historyCache") if previous.get("schemaVersion") == EXPORT_SCHEMA else None
    data = export_dictionary(entries, sentences, exercises, cache)
    EXPORT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c = data["counts"]
    print(f"Exportado {EXPORT_PATH.relative_to(ROOT).as_posix()}: {c['entries']} entradas, {c['sentences']} frases, "
          f"{len(data['groups'])} grupos (esquema {EXPORT_SCHEMA}).")
    return 0


# ---------------------------------------------------------------- cierre de lote

BATCH_RE = re.compile(r"^(\d{3})-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
NOTE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}|mixto|sin-fecha)_")


def _git(*args, check=True):
    import subprocess
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def close_batch_plan(batch):
    """(acciones, errores) para cerrar un lote. Acción: (descripción, origen, destino)."""
    errors, actions = [], []
    m = BATCH_RE.match(batch)
    if not m:
        return [], [f"nombre de lote «{batch}»: debe ser NNN-AAAA-MM-DD-tema (tema en minúsculas y guiones)"]
    tags = _git("tag", "--list", "lote-*", check=False).split()
    expected = max((int(t[5:]) for t in tags if t[5:].isdigit()), default=0) + 1
    if f"lote-{m.group(1)}" in tags:
        errors.append(f"la etiqueta lote-{m.group(1)} ya existe: ese lote ya está cerrado")
    elif int(m.group(1)) != expected:
        errors.append(f"el siguiente lote debería ser el {expected:03d}, no el {m.group(1)}")
    err, _ = validate(*load())
    if err:
        errors.append(f"`check` tiene {len(err)} error(es): resolverlos antes de cerrar")
    for a, why in batch_attic_awake(batch):
        errors.append(f"desván: {a['hanzi']} despierta en este lote ({why}): pásalo al mazo o ponle "
                      f"snooze: {batch} con snooze_reason")
    log = DIGESTS / f"summary-{batch}.md"
    if not log.exists():
        errors.append(f"falta 2-digests/summary-{batch}.md: el log del lote (lo escribe el agente)")
    elif not log.read_text(encoding="utf-8").startswith(LOG_HEADER):
        errors.append(f"2-digests/summary-{batch}.md debe empezar con LOG_HEADER (anki.py): así se sabe qué es")
    if not (INBOX / f"review-{batch}.md").exists():
        errors.append(f"falta 1-inbox/review-{batch}.md (se empieza con `plan --doc {batch}` y lo completa el agente)")
    raw = HISTORY / batch
    for f in sorted(INBOX.iterdir()) if INBOX.exists() else []:
        if not f.is_file() or f.name == "README.md" or f.name == f"review-{batch}.md":
            continue
        if f.suffix.lower() in RECORDING_EXTS:
            # la grabación no se versiona (voz de la profesora; repositorio público): va con su transcripción
            if not (CLASS_AUDIO / f.stem / "transcript.md").exists():
                errors.append(f"1-inbox/{f.name}: grabación sin transcribir (tools/class_audio.py transcribe)")
            else:
                actions.append(("grabación → private/ (local)", f, CLASS_AUDIO / f.stem / f.name))
        elif f.name.startswith("review-"):
            actions.append(("review leído → 1-inbox/history/", f, raw / f.name))
        elif NOTE_PREFIX_RE.match(f.name):
            actions.append(("apunte → 1-inbox/history/", f, raw / f.name))
        else:
            errors.append(f"1-inbox/{f.name}: ponle delante su fecha (AAAA-MM-DD_), mixto_ o sin-fecha_ antes de cerrar")
    return actions, errors


def cmd_close_batch(batch, dry_run):
    """Cierra un lote: archiva el review leído y los apuntes, regenera el cuaderno, commit y etiqueta lote-NNN.
    El log del lote ya está en 2-digests/ (lo escribe el agente al procesar)."""
    import shutil
    actions, errors = close_batch_plan(batch)
    for desc, src, dst in actions:
        print(f"{'·' if dry_run else '→'} {desc:32} {src.relative_to(ROOT).as_posix()} → {dst.relative_to(ROOT).as_posix()}")
    for e in errors:
        print(f"ERROR  {e}")
    if errors:
        print("Lote sin cerrar: nada se ha movido.")
        return 1
    if dry_run:
        print("Simulación: repetir sin --dry-run para cerrar el lote.")
        return 0
    for _, src, dst in actions:
        dst.parent.mkdir(parents=True, exist_ok=True)
        tracked = bool(_git("ls-files", src.relative_to(ROOT).as_posix(), check=False).strip())
        if tracked:
            _git("mv", src.relative_to(ROOT).as_posix(), dst.relative_to(ROOT).as_posix())
        else:
            shutil.move(str(src), str(dst))
    cmd_notebook()
    cmd_export()
    _git("add", "-A")
    _git("commit", "-q", "-m", f"lote {batch}\n\nCo-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>")
    tag = f"lote-{batch[:3]}"
    _git("tag", "-a", tag, "-m", f"Lote {batch}: estado tras procesarlo")
    print(f"Lote cerrado: commit y etiqueta {tag}. Subir a GitHub: git push && git push origin {tag}")
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


STAGE = {"read": 0, "contrast": 1, "components": 1, "nuance": 1, "listen": 2, "tones": 3,
         "produce": 4, "derive": 4, "cloze": 4, "speak": 5, "pattern": 5}


def new_card_order(entries, sentences, exercises):
    """Posición de cada ejercicio entre las nuevas: por nivel del HSK primero (lo básico antes); dentro, por tema, y cada paso (lectura, escucha, tonos,
    producción) dos temas por detrás del anterior, para que las tarjetas de una misma entrada no
    salgan el mismo día (Anki solo separa hermanas de una misma nota)."""
    theme_idx = {t["id"]: i for i, t in enumerate(load_themes())}
    items = {it["id"]: (theme_idx.get(it.get("theme"), 99), n) for n, it in enumerate(entries + sentences)}
    eby, sby, levels = {e["id"]: e for e in entries}, {x["id"]: x for x in sentences}, hsk_levels()
    def key(ex):
        th, n = items.get((ex.get("targets") or [None])[0], (99, 0))
        stage = STAGE.get(ex.get("type"), 1)
        return (exercise_level(ex, eby, sby, levels), th + 2 * stage, th, n, stage, ex["id"])
    return {ex["id"]: pos for pos, ex in enumerate(sorted(exercises, key=key))}


def our_decks():
    return [d for d in anki_request("deckNames") if d == DECK_NAME or d.startswith(DECK_NAME + "::")]


def sync_templates():
    """El importador no siempre actualiza plantillas de un tipo de nota existente: se fuerzan."""
    for name, front, back in ((MODEL_TYPED_NAME, FRONT_TYPED, BACK), (MODEL_SELF_NAME, FRONT_SELF, BACK_SELF)):
        anki_request("updateModelTemplates", model={"name": name, "templates": {"Tarjeta": {"Front": front, "Back": back}}})
        anki_request("updateModelStyling", model={"name": name, "css": CSS})


def ensure_limits():
    """Preset propio con los límites diarios; nunca se modifica el preset que usan otros mazos."""
    decks = our_decks()
    confs = {d: anki_request("getDeckConfig", deck=d) for d in decks}
    ours = next((c["id"] for c in confs.values() if c.get("name") == DECK_PRESET), None)
    if ours is None:
        ours = anki_request("cloneDeckConfigId", name=DECK_PRESET, cloneFrom=confs[DECK_NAME]["id"])
    anki_request("setDeckConfigId", decks=decks, configId=ours)
    conf = anki_request("getDeckConfig", deck=DECK_NAME)
    if conf["new"]["perDay"] != NEW_PER_DAY or conf["rev"]["perDay"] != REVIEWS_PER_DAY:
        conf["new"]["perDay"], conf["rev"]["perDay"] = NEW_PER_DAY, REVIEWS_PER_DAY
        anki_request("saveDeckConfig", config=conf)
    return f"{NEW_PER_DAY} nuevas y {REVIEWS_PER_DAY} repasos al día (preset «{DECK_PRESET}»)"


def reorder_new(order):
    cards = anki_request("findCards", query=f'"deck:{DECK_NAME}" is:new')
    if not cards:
        return 0
    info = anki_request("cardsInfo", cards=cards)
    base = min(c["due"] for c in info)
    actions = []
    for c in info:
        pos = order.get(c["fields"].get("ExerciseID", {}).get("value"))
        if pos is not None and c["due"] != base + pos:
            actions.append({"action": "setSpecificValueOfCard",
                            "params": {"card": c["cardId"], "keys": ["due"], "newValues": [base + pos]}})
    for i in range(0, len(actions), 200):
        anki_request("multi", actions=actions[i:i + 200])
    return len(actions)


def reset_progress():
    """Fase de pruebas: todas las tarjetas del mazo vuelven a nuevas, con repasos y fallos a 0.
    Solo este mazo. El registro de repasos de Anki (estadísticas) no se borra."""
    cards = anki_request("findCards", query=f'"deck:{DECK_NAME}"')
    if not cards:
        return 0
    anki_request("forgetCards", cards=cards)
    actions = [{"action": "setSpecificValueOfCard",
                "params": {"card": c, "keys": ["reps", "lapses"], "newValues": [0, 0], "warning_check": True}}
               for c in cards]
    for i in range(0, len(actions), 200):
        anki_request("multi", actions=actions[i:i + 200])
    return len(cards)


def place_by_theme(exercises):
    """Mueve cada tarjeta al subdeck de su tema (conserva el progreso), también las de este mazo que hayan acabado
    fuera de él, y borra los subdecks propios que queden vacíos y no sean de ningún tema. Nunca toca otras notas."""
    entries, sentences, _ = load()
    eby, sby, themes, levels = {e["id"]: e for e in entries}, {x["id"]: x for x in sentences}, load_themes(), hsk_levels()
    want = {ex["id"]: deck_name(exercise_level(ex, eby, sby, levels), ex["theme"], themes) for ex in exercises}
    names = {v: v for v in want.values()}
    cards = anki_request("findCards", query=f'"deck:{DECK_NAME}"')
    # Our cards that ended up outside the deck (e.g. in the default deck) come back too; filtered decks are left alone.
    cards += anki_request("findCards", query=f'(note:"{MODEL_TYPED_NAME}" OR note:"{MODEL_SELF_NAME}") '
                                             f'-"deck:{DECK_NAME}" -deck:filtered')
    info = anki_request("cardsInfo", cards=cards) if cards else []
    moves = {}
    for c in info:
        target = want.get(c["fields"].get("ExerciseID", {}).get("value"))
        if target and c["deckName"] != target:
            moves.setdefault(target, []).append(c["cardId"])
    for deck, ids in moves.items():
        anki_request("changeDeck", cards=ids, deck=deck)
    removed = []
    for d in our_decks():
        if d == DECK_NAME or d in names.values():
            continue
        if any(x.startswith(d + "::") for x in our_decks()):
            continue
        if not anki_request("findCards", query=f'"deck:{d}"'):      # vacío: comprobado justo antes
            anki_request("deleteDecks", decks=[d], cardsToo=True)
            removed.append(d)
    return sum(len(v) for v in moves.values()), removed


def orphans(exercises, prune, force=False):
    notes = anki_request("findNotes", query=f'"deck:{DECK_NAME}"')
    info = anki_request("notesInfo", notes=notes) if notes else []
    ids = {ex["id"] for ex in exercises}
    lost = [n for n in info if n["modelName"] in (MODEL_TYPED_NAME, MODEL_SELF_NAME)
            and n["fields"]["ExerciseID"]["value"] not in ids]
    for n in lost:
        print(f"  huérfana: {n['fields']['ExerciseID']['value']}")
    if lost and prune and len(lost) > PRUNE_MAX and not force:
        print(f"{len(lost)} huérfanas son muchas (más de {PRUNE_MAX}): no borro nada. Si es intencionado, repetir con "
              "--prune --force. Si no, algo ha cambiado IDs: revisar `check` antes.")
    elif lost and prune:
        anki_request("deleteNotes", notes=[n["noteId"] for n in lost])
        print(f"Borradas {len(lost)} nota(s) huérfana(s).")
    elif lost:
        print(f"{len(lost)} nota(s) del mazo ya no existen en 3-data/. Revisar y repetir con --prune para borrarlas.")


def cmd_push(allow_missing_audio, sync, prune=False, reset=False, force=False):
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
    print(f"Importado en Anki: {APKG.name}")
    entries, sentences, exercises = load()
    sync_templates()
    if reset:
        print(f"Progreso reiniciado: {reset_progress()} tarjeta(s) vuelven a nuevas.")
    moved = reorder_new(new_card_order(entries, sentences, exercises))
    print(f"Orden de nuevas: {moved} tarjeta(s) recolocada(s).")
    orphans(exercises, prune, force)
    moved_decks, removed = place_by_theme(exercises)
    print(f"Subdecks por tema: {moved_decks} tarjeta(s) recolocada(s)"
          + (f"; borrados por vacíos: {', '.join(removed)}" if removed else "") + ".")
    print("Límites: " + ensure_limits())
    anki_request("guiDeckBrowser")
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
    u.add_argument("--prune", action="store_true", help="borrar notas del mazo cuyo ejercicio ya no existe")
    u.add_argument("--reset", action="store_true", help="fase de pruebas: todo el mazo vuelve a nuevas, sin progreso")
    u.add_argument("--force", action="store_true", help=f"con --prune, borrar aunque haya más de {PRUNE_MAX} huérfanas")
    pl = sub.add_parser("plan")
    pl.add_argument("--doc", metavar="LOTE", help="escribe 1-inbox/review-<LOTE>.md")
    sub.add_parser("notebook")
    at = sub.add_parser("attic")
    at.add_argument("batch", nargs="?", metavar="LOTE", help="qué despiertan las entradas nuevas de este lote")
    cb = sub.add_parser("close-batch")
    cb.add_argument("batch", metavar="LOTE", help="NNN-AAAA-MM-DD-tema")
    cb.add_argument("--dry-run", action="store_true", help="mostrar lo que haría sin mover nada")
    sub.add_parser("export")
    sc = sub.add_parser("scaffold")
    sc.add_argument("--write", action="store_true", help="escribir las tarjetas (sin esto, solo se listan)")
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
        return cmd_push(args.allow_missing_audio, not args.no_sync, args.prune, args.reset, args.force)
    if args.cmd == "plan":
        return cmd_plan(args.doc)
    if args.cmd == "notebook":
        return cmd_notebook()
    if args.cmd == "attic":
        return cmd_attic(args.batch)
    if args.cmd == "scaffold":
        return cmd_scaffold(args.write)
    if args.cmd == "export":
        return cmd_export()
    if args.cmd == "close-batch":
        return cmd_close_batch(args.batch, args.dry_run)
    return cmd_build(args.allow_missing_audio)


if __name__ == "__main__":
    sys.exit(main())
