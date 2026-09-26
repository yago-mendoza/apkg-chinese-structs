"""Consulta, validación, cobertura, audio y compilación del mazo de chino.

Uso:
    python anki.py lookup <hanzi|pinyin|significado>
    python anki.py plan [--doc <lote>]     tarjetas exigidas que faltan; --doc escribe 1-inbox/gaps-<lote>.md
    python anki.py gaps                    reparto del mazo y pendientes
    python anki.py check
    python anki.py guide                   regenera 5-guide/ desde 3-data/
    python anki.py audio [--dry-run]
    python anki.py build [--allow-missing-audio]
    python anki.py push [--allow-missing-audio] [--no-sync] [--prune]

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

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "3-data"                    # fuente de verdad, mantenida por el agente
LEXICON = DATA / "lexicon.yaml"
EXERCISES = DATA / "exercises.yaml"
MEDIA = DATA / "audio"                  # MP3 generados; no regenerar
AUDIO_MANIFEST = MEDIA / "index.yaml"
INBOX = ROOT / "1-inbox"                  # apuntes en bruto de YAGO
GUIDE = ROOT / "5-guide"                  # guía acumulada por temas, generada
OUTPUT = ROOT / "6-output"                # lo que sale: mazo y futuras exportaciones
APKG = OUTPUT / "chino-practico.apkg"
ANKI_CONNECT = "http://127.0.0.1:8765"

# Identidades estables: no cambiarlas nunca, o Anki verá un mazo/modelo nuevo.
GUID_NAMESPACE = "apkg-chinese-structs"
DECK_NAME = "🐉 Chino práctico"          # un subdeck por mes: "🐉 Chino práctico::2026-09"
DECK_ID_BASE = 1_758_800_000_000         # ID del subdeck = base + AAAAMM
MODEL_TYPED_ID = 1_758_800_101
MODEL_SELF_ID = 1_758_800_102
AUDIO_PREFIX = "acs_"
MODEL_TYPED_NAME = "Chino práctico (tecleada)"
MODEL_SELF_NAME = "Chino práctico (autoevaluación)"
DECK_PRESET = "🐉 Chino práctico"          # preset propio: nunca tocar el de otros mazos
NEW_PER_DAY, REVIEWS_PER_DAY = 30, 300

AZURE_VOICE = os.environ.get("AZURE_SPEECH_VOICE", "zh-CN-YunyangNeural")
# Más despacio que lo normal: más claro para aprender tonos. Las palabras sueltas, aún más.
AZURE_RATE = "-30%"
AZURE_RATE_WORD = "-40%"
AZURE_LEAD_MS = 200        # silencio inicial: algunos reproductores cortan el primer instante
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
    try:
        from dragonmapper.transcriptions import pinyin_to_ipa
        out = pinyin_to_ipa(" ".join(parts))
    except Exception:
        return ""
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
        if mods:
            req.add("recognize")
    elif kind == "pronunciation":
        if "hear" in mods:
            req.add("listen")
        if "say" in mods:
            req.add("speak")
    if mods:
        for g in groups_of.get(item.get("id"), []):
            if g.get("basis") in ("visual", "homophone"):
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
    # Palabras de frases aún no registradas que coinciden.
    loose = {f"{seg['text']} {seg.get('pinyin', '')}".strip() for s in sentences for seg in s["segments"]
             if not seg.get("ref") and seg.get("pinyin") and q and
             (q in seg["text"] or q_plain == compact(strip_tones(seg["pinyin"])))}
    if loose:
        print("\nEn frases, sin entrada: " + ", ".join(sorted(loose)))


PRIMARY = {"read": "lectura", "listen": "escucha", "tones": "tonos", "produce": "producción",
           "derive": "producción", "cloze": "producción", "speak": "voz alta", "contrast": "contraste",
           "components": "componentes"}
GENERATED = "<!-- Generado por `anki.py guide` desde 3-data/. No editar: se rehace en cada lote. -->"
GAPS_HEADER = ("<!-- Documento editable: escribe encima, tacha, añade dudas. "
               "Todo lo que pongas aquí entra en el siguiente lote. -->")


def load_themes():
    return load_yaml(LEXICON).get("themes", [])


def cmd_gaps():
    """Reparto del mazo: cada tarjeta cuenta una vez, por lo que practica."""
    from collections import Counter
    entries, sentences, exercises = load()
    manifest = load_manifest()
    by_skill = Counter(PRIMARY.get(ex.get("type"), ex.get("type")) for ex in exercises)
    print(f"{len(exercises)} tarjetas (registrado no equivale a aprendido).\n")
    for skill, n in by_skill.most_common():
        print(f"  {skill:12} {n:4}  {100 * n / len(exercises):5.1f} %")
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
    raw = sorted(f.name for f in INBOX.glob("*.txt")) if INBOX.exists() else []
    print(f"Inbox sin procesar: {len(raw)}" + (f" → {', '.join(raw)}" if raw else ""))


def label(item):
    return item.get("hanzi") or item.get("title") or ("".join(seg["text"] for seg in item.get("segments", [])))


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
        write_gaps_doc(doc, osm)
    return 0


def write_gaps_doc(batch, osm):
    """Deja en 1-inbox/ los huecos que necesitan a YAGO. Lo pendiente del digest lo añade el agente."""
    INBOX.mkdir(exist_ok=True)
    for old in INBOX.glob("gaps-*.md"):
        print(f"AVISO  ya había {old.name}: archívalo en 2-raw/ con el lote que lo leyó antes de generar otro.")
        return
    lines = [GAPS_HEADER, "", f"# Huecos tras el lote {batch}", ""]
    lines += ["## Palabras que quieres decir y aún no tienen frase", "",
              "Trae una frase de clase o de tu día a día que las use (o dime una que digas tú).", ""]
    lines += [f"- {e['hanzi']} {e.get('pinyin', '')} · {e.get('meaning', {}).get('es', '')}" for e in osm] or ["- (ninguna)"]
    lines += ["", "## Pendiente de tus apuntes", "", "<!-- lo rellena el agente desde el digest -->", "",
              "## Dudas y ajustes", "", "- ", ""]
    path = INBOX / f"gaps-{batch}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito {path.relative_to(ROOT)}")


def mark(item, has_cards):
    u, mods = item.get("use"), use_modalities(item)
    m = "❌" if u == "drop" else "✅" if (mods & {"hear", "say"} or u == "context") else "🟡"
    return m + ("🃏" if has_cards else "")


def cmd_guide():
    """Regenera 5-guide/: todo lo aprendido, un archivo por tema, desde 3-data/."""
    entries, sentences, exercises = load()
    themes = load_themes()
    targeted = {t for ex in exercises for t in ex.get("targets", [])}
    eby = {e["id"]: e for e in entries}
    GUIDE.mkdir(exist_ok=True)
    for old in GUIDE.glob("*.md"):
        if old.read_text(encoding="utf-8").startswith(GENERATED):
            old.unlink()
    index = [GENERATED, "", "# Guía", "", "Todo lo aprendido, por temas. ✅ aprender · 🟡 reconocer · ❌ descartado · 🃏 en el mazo.", ""]
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
                           + (f" · {notes}" if notes else ""))
            out.append("")
        for g in (e for e in items if e.get("kind") == "group"):
            out += [f"## {g['title']}", "", g.get("explanation", ""), ""]
            out += [f"- {eby[m['ref']]['hanzi']} {eby[m['ref']].get('pinyin', '')} · {m.get('cue', '')}"
                    for m in g.get("members", []) if m["ref"] in eby]
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
        (GUIDE / name).write_text("\n".join(out), encoding="utf-8")
        index.append(f"- [{th['title']}]({name}) · {len(items)} entradas, {len(sents)} frases")
    (GUIDE / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Guía regenerada: {len(themes)} temas en {GUIDE.relative_to(ROOT)}/")
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
    raw = json.dumps([text, voice, audio_rate(text), AZURE_LEAD_MS, AZURE_FORMAT], ensure_ascii=False, sort_keys=True)
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
                       "lead_ms": AZURE_LEAD_MS,
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
.acs-in { font-size: 20px; padding: 6px 10px; width: 12em; max-width: 90%; text-align: center;
          border: 1px solid #999; border-radius: 6px; background: transparent; color: inherit; }
#acs-result { font-size: 20px; margin-bottom: 8px; }
.acs-ok { color: #2e7d32; } .acs-bad { color: #c62828; }
.legend { font-size: 13px; opacity: .7; margin-top: 10px; }
.ipa { font-size: 15px; opacity: .6; margin-top: 2px; }
"""
# Los colores solo alinean segmentos hanzi↔pinyin; los tonos se leen por sus marcas.

