"""Pruebas de lo que anki.py hace en la colección de Anki, contra un AnkiConnect simulado.
Lo que protegen: nada fuera de este mazo se mueve, se borra ni se reconfigura, y los borrados masivos se frenan."""
import copy
import io
import re
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import anki  # noqa: E402

OURS = anki.DECK_NAME
MODEL = anki.MODEL_TYPED_NAME


class FakeAnki:
    """Una colección mínima: mazos, tarjetas (una por nota) y presets. Registra las llamadas que escriben."""

    def __init__(self, cards, decks=(), configs=None):
        self.cards = {c["id"]: dict(c) for c in cards}
        self.decks = set(decks) | {c["deck"] for c in cards}
        self.configs = configs or {1: {"id": 1, "name": "Default", "new": {"perDay": 20}, "rev": {"perDay": 200}}}
        self.deck_conf = {d: 1 for d in self.decks}
        self.writes = []

    def _in_deck(self, card, deck):
        return card["deck"] == deck or card["deck"].startswith(deck + "::")

    def _find(self, query):
        if query.startswith("(note:"):                   # our note types, outside our deck
            ours = re.search(r'-"deck:([^"]+)"', query).group(1)
            return [i for i, c in self.cards.items() if c.get("model", MODEL) in (MODEL, anki.MODEL_SELF_NAME)
                    and not self._in_deck(c, ours)]
        deck = re.search(r'"deck:([^"]+)"', query).group(1)
        return [i for i, c in self.cards.items() if self._in_deck(c, deck) and ("is:new" not in query or c["new"])]

    def __call__(self, action, timeout=120, **p):
        if action == "deckNames":
            return sorted(self.decks)
        if action in ("findCards", "findNotes"):
            return self._find(p["query"])
        if action == "cardsInfo":
            return [{"cardId": i, "deckName": self.cards[i]["deck"], "due": self.cards[i].get("due", 0),
                     "fields": {"ExerciseID": {"value": self.cards[i]["ex"]}}} for i in p["cards"]]
        if action == "notesInfo":
            return [{"noteId": i, "modelName": self.cards[i].get("model", MODEL),
                     "fields": {"ExerciseID": {"value": self.cards[i]["ex"]}}} for i in p["notes"]]
        if action == "getReviewsOfCards":
            return {str(i): self.cards[i].get("revlog", []) for i in p["cards"]}
        if action == "getDeckConfig":                     # AnkiConnect devuelve siempre una copia (JSON)
            return copy.deepcopy(self.configs[self.deck_conf[p["deck"]]])
        self.writes.append((action, p))
        if action == "changeDeck":
            self.decks.add(p["deck"])
            for i in p["cards"]:
                self.cards[i]["deck"] = p["deck"]
        elif action == "deleteDecks":
            for d in p["decks"]:
                self.decks.discard(d)
                for i in [i for i, c in self.cards.items() if self._in_deck(c, d)]:
                    del self.cards[i]
        elif action == "deleteNotes":
            for i in p["notes"]:
                del self.cards[i]
        elif action == "cloneDeckConfigId":
            new = max(self.configs) + 1
            self.configs[new] = {**copy.deepcopy(self.configs[p["cloneFrom"]]), "id": new, "name": p["name"]}
            return new
        elif action == "setDeckConfigId":
            for d in p["decks"]:
                self.deck_conf[d] = p["configId"]
        elif action == "saveDeckConfig":
            self.configs[p["config"]["id"]] = copy.deepcopy(p["config"])
        return None

    def touched_cards(self):
        ids = []
        for action, p in self.writes:
            ids += p.get("cards", []) + p.get("notes", [])
            ids += [a["params"]["card"] for a in p.get("actions", [])]
        return ids


def ex(ex_id, theme):
    return {"id": ex_id, "theme": theme}


