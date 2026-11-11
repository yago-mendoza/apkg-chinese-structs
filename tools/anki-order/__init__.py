# Chino práctico: new-card order. AnkiConnect (since its October 2026 rewrite) refuses to change a card's position
# («Use native scheduling commands for protected state») and has no reposition action, so anki.py's order of new
# cards (class first, level by level, interleaved: docs/design.md, «Orden de nuevas») never reached Anki.
#
# anki.py writes a request into this add-on's user_files folder: {"token": ..., "deck": full deck path, "moves": [[card
# id, position], ...]}. The deck path comes from anki.py (DECK_NAME), since YAGO moves the deck around in Anki (2026-11-09:
# from «🀄 Chinese::🐉 Chino práctico» to «🌐 Language::🀄 Chino práctico»); a path whose own name does not end in
# «Chino práctico» is refused whole. This add-on, polling once a second on Anki's main thread, checks each card is new
# and in that deck (anything else is refused, never touched), sets its position, and answers in the same folder:
# {"token": ..., "moved": n, "refused": [...]}. Only new cards' positions change: never a review, an interval or
# another deck. Installed by copying this folder into Anki's addons21 folder (see README.md); Anki must restart.
import json
import os

from aqt import mw
from aqt.qt import QTimer

OWN_NAME = "Chino práctico"   # the deck's own name ends like this wherever it lives in Anki
HERE = os.path.join(os.path.dirname(__file__), "user_files")
REQUEST, ANSWER = os.path.join(HERE, "request.json"), os.path.join(HERE, "answer.json")


def _ours(card, deck):
    name = mw.col.decks.name(card.did)
    return name == deck or name.startswith(deck + "::")


def _serve():
    if not mw.col or not os.path.isfile(REQUEST):
        return
    try:
        with open(REQUEST, encoding="utf-8") as f:
            req = json.load(f)
        os.remove(REQUEST)
    except (OSError, ValueError):
        return
    moved, refused, changed = 0, [], []
    deck = str(req.get("deck") or "")
    if not deck.split("::")[-1].endswith(OWN_NAME):
        refused = [[cid, "unknown deck"] for cid, _ in req.get("moves", [])]
    for cid, pos in ([] if refused else req.get("moves", [])):
        try:
            card = mw.col.get_card(int(cid))
        except Exception:
            refused.append([cid, "missing"])
            continue
        if card.type != 0 or card.queue != 0 or not _ours(card, deck):
            refused.append([cid, "not a new card of the deck"])
            continue
        if card.due != int(pos):
            card.due = int(pos)
            changed.append(card)
        moved += 1
    if changed:
        mw.col.update_cards(changed)
    tmp = ANSWER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"token": req.get("token"), "moved": moved, "changed": len(changed), "refused": refused}, f)
    os.replace(tmp, ANSWER)


os.makedirs(HERE, exist_ok=True)
_timer = QTimer(mw)
_timer.timeout.connect(_serve)
_timer.start(1000)
