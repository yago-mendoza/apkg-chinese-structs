"""La app de revisión: abre las tarjetas del mazo, dice qué entrada o frase respalda cada una y dibuja la
historia de todo, lote a lote.

    .\\.venv\\Scripts\\python tools\\review\\serve.py            arranca en http://127.0.0.1:5198/ y la abre
    .\\.venv\\Scripts\\python tools\\review\\serve.py --no-open  sin abrir el navegador
    .\\.venv\\Scripts\\python tools\\review\\serve.py --pending  lista los pedidos de YAGO aún sin atender
    .\\.venv\\Scripts\\python tools\\review\\serve.py --stale    tarjetas cuya entrada o frase cambió después que ellas, y al revés
    .\\.venv\\Scripts\\python tools\\review\\serve.py --checked <id> ...   revisada: no hacía falta cambiar nada

La historia sale de git (tools/review/history.py). Lo que YAGO hace en la app (su visto bueno, sus pedidos) se
apunta en records/review-log.jsonl, un evento por línea; records/ se versiona con el resto del
repositorio. Con Anki abierto, la app enseña cada tarjeta tal cual la dibuja Anki y la abre en su
navegador; sin Anki, enseña los datos.
"""
import base64
import json
import mimetypes
import os
import re
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history  # noqa: E402

