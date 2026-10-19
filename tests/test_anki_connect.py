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
        elif action == "multi":
            for a in p["actions"]:
                if a["action"] == "setSpecificValueOfCard" and a["params"]["keys"] == ["due"]:
                    self.cards[a["params"]["card"]]["due"] = a["params"]["newValues"][0]
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

    def test_prune_keeps_cards_with_real_reviews(self):
        """Lote 012: una tarjeta que perdió su progreso parece nueva, pero su historial dice que se estudió."""
        fake = FakeAnki([
            {"id": 1, "deck": self.saludos, "ex": "x.lost", "new": True,
             "revlog": [{"type": 0, "ease": 3, "ivl": 1}, {"type": 4, "ease": 0, "ivl": 0}]},
            {"id": 2, "deck": self.saludos, "ex": "x.lost2", "new": True, "revlog": [{"type": 4, "ease": 0, "ivl": 0}]},
        ])
        _, out = self.run_with(fake, anki.orphans, [], True, False)
        self.assertEqual(sorted(fake.cards), [1])
        self.assertIn("no se borra: x.lost", out)

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
            self.assertEqual(anki.cmd_push(False, False, reset=True, phone_synced=True), 1)
        self.assertIn("fase de pruebas", out.getvalue())

    def test_push_refused_without_phone_sync(self):
        """Lotes 011 y 012: sin el «ya» de YAGO de que el móvil sincronizó, push no compila ni toca Anki."""
        def must_not_run(*a, **k):
            raise AssertionError("no debía llegar a compilar ni tocar Anki")
        with mock.patch.object(anki, "cmd_build", must_not_run), mock.patch.object(anki, "anki_request", must_not_run),                 redirect_stdout(io.StringIO()) as out:
            self.assertEqual(anki.cmd_push(False, True), 1)
        self.assertIn("--phone-synced", out.getvalue())

    def test_push_syncs_before_touching_cards(self):
        """Lo estudiado en el móvil baja antes de importar o reordenar: si no, la sincronización se quedaría con la
        tarjeta tocada aquí y se perdería el repaso."""
        calls = []
        def spy(action, timeout=120, **p):
            calls.append(action)
            if action == "sync":
                raise RuntimeError("sin red")
            raise AssertionError(f"no debía llegar a {action} sin haber sincronizado")
        with mock.patch.object(anki, "cmd_build", lambda *a: 0), mock.patch.object(anki, "anki_ready", lambda: True),                 mock.patch.object(anki, "anki_request", spy), redirect_stdout(io.StringIO()):
            self.assertEqual(anki.cmd_push(False, True, phone_synced=True), 1)
        self.assertEqual(calls, ["sync"])

    def test_reorder_new_leaves_well_placed_cards_alone(self):
        """Lote 008: mover una nueva la marca como modificada y, al sincronizar, pisa lo aprendido en el móvil sin
        sincronizar. Una segunda subida sin cambios no toca nada; una tarjeta nueva intercalada solo se mueve ella."""
        cards = [{"id": i, "deck": self.saludos, "ex": f"x.{i}", "new": True, "due": [3, 1, 2, 6, 4, 5][i - 1]}
                 for i in range(1, 7)]
        fake = FakeAnki(cards)
        order = {f"x.{i}": i for i in range(1, 7)}
        seen = []
        self.run_with(fake, anki.reorder_new, lambda pending: seen.append(pending) or order)   # desordenadas: renumera
        self.assertEqual(seen, [set(order)])                  # el orden se calcula con las que siguen nuevas
        dues = [fake.cards[i]["due"] for i in range(1, 7)]
        self.assertEqual(dues, [anki.NEW_DUE_GAP * k for k in range(1, 7)])
        fake.writes.clear()
        moved, _ = self.run_with(fake, anki.reorder_new, lambda pending: order)
        self.assertEqual((moved, fake.writes), (0, []))
        fake.cards[9] = {"id": 9, "deck": self.saludos, "ex": "x.new", "new": True, "due": 99999}
        order = {"x.1": 0, "x.2": 1, "x.3": 2, "x.new": 3, "x.4": 4, "x.5": 5, "x.6": 6}
        moved, _ = self.run_with(fake, anki.reorder_new, lambda pending: order)
        self.assertEqual((moved, fake.touched_cards()), (1, [9]))
        self.assertLess(fake.cards[3]["due"], fake.cards[9]["due"])
        self.assertLess(fake.cards[9]["due"], fake.cards[4]["due"])

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
