"""La historia de cada entrada, frase y ejercicio, lote a lote, sacada de git.

Cada commit que toca 3-data/ (diccionario, frases, ejercicios) se carga entero y se compara por id con el
anterior: qué nació, qué cambió y qué desapareció. Los commits de un lote (los que contiene su etiqueta
lote-NNN y ninguna anterior, hasta el último que toca datos) son su columna; los commits sueltos entre dos
lotes se juntan en una columna de ajustes; lo que aún no tiene commit, en una columna local. Nada de esto se
escribe a mano: se recalcula desde git cada vez.
"""
import hashlib
import json
import os
import re
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOLDERS = {"lexicon": "entries", "sentences": "sentences", "exercises": "exercises"}
PATHS = [f"3-data/{f}" for f in FOLDERS]
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
BLOBS = {}


def git(*args, data=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=data, capture_output=True, check=True).stdout


def item_hash(item):
    return hashlib.sha1(json.dumps(item, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:12]


def items_of(path, text):
    folder, name = path.split("/")[-2], os.path.splitext(path.split("/")[-1])[0]
    try:
        doc = yaml.load(text, Loader=Loader) or {}
    except yaml.YAMLError:
        return {}
    return {item["id"]: {"folder": folder, "theme": name, "hash": item_hash(item), "item": item}
            for item in doc.get(FOLDERS[folder]) or [] if isinstance(item, dict) and item.get("id")}


def snapshot(commit):
    """Every item of 3-data at one commit. A file is parsed once per content (its blob), however many commits share it."""
    files = []
    for line in git("ls-tree", "-r", commit, *PATHS).decode("utf-8").splitlines():
        meta, name = line.split("\t", 1)
        if name.endswith(".yaml"):
            files.append((meta.split()[2], name))
    todo = [(b, n) for b, n in files if b not in BLOBS]
    if todo:
        raw, pos = git("cat-file", "--batch", data="".join(f"{b}\n" for b, _ in todo).encode("utf-8")), 0
        for b, n in todo:
            nl = raw.index(b"\n", pos)
            size = int(raw[pos:nl].split()[2])
            BLOBS[b] = items_of(n, raw[nl + 1:nl + 1 + size].decode("utf-8"))
            pos = nl + 1 + size + 1
    out = {}
    for b, _ in files:
        out.update(BLOBS[b])
    return out


def working_tree():
    out = {}
    for folder in FOLDERS:
        base = os.path.join(ROOT, "3-data", folder)
        for f in sorted(os.listdir(base)):
            if f.endswith(".yaml"):
                with open(os.path.join(base, f), encoding="utf-8") as fh:
                    out.update(items_of(f"3-data/{folder}/{f}", fh.read()))
    return out


def lote_tags():
    out = []
    for line in git("for-each-ref", "refs/tags/lote-*", "--format=%(refname:short) %(objectname) %(*objectname)").decode().splitlines():
        name, obj, deref = (line.split() + [""])[:3]
        out.append((name, deref or obj))
    return sorted(out)


def build():
    tags = lote_tags()
    log = git("log", "--reverse", "--format=%H\t%aI\t%s", "--", *PATHS).decode("utf-8").splitlines()
    # A lote is the commit that closes it: the tagged one, or the one named `lote NNN-...`.
    lote_of = {sha: name for name, sha in tags}
    for line in log:
        sha, _, subject = line.split("\t", 2)
        if re.match(r"lote \d{3}-", subject) and sha not in lote_of:
            lote_of[sha] = "lote-" + subject.split(" ", 1)[1][:3]
    shas = {l.split("\t", 1)[0] for l in log}
    # Lotes closed before 3-data/ took its current shape (lote 001): the commits before the first lote with data are that lote.
    dataless = [name for name, sha in tags if not any(v == name for k, v in lote_of.items() if k in shas)]
    columns, units, prev = [], {}, {}

    def column_for(sha, date, subject):
        name = lote_of.get(sha)
        if name:
            columns.append({"id": name, "kind": "lote", "label": f"Lote {name.split('-')[-1]}", "title": subject.split(" ", 1)[1] if subject.startswith("lote ") else "",
                            "date": date, "commits": 1})
            return len(columns) - 1
        if not columns and dataless:
            columns.append({"id": dataless[0], "kind": "lote", "label": f"Lote {dataless[0].split('-')[-1]}", "title": "y la estructura de datos de hoy",
                            "date": date, "commits": 1})
            return 0
        if len(columns) == 1 and dataless and columns[0]["id"] == dataless[0]:
            columns[0]["commits"] += 1
            columns[0]["date"] = date
            return 0
        if columns and columns[-1]["kind"] == "ajuste":
            columns[-1]["commits"] += 1
            columns[-1]["date"] = date
            columns[-1]["subjects"].append(subject)
            return len(columns) - 1
        after = next((c["label"] for c in reversed(columns) if c["kind"] == "lote"), None)
        columns.append({"id": f"ajustes-{len(columns)}", "kind": "ajuste", "label": f"Ajustes tras el {after.lower()}" if after else "Antes del primer lote",
                        "date": date, "commits": 1, "subjects": [subject]})
        return len(columns) - 1

    def compare(col, now):
        for uid, u in now.items():
            if uid not in prev:
                units.setdefault(uid, []).append({"col": col, "k": "created"})
            elif prev[uid]["hash"] != u["hash"]:
                units.setdefault(uid, []).append({"col": col, "k": "changed"})
        for uid in prev:
            if uid not in now:
                units.setdefault(uid, []).append({"col": col, "k": "removed"})

    for line in log:
        sha, date, subject = line.split("\t", 2)
        col = column_for(sha, date, subject)
        now = snapshot(sha)
        compare(col, now)
        prev = now
    local = working_tree()
    if any(uid not in prev or prev[uid]["hash"] != u["hash"] for uid, u in local.items()) or any(uid not in local for uid in prev):
        columns.append({"id": "local", "kind": "local", "label": "Sin commit todavía", "date": None, "commits": 0})
        compare(len(columns) - 1, local)
    return {"columns": columns, "history": units, "current": local}


if __name__ == "__main__":
    import time
    t = time.time()
    h = build()
    print(len(h["columns"]), "columnas,", len(h["current"]), "elementos,", f"{time.time() - t:.1f} s")
    for c in h["columns"]:
        print(" ", c["label"], c.get("title", ""), c["commits"])