ROOT = history.ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
RECORDS = os.path.join(ROOT, "records")
LOG = os.path.join(RECORDS, "review-log.jsonl")
ANKI = "http://127.0.0.1:8765"
with open(os.path.join(ROOT, "anki.py"), encoding="utf-8") as fh:
    DECK = re.search(r'^DECK_NAME = "([^"]+)"', fh.read(), re.M).group(1)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_log():
    if not os.path.exists(LOG):
        return []
    with open(LOG, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def append(events):
    os.makedirs(RECORDS, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        for e in events:
            fh.write(json.dumps({"t": now(), **e}, ensure_ascii=False) + "\n")


def anki(action, **params):
    body = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    with urllib.request.urlopen(urllib.request.Request(ANKI, data=body), timeout=8) as r:
        out = json.load(r)
    if out.get("error"):
        raise RuntimeError(out["error"])
    return out["result"]


def text_of(v):
    return v.get("es") if isinstance(v, dict) else (v or "")


def describe(uid, u):
    it, f = u["item"], u["folder"]
    if f == "lexicon":
        return {"kind": "entry", "name": f"{it.get('hanzi', '')} {it.get('pinyin', '')}".strip(), "gloss": text_of(it.get("meaning")), "type": it.get("kind", ""),
                "links": []}
    if f == "sentences":
        segs = it.get("segments") or []
        return {"kind": "sentence", "name": "".join(s.get("text", "") for s in segs), "gloss": text_of(it.get("translation")), "type": "frase",
                "links": sorted({s["ref"] for s in segs if s.get("ref")})}
    ans, pr = it.get("answer") or {}, it.get("prompt") or {}
    return {"kind": "card", "name": ans.get("hanzi") or pr.get("hanzi") or ans.get("pinyin") or uid, "gloss": text_of(ans.get("meaning")) or pr.get("text", ""),
            "type": it.get("type", ""), "links": list(dict.fromkeys([*(it.get("targets") or []), *(it.get("context") or []), *(it.get("reveal") or [])]))}


def build_data():
    h = history.build()
    with open(os.path.join(ROOT, "3-data", "themes.yaml"), encoding="utf-8") as fh:
        themes = (yaml.safe_load(fh) or {}).get("themes") or []
    units = []
    for uid, u in h["current"].items():
        d = describe(uid, u)
        units.append({"id": uid, "folder": u["folder"], "theme": u["theme"], "hash": u["hash"], **d, "history": h["history"].get(uid, []),
                      "raw": yaml.safe_dump(u["item"], allow_unicode=True, sort_keys=False, width=110)})
    return {"built": now(), "deck": DECK, "columns": h["columns"], "themes": [{"id": t.get("id"), "title": t.get("title")} for t in themes],
            "units": units, "events": read_log()}


PAGE = os.path.join(HERE, "page.html")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else (body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8" if ctype.startswith(("text", "application/json")) else ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(min(n, 1_000_000)) or b"{}")

    def do_GET(self):
        path = self.path.split("?")[0]
        q = dict(p.split("=", 1) for p in self.path.split("?", 1)[1].split("&")) if "?" in self.path else {}
        if path in ("/", "/index.html"):
            with open(PAGE, encoding="utf-8") as fh:
                return self.send(200, fh.read(), "text/html")
        if path == "/api/data":
            return self.send(200, build_data())
        if path == "/api/card":
            # The card as Anki draws it, with its review history.
            eid = urllib.parse.unquote(q.get("id", ""))
            try:
                ids = anki("findCards", query=f'"deck:{DECK}" "ExerciseID:{eid}"')
                if not ids:
                    return self.send(200, {"ok": True, "found": False})
                c = anki("cardsInfo", cards=ids[:1])[0]
                # Anki renders sounds as [anki:play:q:N] / [anki:play:a:N]: the Nth sound of that side, in field order.
                fields = {k: v["value"] for k, v in sorted(c.get("fields", {}).items(), key=lambda kv: kv[1]["order"])}
                sounds = lambda names: [s for n in names for s in re.findall(r"\[sound:([^\]]+)\]", fields.get(n, ""))]
                q_s, a_s = sounds(["Front", "PromptAudio"]), sounds(list(fields))
                play = lambda html, side, lst: re.sub(rf"\[anki:play:{side}:(\d+)\]", lambda m: f"[sound:{lst[int(m.group(1))]}]" if int(m.group(1)) < len(lst) else "", html or "")
                c["question"], c["answer"] = play(c.get("question"), "q", q_s), play(play(c.get("answer"), "a", a_s), "q", q_s)
                return self.send(200, {"ok": True, "found": True, "question": c.get("question"), "answer": c.get("answer"), "css": c.get("css", ""),
                                       "deck": c.get("deckName"), "interval": c.get("interval"), "reps": c.get("reps"), "lapses": c.get("lapses"),
                                       "due": c.get("due"), "queue": c.get("queue")})
            except Exception as e:  # Anki closed or AnkiConnect missing
                return self.send(200, {"ok": False, "error": str(e)})
        if path.startswith("/media/"):
            name = urllib.parse.unquote(path[len("/media/"):])
            try:
                data = anki("retrieveMediaFile", filename=name)
                if data:
                    return self.send(200, base64.b64decode(data), mimetypes.guess_type(name)[0] or "application/octet-stream")
            except Exception:
                pass
            return self.send(404, b"", "text/plain")
        if path == "/favicon.ico":
            return self.send(204, b"", "text/plain")
        self.send(404, {"ok": False})

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            b = self.body()
        except ValueError:
            return self.send(400, {"ok": False})
        if path == "/api/log":
            ok = {"approved", "unapproved", "note", "cleared", "view", "caused", "checked", "start"}
            ev = [{k: (str(v)[:5000] if isinstance(v, str) else v) for k, v in e.items() if k in ("type", "unit", "hash", "text", "id", "from", "to", "what", "against")}
                  for e in b.get("events", []) if e.get("type") in ok and (e.get("unit") or e.get("id"))]
            append(ev)
            return self.send(200, {"ok": True, "written": len(ev)})
        if path == "/api/browse":
            try:
                anki("guiBrowse", query=f'"deck:{DECK}" "ExerciseID:{b.get("id", "")}"')
                return self.send(200, {"ok": True})
            except Exception as e:
                return self.send(200, {"ok": False, "error": str(e)})
        self.send(404, {"ok": False})


def stale(h=None, log=None):
    """Unit -> [(other, column)]: what changed on the other side after this one was last touched or checked.

    A tarjeta only asks what its entries and sentences hold, so when one of them changes later, the tarjeta is due for
    a look against it, and the other way round. Changes before the review began (the first `start` event) do not
    count: those lotes were validated by `anki.py check` when they closed."""
    h = h or history.build()
    log = read_log() if log is None else log
    cols = h["columns"]
    start = min((datetime.fromisoformat(e["t"]).timestamp() for e in log if e["type"] == "start"), default=None)
    when = lambda c: datetime.fromisoformat(cols[c]["date"]).timestamp() if cols[c]["date"] else datetime.now(timezone.utc).timestamp()
    changed, born, checked = {}, {}, {}
    for uid, hs in h["history"].items():
        for x in hs:
            t = when(x["col"])
            if x["k"] == "changed" and (start is None or t > start):
                changed[uid] = max(changed.get(uid, 0), t)
            if x["k"] == "created" and uid not in born:
                born[uid] = t
    for e in log:
        if e["type"] == "checked":
            k = (e["unit"], e.get("against"))
            checked[k] = max(checked.get(k, 0), datetime.fromisoformat(e["t"]).timestamp())
    out = {}
    for uid, u in h["current"].items():
        for l in describe(uid, u)["links"]:
            if l not in h["current"]:
                continue
            for a, b in ((uid, l), (l, uid)):
                if changed.get(b, 0) > max(changed.get(a, 0), born.get(a, 0), checked.get((a, b), 0), start or 0):
                    out.setdefault(a, set()).add(b)
    return out


def pending():
    notes, done = {}, set()
    for e in read_log():
        if e["type"] == "note":
            notes[e["id"]] = e
        elif e["type"] in ("cleared", "applied"):
            done.add(e["id"])
    left = [n for k, n in notes.items() if k not in done and n.get("text")]
    for n in left:
        print(f"{n['id']}  {n['unit']}\n    {n['text']}\n")
    print(f"{len(left)} pedidos sin atender.")


if __name__ == "__main__":
    if "--pending" in sys.argv:
        pending()
        sys.exit(0)
    if "--stale" in sys.argv or "--checked" in sys.argv:
        if not any(e["type"] == "start" for e in read_log()):
            append([{"type": "start", "unit": "*"}])
        due = stale()
        if "--checked" in sys.argv:
            ids = [a for a in sys.argv[sys.argv.index("--checked") + 1:] if not a.startswith("--")]
            append([{"type": "checked", "unit": i, "against": o} for i in ids for o in sorted(due.get(i, ()))])
            print(f"{sum(len(due.get(i, ())) for i in ids)} revisiones apuntadas.")
        else:
            for uid in sorted(due):
                print(uid, "\n    " + "\n    ".join(sorted(due[uid])))
            print(f"{len(due)} por revisar." if due else "Nada por revisar: cada tarjeta está al día con sus entradas y frases.")
        sys.exit(0)
    if "--done" in sys.argv:
        # Mark requests done: --done <id> ... [--touched <id> ...] [--created <id> ...]; the cross matrices read these.
        def after(flag):
            if flag not in sys.argv:
                return []
            out = []
            for a in sys.argv[sys.argv.index(flag) + 1:]:
                if a.startswith("--"):
                    break
                out.append(a)
            return out
        notes = {e["id"]: e for e in read_log() if e["type"] == "note"}
        ids = [i for i in after("--done") if i in notes]
        append([ev for i in ids for ev in [{"type": "applied", "id": i},
                                           *[{"type": "caused", "id": i, "from": notes[i]["unit"], "to": t, "what": "edit"} for t in after("--touched")],
                                           *[{"type": "caused", "id": i, "from": notes[i]["unit"], "to": t, "what": "create"} for t in after("--created")]]])
        print(f"{len(ids)} pedidos marcados como atendidos.")
        sys.exit(0)
    if not any(e["type"] == "start" for e in read_log()):
        append([{"type": "start", "unit": "*"}])  # the review begins: only changes after this count as due
    port = 5198
    for port in range(5198, 5210):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    url = f"http://127.0.0.1:{port}/"
    print(f"revisión en {url} (Ctrl+C para parar); registro: records/review-log.jsonl")
    if "--no-open" not in sys.argv:
        threading.Timer(.6, lambda: webbrowser.open(url)).start()
    server.serve_forever()