FIELDS = ["ExerciseID", "Task", "Front", "PromptAudio", "Answer", "Back", "AnswerAudio", "Notes"]

# Respuesta tecleada sin la comparación literal de Anki: la tarjeta guarda lo escrito (sessionStorage)
# y el reverso lo compara normalizado (espacios, mayúsculas, tildes o dígitos, v = ü). Si el cliente
# no conserva sessionStorage entre anverso y reverso, la tarjeta queda como autoevaluación.
TYPED_JS_FRONT = """<script>
setTimeout(function () {
  var i = document.getElementById('acs-in'); if (!i) return;
  if (document.getElementById('answer')) { i.style.display = 'none'; return; }
  var save = function () { try { sessionStorage.setItem('acs-typed', i.value); } catch (e) {} };
  try { sessionStorage.removeItem('acs-typed'); } catch (e) {}
  i.addEventListener('input', save);
  i.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { save(); try { pycmd('ans'); } catch (x) {} }
  });
  i.focus();
}, 0);
</script>"""

TYPED_JS_BACK = """<script>
setTimeout(function () {
  var M = {a:'āáǎà', e:'ēéěè', i:'īíǐì', o:'ōóǒò', u:'ūúǔù', 'ü':'ǖǘǚǜ'};
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
    s = (s || '').normalize('NFC').toLowerCase().replace(/u:/g, 'ü').replace(/v/g, 'ü')
          .replace(/[\\s'’·,.\\-]/g, '');
    return /^[1-5]+$/.test(s) ? s : mark(s);
  }
  var out = document.getElementById('acs-result'), exp = document.getElementById('acs-expected');
  if (!out || !exp) return;
  var typed = null; try { typed = sessionStorage.getItem('acs-typed'); } catch (e) {}
  if (typed === null || typed.trim() === '') return;
  var ok = norm(typed) === norm(exp.textContent);
  out.className = ok ? 'acs-ok' : 'acs-bad';
  out.textContent = ok ? '✓ ' + typed : '✗ ' + typed;
}, 0);
</script>"""