class AnkiSafety(unittest.TestCase):
    def setUp(self):
        self.saludos = anki.deck_name(1, "saludos")
        self.familia = anki.deck_name(1, "familia")

    def run_with(self, fake, fn, *args):
        with mock.patch.object(anki, "anki_request", fake), redirect_stdout(io.StringIO()) as out:
            result = fn(*args)
        return result, out.getvalue()

    def test_place_by_theme_moves_only_our_cards(self):
        fake = FakeAnki([
            {"id": 1, "deck": self.saludos, "ex": "x.a", "new": True},
            {"id": 2, "deck": f"{OURS}::2026-09", "ex": "x.b", "new": True},       # subdeck antiguo, por mes
            {"id": 3, "deck": "HSK 1", "ex": "x.b", "new": True, "model": "Basic"},  # otro mazo con un ID igual
            {"id": 4, "deck": "Pimsleur::Unit 1", "ex": "zzz", "new": False},
        ])
        (moved, removed), _ = self.run_with(fake, anki.place_by_theme, [ex("x.a", "saludos"), ex("x.b", "familia")])
        self.assertEqual(moved, 1)
        self.assertEqual(fake.cards[2]["deck"], self.familia)
        self.assertEqual(fake.cards[3]["deck"], "HSK 1")
        self.assertEqual(fake.cards[4]["deck"], "Pimsleur::Unit 1")
        self.assertEqual(removed, [f"{OURS}::2026-09"])
        self.assertIn("HSK 1", fake.decks)
        self.assertIn("Pimsleur::Unit 1", fake.decks)
        self.assertNotIn(3, fake.touched_cards())

    def test_place_by_theme_recovers_our_cards_left_in_the_default_deck(self):
        fake = FakeAnki([
            {"id": 1, "deck": "Predeterminado", "ex": "x.a", "new": True},
            {"id": 2, "deck": "Predeterminado", "ex": "otra", "new": True, "model": "Basic"},   # ajena: se queda
        ])
        (moved, _), _ = self.run_with(fake, anki.place_by_theme, [ex("x.a", "saludos")])
        self.assertEqual(moved, 1)
        self.assertEqual(fake.cards[1]["deck"], self.saludos)
        self.assertEqual(fake.cards[2]["deck"], "Predeterminado")

    def test_place_by_theme_keeps_a_stale_subdeck_that_still_has_cards(self):
        fake = FakeAnki([{"id": 1, "deck": f"{OURS}::viejo", "ex": "x.desconocido", "new": True}])
        (_, removed), _ = self.run_with(fake, anki.place_by_theme, [ex("x.a", "saludos")])
        self.assertEqual(removed, [])
        self.assertIn(1, fake.cards)

    def test_prune_needs_force_when_many(self):
        lost = [{"id": i, "deck": self.saludos, "ex": f"x.lost{i}", "new": True} for i in range(anki.PRUNE_MAX + 1)]
        fake = FakeAnki(lost)
        _, out = self.run_with(fake, anki.orphans, [], True, False)
        self.assertEqual(len(fake.cards), anki.PRUNE_MAX + 1)
        self.assertIn("--force", out)
        self.run_with(fake, anki.orphans, [], True, True)
        self.assertEqual(fake.cards, {})

    def test_prune_ignores_other_note_types_and_other_decks(self):
        fake = FakeAnki([
            {"id": 1, "deck": self.saludos, "ex": "x.lost", "new": True},
            {"id": 2, "deck": self.saludos, "ex": "x.lost2", "new": True, "model": "Basic"},
            {"id": 3, "deck": "HSK 1", "ex": "x.lost3", "new": True},
        ])
        self.run_with(fake, anki.orphans, [], True, False)
        self.assertEqual(sorted(fake.cards), [2, 3])

    def test_without_prune_nothing_is_deleted(self):
        fake = FakeAnki([{"id": 1, "deck": self.saludos, "ex": "x.lost", "new": True}])
        self.run_with(fake, anki.orphans, [], False, False)
        self.assertEqual(fake.writes, [])

    def test_reset_touches_only_our_deck(self):
        fake = FakeAnki([
            {"id": 1, "deck": self.saludos, "ex": "x.a", "new": False},
            {"id": 2, "deck": "HSK 1", "ex": "x.a", "new": False},
        ])
        count, _ = self.run_with(fake, anki.reset_progress)
        self.assertEqual(count, 1)
        self.assertEqual(set(fake.touched_cards()), {1})

    def test_reset_refused_once_testing_is_over(self):
        def must_not_run(*a, **k):
            raise AssertionError("no debía llegar a compilar ni tocar Anki")
        with mock.patch.object(anki, "TESTING_PHASE", False), mock.patch.object(anki, "cmd_build", must_not_run), \
                mock.patch.object(anki, "anki_request", must_not_run), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(anki.cmd_push(False, False, reset=True), 1)
        self.assertIn("fase de pruebas", out.getvalue())

    def test_stats_only_reads_our_deck(self):
        fake = FakeAnki([{"id": 1, "deck": self.saludos, "ex": "x.a", "new": False},
                         {"id": 2, "deck": "HSK 1", "ex": "x.a", "new": False}])
        queries = []
        def spy(action, timeout=120, **p):
            if action == "findCards":
                queries.append(p["query"])
            if action == "cardsInfo":
                self.assertNotIn(2, p["cards"])
            return fake(action, timeout, **p)
        with mock.patch.object(anki, "anki_ready", lambda: True):
            self.run_with(spy, anki.cmd_stats, 30, False)
        self.assertEqual(fake.writes, [])
        self.assertTrue(queries and all(f'"deck:{OURS}"' in q for q in queries))

    def test_limits_use_our_own_preset(self):
        fake = FakeAnki([{"id": 1, "deck": self.saludos, "ex": "x.a", "new": True},
                         {"id": 2, "deck": "HSK 1", "ex": "y", "new": True}], decks=[OURS])
        self.run_with(fake, anki.ensure_limits)
        ours = fake.deck_conf[OURS]
        self.assertEqual(fake.configs[ours]["name"], anki.DECK_PRESET)
        self.assertEqual(fake.configs[ours]["new"]["perDay"], anki.NEW_PER_DAY)
        self.assertEqual(fake.configs[ours]["new"]["delays"], anki.LEARN_STEPS)      # fallar: vuelve en minutos
        self.assertEqual(fake.configs[ours]["lapse"]["delays"], anki.RELEARN_STEPS)
        self.assertNotIn("lapse", fake.configs[1])                                    # el compartido, intacto
        self.assertEqual((fake.configs[ours]["newGatherPriority"], fake.configs[ours]["newSortOrder"]),
                         (anki.NEW_GATHER_LOWEST_POSITION, anki.NEW_SORT_NONE))       # el orden calculado, no al azar
        self.assertNotIn("newGatherPriority", fake.configs[1])
        conf = fake.configs[ours]
        self.assertEqual(conf["new"]["ints"][:2], [anki.GRADUATING_DAYS, anki.EASY_DAYS])  # mañana, tras dormir
        self.assertEqual(conf["lapse"]["minInt"], anki.LAPSE_MIN_DAYS)                     # un fallo vuelve mañana
        self.assertEqual((conf["newMix"], conf["reviewOrder"]),
                         (anki.REVIEWS_BEFORE_NEW, anki.REVIEW_ORDER_AT_RISK_FIRST))         # repasos primero, en riesgo antes
        self.assertNotIn("reviewOrder", fake.configs[1])
        self.assertEqual(fake.deck_conf["HSK 1"], 1)
        self.assertEqual(fake.configs[1]["new"]["perDay"], 20)            # el preset compartido, intacto


if __name__ == "__main__":
    unittest.main()