FRONT_TYPED = ('<div class="task">{{Task}}</div>{{Front}}{{PromptAudio}}'
               '<br><input id="acs-in" class="acs-in" autocomplete="off" autocapitalize="off" '
               'autocorrect="off" spellcheck="false" placeholder="pinyin">' + TYPED_JS_FRONT)
FRONT_SELF = '<div class="task">{{Task}}</div>{{Front}}{{PromptAudio}}'
BACK = ('{{FrontSide}}<hr id="answer"><div id="acs-result"></div>'
        '<div id="acs-expected" style="display:none">{{Answer}}</div>'
        '{{Back}}{{AnswerAudio}}{{Notes}}' + TYPED_JS_BACK)
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
    if ex["type"] == "tones":
        front += ('<div class="legend">1 ā alto y plano · 2 á sube · 3 ǎ baja (y sube) · 4 à baja fuerte · '
                  '5 a neutro, corto</div>')
    prompt_audio = sound(spoken, manifest, media_files) if prompt.get("audio") else ""
    if prompt.get("audio") and not prompt_audio:
        # Solo ocurre con --allow-missing-audio: que la tarjeta no parezca rota.
        prompt_audio = '<div class="task">(audio pendiente)</div>'

    if sent:
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
            example = (f"<div>Ejemplo del fenómeno: {esc(p.get('audio_text'))} "
                       f"{sound(p.get('audio_text'), manifest, media_files)}</div>") if p.get("audio_text") else ""
            notes.append(f"<h4>{esc(p.get('title'))}</h4>{esc(p.get('explanation'))}{example}")
    for sid in ex.get("reveal", []):
        s = sby.get(sid)
        if s:
            notes.append(f"<h4>Ejemplo</h4>{render_sentence(s)}<div>{esc(s['translation'].get(lang))}</div>"
                         f"{sound(sentence_text(s), manifest, media_files)}")
    # Comentarios: solo los marcados private: false (del ejercicio y de sus objetivos).
    comments = list(ex.get("comments", []))
    for tid in ex.get("targets", []):
        comments += eby.get(tid, {}).get("comments", [])
    labels = {"mnemonic": "Mnemotecnia", "teacher": "Profesora", "linguistic": "Nota", "note": "Apunte",
              "sound": "Cómo suena"}
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
        "typed": genanki.Model(MODEL_TYPED_ID, MODEL_TYPED_NAME, fields=fields, css=CSS,
                               templates=[{"name": "Tarjeta", "qfmt": FRONT_TYPED, "afmt": BACK}]),
        "self": genanki.Model(MODEL_SELF_ID, MODEL_SELF_NAME, fields=fields, css=CSS,
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


STAGE = {"read": 0, "contrast": 1, "components": 1, "listen": 2, "tones": 3,
         "produce": 4, "derive": 4, "cloze": 4, "speak": 5}


def new_card_order(entries, sentences, exercises):
    """Posición de cada ejercicio entre las nuevas: por tema, y cada paso (lectura, escucha, tonos,
    producción) dos temas por detrás del anterior, para que las tarjetas de una misma entrada no
    salgan el mismo día (Anki solo separa hermanas de una misma nota)."""
    theme_idx = {t["id"]: i for i, t in enumerate(load_themes())}
    items = {it["id"]: (theme_idx.get(it.get("theme"), 99), n) for n, it in enumerate(entries + sentences)}
    def key(ex):
        th, n = items.get((ex.get("targets") or [None])[0], (99, 0))
        stage = STAGE.get(ex.get("type"), 1)
        return (th + 2 * stage, th, n, stage, ex["id"])
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


def orphans(exercises, prune):
    notes = anki_request("findNotes", query=f'"deck:{DECK_NAME}"')
    info = anki_request("notesInfo", notes=notes) if notes else []
    ids = {ex["id"] for ex in exercises}
    lost = [n for n in info if n["modelName"] in (MODEL_TYPED_NAME, MODEL_SELF_NAME)
            and n["fields"]["ExerciseID"]["value"] not in ids]
    for n in lost:
        print(f"  huérfana: {n['fields']['ExerciseID']['value']}")
    if lost and prune:
        anki_request("deleteNotes", notes=[n["noteId"] for n in lost])
        print(f"Borradas {len(lost)} nota(s) huérfana(s).")
    elif lost:
        print(f"{len(lost)} nota(s) del mazo ya no existen en 3-data/. Revisar y repetir con --prune para borrarlas.")


def cmd_push(allow_missing_audio, sync, prune=False):
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
    print("Límites: " + ensure_limits())
    moved = reorder_new(new_card_order(entries, sentences, exercises))
    print(f"Orden de nuevas: {moved} tarjeta(s) recolocada(s).")
    orphans(exercises, prune)
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
    pl = sub.add_parser("plan")
    pl.add_argument("--doc", metavar="LOTE", help="escribe 1-inbox/gaps-<LOTE>.md")
    sub.add_parser("guide")
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
        return cmd_push(args.allow_missing_audio, not args.no_sync, args.prune)
    if args.cmd == "plan":
        return cmd_plan(args.doc)
    if args.cmd == "guide":
        return cmd_guide()
    return cmd_build(args.allow_missing_audio)


if __name__ == "__main__":
    sys.exit(main())
