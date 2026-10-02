"""Pruebas de anki.py. Ejecutar: .\\.venv\\Scripts\\python -m unittest discover -s tests"""
import datetime
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import anki  # noqa: E402


class Pinyin(unittest.TestCase):
    def test_numeric_to_marked(self):
        for numeric, marked in [("ni3 hao3", "nǐ hǎo"), ("xie4 xie5", "xiè xie"), ("nv3", "nǚ"),
                                ("liu4", "liù"), ("gui4", "guì"), ("shen2 me", "shén me")]:
            self.assertEqual(anki.numeric_to_marked(numeric), marked)

    def test_tone_digits(self):
        self.assertEqual(anki.tones_to_numeric("什么", "25"), "shen2 me5")
        self.assertIsNone(anki.tones_to_numeric("什么", "2"))

    def test_syllables_and_erhua(self):
        self.assertEqual(anki.syllable_tones("你好", "nǐ hǎo"), [("ni", 3), ("hao", 3)])
        self.assertEqual(anki.syllable_tones("哪儿", "nǎr"), [("na", 3), ("r", "erhua")])
        self.assertEqual(anki.to_numeric("哪儿", "nǎr"), "nar3")
        self.assertEqual(anki.to_numeric("女儿", "nǚ'ér"), "nü3 er2")
        self.assertIsNone(anki.syllable_tones("你好", "nǐ"))

    def test_tone_traps(self):
        self.assertEqual(anki.tone_traps("什么", "shénme"), {"neutro"})
        self.assertEqual(anki.tone_traps("你好", "nǐ hǎo"), {"3+3"})
        self.assertIn("不/一", anki.tone_traps("不是", "bú shì"))
        self.assertEqual(anki.tone_traps("老师", "lǎoshī"), set())

    def test_ipa(self):
        self.assertEqual(anki.ipa("先生", "xiānsheng"), "ɕjɛn˥ ʂɤŋ")
        self.assertEqual(anki.ipa("哪儿", "nǎr"), "naɻ˧˩˧")

    def test_phonetic_traps(self):
        self.assertIn("x suena", anki.phonetic_notes("谢谢", "xièxie")[0])
        notes = anki.phonetic_notes("你是中国人吗", "nǐ shì Zhōngguó rén ma")
        self.assertEqual(len(notes), 3)
        self.assertEqual(len({n.split(":")[0] for n in notes}), 3, "una nota por sílaba distinta primero")

    def test_audio_rate(self):
        self.assertEqual(anki.audio_rate("上午"), anki.AZURE_RATE_WORD)
        self.assertEqual(anki.audio_rate("你好吗？"), anki.AZURE_RATE)


def word(iid, hanzi, pinyin, use="say", role="content", theme="saludos", kind="word"):
    return {"id": iid, "kind": kind, "hanzi": hanzi, "pinyin": pinyin, "use": use, "role": role, "theme": theme,
            "meaning": {"es": "prueba"}}


class Coverage(unittest.TestCase):
    def test_required_by_use(self):
        req = lambda it: anki.required_cards(it, {})
        self.assertEqual(req(word("w.a", "水", "shuǐ")), {"read", "listen", "produce"})
        self.assertEqual(req(word("w.b", "吗", "ma", role="function")), {"read", "listen", "produce-sentence"})
        self.assertEqual(req(word("w.c", "什么", "shénme", role="function")),
                         {"read", "listen", "produce-sentence", "tones"})
        self.assertEqual(req(word("w.d", "入口", "rùkǒu", use=["read"])), {"read"})
        self.assertEqual(req({"id": "s.a", "use": "say", "segments": []}), {"listen", "produce"})
        self.assertEqual(req({"id": "s.b", "use": "hear", "segments": []}), {"listen"})

    def test_tones_from_audio_count_as_listening(self):
        self.assertIn("listen", anki.satisfied({"type": "tones", "prompt": {"audio": True}}))
        self.assertNotIn("listen", anki.satisfied({"type": "tones", "prompt": {}}))

    def test_examples_respect_sense(self):
        at = {"id": "s.at", "use": "say", "segments": [{"text": "在", "ref": "w.zai.at"}]}
        prog = {"id": "s.prog", "use": "say", "segments": [{"text": "在", "ref": "w.zai.progressive"}]}
        sby = {"s.at": at, "s.prog": prog}
        ex = {"id": "x.read.zai.at", "type": "read", "targets": ["w.zai.at"]}
        self.assertEqual(anki.examples_for(ex, sby), ["s.at"])

    def test_scaffold_fills_what_plan_asks(self):
        entries, sentences, exercises = anki.load()
        new = word("w.test.pengyou", "朋友", "péngyou", theme="personas")
        new["accept_pinyin_mismatch"] = "prueba"
        entries = entries + [new]
        made, manual = anki.scaffold_exercises(entries, sentences, exercises, datetime.date(2026, 1, 1))
        types = sorted(ex["type"] for _, ex in made)
        self.assertEqual(types, ["listen", "produce", "read", "tones"])
        self.assertEqual(manual, [])
        listen = next(ex for _, ex in made if ex["type"] == "listen")
        self.assertEqual(listen["answer"].get("typed"), "peng2 you5")        # lo que se oye se escribe
        base = anki.baseline_exercises()
        if base:
            self.assertFalse({ex["id"] for _, ex in made} & set(base[1]))   # nunca un ID del último lote
        written = [ex | {"theme": theme} for theme, ex in made]   # al escribirlos, su tema es su archivo
        errors, _ = anki.validate(entries, sentences, exercises + written, require_audio=False)
        self.assertEqual([e for e in errors if "w.test" in e], [])


class Comments(unittest.TestCase):
    def test_informal_notes_are_flagged(self):
        for text in ["use paper to practice!", "formal / general ♡", "zǎo ← zǎoshang hǎo.", "Mi profesión"]:
            self.assertIsNotNone(anki.comment_style({"kind": "note", "text": text}), text)
        for text in ["Para practicar, pon una hoja de papel delante de la boca.", "¿Y tú?", "Mi profesión."]:
            self.assertIsNone(anki.comment_style({"kind": "note", "text": text}), text)
        self.assertIsNone(anki.comment_style({"kind": "sound", "text": "xiEnshAng"}))

    def test_repository_notes_are_clean(self):
        entries, sentences, exercises = anki.load()
        dirty = [(it["id"], c["text"]) for it in entries + sentences + exercises for c in it.get("comments", [])
                 if anki.comment_style(c)]
        self.assertEqual(dirty, [])


class Quality(unittest.TestCase):
    """Reglas de calidad deterministas (anki.quality_rules y compañía)."""

    def run_rules(self, entries=(), sentences=(), exercises=()):
        errors, warnings = [], []
        eby = {e["id"]: e for e in entries}
        sby = {s["id"]: s for s in sentences}
        anki.quality_rules(list(entries), list(sentences), list(exercises), eby, sby, errors, warnings)
        return errors, warnings

    def test_cross_level_words_in_notes_need_a_mark(self):
        levels = anki.hsk_levels()
        self.assertEqual(anki.unmarked_levels("Hablando basta 没错.", 1, set(), levels), ["没错 [HSK 4]"])
        self.assertEqual(anki.unmarked_levels("Hablando, 没错 [HSK 4].", 1, set(), levels), [])
        self.assertEqual(anki.unmarked_levels("两个人 «dos personas».", 1, {"两", "个", "人"}, levels), [])
        self.assertEqual(anki.unmarked_levels("En 迎 hay una sonrisa.", 1, set(), levels), [])   # un hanzi suelto es una pieza

    def test_entries_need_a_level(self):
        e = word("w.test.x", "伍", "wǔ")          # no está en la lista del HSK
        errors, _ = self.run_rules([e])
        self.assertTrue(any("sin nivel" in x for x in errors))
        errors, _ = self.run_rules([{**e, "level": 2, "level_reason": "prueba"}])
        self.assertFalse(any("sin nivel" in x for x in errors))

    def test_character_status_and_components(self):
        errors, _ = self.run_rules([{"id": "c.test.a", "kind": "character", "hanzi": "师", "pinyin": "shī", "use": "read"}])
        self.assertTrue(any("standalone" in x for x in errors))
        errors, _ = self.run_rules([{"id": "c.test.b", "kind": "component", "hanzi": "扌", "pinyin": "shǒu", "use": "say",
                                     "level": 1, "level_reason": "prueba"}])
        self.assertTrue(any("componente no se oye" in x for x in errors))
        mouth = {"id": "c.test.c", "kind": "component", "hanzi": "口", "pinyin": "kǒu", "use": "read"}
        errors, _ = self.run_rules([mouth])                 # 口 también es palabra (HSK 1): no puede decir que no lo es
        self.assertTrue(any("también es palabra" in x for x in errors))
        errors, _ = self.run_rules([{**mouth, "as_word": {"es": "boca"}}])
        self.assertFalse(any("también es palabra" in x for x in errors))
        self.assertIn("Suelto también es palabra: 口 kǒu «boca»", anki.status_text({**mouth, "as_word": {"es": "boca"}}))

    def test_word_listening_and_production_are_typed(self):
        e = word("w.test.y", "你", "nǐ")
        x = {"id": "x.test.listen", "type": "listen", "targets": ["w.test.y"], "answer": {"hanzi": "你"}}
        errors, _ = self.run_rules([e], exercises=[x])
        self.assertTrue(any("sin respuesta escrita" in m for m in errors))

    def test_sentences_link_every_chinese_piece(self):
        s = {"id": "s.test", "segments": [{"text": "大卫"}, {"text": "。"}]}
        errors, _ = self.run_rules(sentences=[s])
        self.assertTrue(any("no enlaza" in m for m in errors))

    def test_cloze_sentence_is_chosen_by_rule(self):
        entries, sentences, exercises = anki.load()
        eby, sby = {e["id"]: e for e in entries}, {s["id"]: s for s in sentences}
        used = {x["sentence"] for x in exercises if x.get("type") == "cloze"}
        cands = [s["id"] for s in sentences if any(g.get("ref") == "w.le" for g in s["segments"])]
        pick = anki.cloze_sentence("w.le", cands, sby, eby, exercises)
        free = [c for c in cands if c not in used]
        if free:
            self.assertNotIn(pick, used)


class Repository(unittest.TestCase):
    def test_current_data_is_valid(self):
        errors, _ = anki.validate(*anki.load(), require_audio=True)
        self.assertEqual(errors, [])

    def test_themes_are_well_formed(self):
        for t in anki.load_themes():
            self.assertTrue({"id", "title"} <= set(t) <= {"id", "title", "keep"}, t)

    def test_export_is_public_only(self):
        entries, sentences, exercises = anki.load()
        data = anki.export_dictionary(entries, sentences, exercises)
        self.assertEqual(data["schemaVersion"], anki.EXPORT_SCHEMA)
        text = json.dumps(data, ensure_ascii=False)
        self.assertNotIn('"private"', text)
        self.assertNotIn("x.", " ".join(e["id"] for e in data["entries"]))     # nada de ejercicios
        private = [c["text"] for e in entries for c in e.get("comments", []) if c.get("private", True) is not False]
        for t in private:
            self.assertNotIn(t, text)
        for e in data["entries"]:
            if e.get("audio"):
                self.assertTrue((anki.ROOT / e["audio"]).exists(), e["audio"])
        self.assertEqual(len(data["cards"]), len(exercises))
        self.assertEqual(data["cardCss"], anki.CSS.strip())
        for slot in anki.SLOTS:                                            # cada hueco tiene su color
            self.assertIn(f".slot-{slot} ", data["cardCss"])
        for c in data["cards"]:
            html = c["front"] + c["back"] + c["notes"]
            self.assertNotIn("[sound:", html)
            for path in re.findall(r'data-audio="([^"]+)"', html):
                self.assertTrue((anki.ROOT / path).exists(), path)
        # Lo que la web ya no deriva: tipo de entrada, lista del HSK, conexiones y qué entrena y enseña cada tarjeta.
        by = {e["id"]: e for e in data["entries"]}
        ids = set(by) | {s["id"] for s in data["sentences"]}
        types = {"word", "charword", "bound", "component", "expression", "structure", "pronunciation"}
        self.assertTrue(all(e["entryType"] in types for e in data["entries"]))
        self.assertEqual((by["w.laoshi"]["entryType"], by["w.wo"]["entryType"]), ("word", "charword"))
        self.assertEqual(by["st.hen-adj"]["entryType"], "structure")
        self.assertFalse(by["st.hen-adj"]["levelEstimated"])
        self.assertIsNone(by["st.hen-adj"]["onHskList"])
        self.assertTrue(by["w.laoshi"]["onHskList"])
        self.assertEqual(by["w.ben"]["connection"]["with"], ["本"])
        for c in data["cards"]:
            self.assertTrue(c["targets"] and set(c["targets"] + c["examples"]) <= ids, c["id"])

    def test_part_of_speech(self):
        w = lambda h, **k: {"id": "w.t", "kind": "word", "hanzi": h, **k}
        self.assertEqual(anki.pos_of(w("我")), "pronombre")
        self.assertEqual(anki.pos_of(w("个")), "clasificador")
        self.assertEqual(anki.pos_of(w("什么")), "interrogativo")          # la lista lo da como pronombre
        self.assertEqual(anki.pos_of(w("对", pos="adjetivo")), "adjetivo")
        self.assertEqual(anki.pos_of({"kind": "expression", "hanzi": "你好"}), "expresion")
        self.assertIsNone(anki.pos_of({"kind": "character", "hanzi": "们"}))
        e = w("对", pos="adjetivo")
        errors, warnings = [], []
        anki.grammar_rules([e], [], {"w.t": e}, {}, errors, warnings)
        self.assertTrue(any("pos_reason" in m for m in warnings))

    def test_structures(self):
        self.assertEqual(anki.pattern_tokens("{S} + 很 + {Adj}"), [("slot", "S"), ("fixed", "很"), ("slot", "Adj")])
        self.assertEqual(anki.pattern_tokens("{S} + {Adj} + 吗？")[-2:], [("fixed", "吗"), ("punct", "？")])
        words = [{"id": "w.ta", "kind": "word", "hanzi": "他", "pinyin": "tā"},
                 {"id": "w.hen", "kind": "word", "hanzi": "很", "pinyin": "hěn"},
                 {"id": "w.gao", "kind": "word", "hanzi": "高", "pinyin": "gāo"},
                 {"id": "w.pengyou", "kind": "word", "hanzi": "朋友", "pinyin": "péngyou"}]
        seg = lambda *ids: {"segments": [{"text": i, "ref": i} for i in ids]}
        good = {"id": "s.good", **seg("w.ta", "w.hen", "w.gao")}
        odd = {"id": "s.odd", **seg("w.ta", "w.hen", "w.pengyou")}
        st = {"id": "st.t", "kind": "structure", "pattern": "{S} + 很 + {Adj}", "refs": ["w.hen"],
              "meaning": {"es": "describir"}, "examples": ["s.good"]}
        errors, warnings = [], []
        anki.grammar_rules(words + [st], [good], {e["id"]: e for e in words + [st]}, {"s.good": good}, errors, warnings)
        self.assertEqual((errors, warnings), ([], []))
        errors, warnings = [], []
        bad = {**st, "examples": ["s.odd"]}
        anki.grammar_rules(words + [bad], [odd], {e["id"]: e for e in words + [bad]}, {"s.odd": odd}, errors, warnings)
        self.assertTrue(any("ocupa el hueco" in m for m in warnings))        # 朋友 no es un adjetivo
        errors, warnings = [], []
        anki.grammar_rules(words + [{**st, "refs": []}], [good], {e["id"]: e for e in words}, {"s.good": good}, errors, warnings)
        self.assertTrue(any("refs deben ser" in m for m in errors))

    def test_structure_cards_oppose_a_calque(self):
        """Una estructura se practica frente a su calco erróneo, nunca con «di una frase» (YAGO, 2026-10-01)."""
        words = [{"id": "w.ta", "kind": "word", "hanzi": "他", "pinyin": "tā"},
                 {"id": "w.hen", "kind": "word", "hanzi": "很", "pinyin": "hěn"},
                 {"id": "w.gao", "kind": "word", "hanzi": "高", "pinyin": "gāo"}]
        good = {"id": "s.good", "use": "say", "theme": "describir", "translation": {"es": "Él es alto."},
                "segments": [{"text": "他", "ref": "w.ta", "pinyin": "tā"}, {"text": "很", "ref": "w.hen", "pinyin": "hěn"},
                             {"text": "高", "ref": "w.gao", "pinyin": "gāo"}, {"text": "。"}]}
        st = {"id": "st.t", "kind": "structure", "use": "say", "theme": "estructuras", "pattern": "{S} + 很 + {Adj}",
              "refs": ["w.hen"], "meaning": {"es": "describir"}, "examples": ["s.good"]}

        def errors_for(s):
            errors, warnings = [], []
            anki.grammar_rules(words + [s], [good], {e["id"]: e for e in words + [s]}, {"s.good": good}, errors, warnings)
            return errors
        self.assertTrue(any("falta contrast" in m for m in errors_for(st)))
        same = {**st, "contrast": {"right": "s.good", "wrong": "他很高。", "why": {"es": "x"}}}
        self.assertTrue(any("igual que la frase buena" in m for m in errors_for(same)))
        ok = {**st, "contrast": {"right": "s.good", "wrong": "他是高。", "why": {"es": "Sin 是."}}}
        self.assertEqual(errors_for(ok), [])
        made, _ = anki.scaffold_exercises(words + [ok], [good], [], datetime.date(2026, 10, 1))
        cards = [ex for _, ex in made if ex["type"] == "pattern"]
        self.assertEqual(len(cards), 1)
        self.assertTrue(cards[0]["id"].startswith("x.calque."))
        self.assertEqual(cards[0]["sentence"], "s.good")
        self.assertNotIn("Di una frase", cards[0]["prompt"]["text"])
        options = [hz for hz, _ in anki.calque_options(cards[0], ok, {"s.good": good})]
        self.assertEqual(sorted(options), sorted(["他是高。", "他很高。"]))

    def test_standard_mandarin_and_soundalikes(self):
        """Nada de erhua; aviso de palabras que suenan igual sin contrastar; los parecidos al oído se contrastan
        oyendo (YAGO, 2026-10-01)."""
        nar = {"id": "w.t.nar", "kind": "word", "hanzi": "哪儿", "pinyin": "nǎr", "use": "hear"}
        self.assertTrue(anki.is_erhua(nar))
        self.assertFalse(anki.is_erhua({"hanzi": "女儿", "pinyin": "nǚ'ér"}))
        shi = {"id": "w.t.shi", "kind": "word", "hanzi": "是", "pinyin": "shì", "use": "say", "theme": "presentarse"}
        ten = {"id": "w.t.ten", "kind": "word", "hanzi": "十", "pinyin": "shí", "use": "say", "theme": "numeros"}
        sent = {"id": "s.t", "segments": [{"text": "哪儿", "ref": "w.t.nar"}]}

        def run(entries, sentences=()):
            errors, warnings = [], []
            anki.standard_rules(entries, list(sentences), {e["id"]: e for e in entries}, errors, warnings)
            return errors, warnings
        errors, _ = run([nar])
        self.assertTrue(any("erhua" in m for m in errors))
        errors, _ = run([{**nar, "use": "drop"}], [sent])
        self.assertTrue(any("descartada" in m for m in errors))
        _, warnings = run([shi, ten])
        self.assertTrue(any("suenan igual" in m for m in warnings))
        grp = {"id": "g.t", "kind": "group", "basis": "soundalike", "theme": "presentarse",
               "members": [{"ref": "w.t.shi", "cue": "ser"}, {"ref": "w.t.ten", "cue": "diez"}]}
        _, warnings = run([shi, ten, grp])
        self.assertEqual(warnings, [])
        made, _ = anki.scaffold_exercises([shi, ten, grp], [], [], datetime.date(2026, 10, 1))
        contrast = [ex for _, ex in made if ex["type"] == "contrast"]
        self.assertEqual(len(contrast), 2)
        self.assertTrue(all(ex["prompt"].get("audio") for ex in contrast))      # se oye y se elige
        self.assertTrue(anki.wants_audio(contrast[0], {"g.t": grp}))

    def test_confusable_partner_appears_in_examples(self):
        yao = {"id": "w.t.yao", "kind": "word", "hanzi": "要", "pinyin": "yào"}
        ai = {"id": "w.t.ai", "kind": "word", "hanzi": "爱", "pinyin": "ài"}
        grp = {"id": "g.t", "kind": "group", "basis": "set", "members": [{"ref": "w.t.yao"}, {"ref": "w.t.ai"}]}
        sby = {f"s.y{i}": {"id": f"s.y{i}", "use": "say", "segments": [{"text": "要", "ref": "w.t.yao"}]} for i in range(3)}
        sby["s.a"] = {"id": "s.a", "use": "say", "segments": [{"text": "爱", "ref": "w.t.ai"}]}
        eby = {e["id"]: e for e in (yao, ai, grp)}
        ex = {"id": "x.t", "type": "read", "targets": ["w.t.yao"]}
        out = anki.examples_for(ex, sby, eby)
        self.assertIn("s.a", out)
        self.assertEqual(len(out), anki.EXAMPLES_MAX)

    def test_whole_clause_slot(self):
        words = [{"id": "w.ru", "kind": "word", "hanzi": "如果", "pinyin": "rúguǒ"},
                 {"id": "w.ni", "kind": "word", "hanzi": "你", "pinyin": "nǐ"}]
        st = {"id": "st.t", "kind": "structure", "pattern": "如果 + {Frase}", "refs": ["w.ru"], "meaning": {"es": "si"},
              "examples": ["s.t"]}
        s = {"id": "s.t", "segments": [{"text": "如果", "ref": "w.ru"}, {"text": "你", "ref": "w.ni"}]}
        errors, warnings = [], []
        anki.grammar_rules(words + [st], [s], {e["id"]: e for e in words + [st]}, {"s.t": s}, errors, warnings)
        self.assertEqual((errors, warnings), ([], []))

    def test_hanzi_connections(self):
        """La conexión es del carácter, enlaza solo con lo que ya está en el mazo, y las series fonéticas sin
        contar se avisan (YAGO, 2026-10-01)."""
        self.assertEqual(anki.phonetic_of("请"), "青")                   # datos de sources/hanzi/
        men = {"id": "w.t.men", "kind": "word", "hanzi": "门", "pinyin": "mén", "use": "say"}
        wen = {"id": "w.t.wen", "kind": "word", "hanzi": "问", "pinyin": "wèn", "use": "say"}
        women = {"id": "w.t.women", "kind": "word", "hanzi": "我们", "pinyin": "wǒmen", "use": "say"}
        mens = {"id": "c.t.men", "kind": "character", "hanzi": "们", "pinyin": "men", "use": "context", "standalone": "no"}
        entries = [men, wen, women, mens]
        chars = anki.deck_chars(entries)
        self.assertEqual(sorted(anki.sound_family("门", "men", chars)), ["们", "问"])

        def run(es):
            errors, warnings = [], []
            anki.connection_rules(es, [], {e["id"]: e for e in es}, {}, errors, warnings)
            return errors, warnings
        _, warnings = run(entries)
        self.assertTrue(any("serie fonética" in m for m in warnings))
        told = {**men, "connection": {"kind": "sound", "with": ["们", "问"], "text": "门 da el sonido a 们 y a 问."}}
        self.assertEqual(run([told, wen, women, mens]), ([], []))
        bad = {**men, "connection": {"kind": "sound", "with": ["闻"], "text": "门 da el sonido a 闻."}}
        errors, _ = run([bad, wen, women, mens])
        self.assertTrue(any("no está en el mazo" in m for m in errors))
        # 我们 hereda la conexión de su carácter 们, si la tiene; una como mucho
        home = {**mens, "connection": {"kind": "sound", "with": ["门"], "text": "门 da el sonido a 们."}}
        self.assertIs(anki.connection_for(women, [men, wen, women, home]), home["connection"])
        self.assertIsNone(anki.connection_for(wen, [men, wen, women, mens]))

    def test_scaffold_appends_to_an_empty_list(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "exercises").mkdir()
            path = Path(tmp) / "exercises" / "vacio.yaml"
            path.write_text("# Ejercicios\n\nexercises: []\n", encoding="utf-8")
            with mock.patch.object(anki, "DATA", Path(tmp)):
                anki.append_exercises("vacio", [{"id": "x.t", "type": "read"}])
            self.assertEqual([x["id"] for x in anki.load_yaml(path)["exercises"]], ["x.t"])

    def test_attic_wakes_by_rule(self):
        gou = {"id": "a.gou", "hanzi": "狗", "links": ["猫", "动物"]}
        ri = {"id": "a.ri", "hanzi": "日", "links": ["星期"]}
        color = {"id": "a.huise", "hanzi": "灰色", "links": ["颜色"]}
        w = lambda h: {"hanzi": h}
        attic = [gou, ri, color]
        self.assertEqual(anki.attic_awake(attic, [w("小猫")]), [])            # 猫 suelto no despierta con 小猫
        self.assertEqual([a["id"] for a, _ in anki.attic_awake(attic, [w("猫")])], ["a.gou"])
        self.assertEqual([a["id"] for a, _ in anki.attic_awake(attic, [w("生日")])], ["a.ri"])
        self.assertEqual([a["id"] for a, _ in anki.attic_awake(attic, [w("颜色好看")])], ["a.huise"])
        self.assertEqual(anki.attic_awake([{**gou, "snooze": "003-x"}], [w("猫")], snoozed_for="003-x"), [])

    def test_attic_rules(self):
        base = {"id": "a.t", "hanzi": "狗", "pinyin": "gǒu", "meaning": {"es": "perro"}, "theme": "cosas",
                "links": ["猫"], "reason": "prueba", "source": {"batch": "x"}, "notes": []}
        errors, warnings = [], []
        anki.attic_rules([base], [], errors, warnings)
        self.assertEqual((errors, warnings), ([], []))
        errors, warnings = [], []
        anki.attic_rules([base, {**base, "id": "a.t2"}, {**base, "id": "a.t3", "hanzi": "猫", "links": []}],
                         [{"hanzi": "狗"}], errors, warnings)
        self.assertTrue(any("dos veces" in e for e in errors))
        self.assertTrue(any("sin links" in e for e in errors))
        self.assertTrue(any("ya está en el mazo" in w for w in warnings))

    def test_bound_character_takes_the_level_of_its_word(self):
        levels = anki.hsk_levels()
        ru = {"id": "c.t.ru", "kind": "character", "hanzi": "入", "pinyin": "rù", "standalone": "rare"}
        rukou = {"id": "w.t.rukou", "kind": "word", "hanzi": "入口", "pinyin": "rùkǒu"}
        self.assertEqual(anki.level_of("c.t.ru", {"c.t.ru": ru}, {}, levels), levels["入"])
        self.assertEqual(anki.level_of("c.t.ru", {"c.t.ru": ru, "w.t.rukou": rukou}, {}, levels), levels["入口"])

    def test_examples_never_come_from_a_higher_level(self):
        entries, sentences, exercises = anki.load()
        eby, sby, levels = {e["id"]: e for e in entries}, {s["id"]: s for s in sentences}, anki.hsk_levels()
        for ex in exercises:
            card = max([lv for lv in (anki.level_of(t, eby, sby, levels) for t in ex.get("targets", [])) if lv] or [0])
            if not card:
                continue
            for sid in anki.examples_for(ex, sby, eby):
                if sid in ex.get("reveal", []):
                    continue
                self.assertLessEqual(anki.level_of(sid, eby, sby, levels) or 0, card, (ex["id"], sid))

    def test_history_cache_gives_the_same_days(self):
        entries, sentences, exercises = anki.load()
        level = lambda x: None
        full, cache = anki.deck_history(exercises, level)
        again, cache2 = anki.deck_history(exercises, level, cache)
        self.assertEqual(full, again)
        self.assertEqual(cache, cache2)

    def test_close_batch_rejects_bad_names(self):
        _, errors = anki.close_batch_plan("2-foo")
        self.assertTrue(errors)

    def test_close_batch_keeps_class_recordings_out_of_git(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            inbox, audio = Path(tmp) / "inbox", Path(tmp) / "class-audio"
            inbox.mkdir()
            (inbox / "clase.m4a").write_bytes(b"")
            with mock.patch.object(anki, "INBOX", inbox), mock.patch.object(anki, "HISTORY", inbox / "history"),                     mock.patch.object(anki, "CLASS_AUDIO", audio):
                _, errors = anki.close_batch_plan("999-2026-01-01-prueba")
                self.assertTrue(any("sin transcribir" in e for e in errors))
                (audio / "clase").mkdir(parents=True)
                (audio / "clase" / "transcript.md").write_text("x", encoding="utf-8")
                actions, _ = anki.close_batch_plan("999-2026-01-01-prueba")
            dest = [dst for _, src, dst in actions if src.name == "clase.m4a"]
            self.assertEqual(dest, [audio / "clase" / "clase.m4a"])

    def test_reading_comprehension(self):
        entries, sentences, _ = anki.load()
        eby, sby = {e["id"]: e for e in entries}, {s["id"]: s for s in sentences}
        text = ["s.beijing-hen-re", "s.beijing-hen-da", "s.mingtian-hui-xiayu"]
        ok = {"id": "x.comprehension.t", "type": "comprehension", "targets": text, "script": "hanzi",
              "question": {"sentence": "s.beijing-xiayu-ma"}, "answer": {"meaning": "Mañana."}}
        def run(ex):
            errors, warnings = [], []
            anki.comprehension_rules(ex, eby, sby, errors, warnings)
            return errors
        self.assertEqual(run(ok), [])
        self.assertTrue(run({**ok, "targets": text[:1]}))                       # una frase sola no es un texto
        self.assertTrue(run({**ok, "targets": text + ["w.ta"]}))                 # solo frases
        self.assertTrue(run({**ok, "script": "pinyin"}))                         # nunca pinyin solo
        self.assertTrue(run({**ok, "question": {}}))
        self.assertTrue(run({**ok, "answer": {}}))
        self.assertEqual(anki.satisfied(ok), {"comprehension"})                  # no cubre la escucha de sus frases
        f = anki.card_fields({**ok, "lang": "es", "prompt": {"text": "Lee."}}, eby, sby, {}, set())
        front = f["front"]
        self.assertIn("北京很热。北京很大。明天会下雨。", front)                   # un párrafo, en hanzi
        self.assertNotIn("Běijīng", front)                                       # sin pinyin delante
        self.assertLess(front.index("passage"), front.index("<details"))         # la pregunta, plegada, después
        self.assertIn("Běijīng", f["back"])                                      # el pinyin, al girar
        both = anki.card_fields({**ok, "script": "both", "lang": "es", "prompt": {"text": "Lee."}}, eby, sby, {}, set())
        self.assertIn("Běijīng", both["front"])

    def test_markdown_anchors_like_github(self):
        self.assertEqual(anki.md_slug("✅ Entró, con matices para ahondar"), "-entró-con-matices-para-ahondar")
        self.assertEqual(anki.md_slug("Cómo vas"), "cómo-vas")
        self.assertEqual(anki.md_anchors("## A\n## A\n```\n## no\n```"), {"a", "a-1"})

    def test_review_starts_with_what_must_be_answered(self):
        log = "/2-digests/summary-003-2026-10-01-comer-dinero-y-contrastes.md"
        ok = (f"# Review\n\n{anki.SINE_QUA_NON}\n\n- ¿Es 行 háng o xíng? ([detalle](#por-verificar))\n  > \n"
              f"- ¿Entra 茶? ([log]({log}#cambios-en-el-sistema))\n  > \n\n## Por verificar\n\n- 行\n  > \n")
        self.assertEqual(anki.review_rules("004-x", ok), [])
        self.assertEqual(anki.review_rules("004-x", f"# R\n\n{anki.SINE_QUA_NON}\n\n- (nada)\n"), [])
        def errs(text):
            return " ".join(anki.review_rules("004-x", text))
        self.assertIn("primer apartado", errs("# R\n\n## Cómo vas\n\n" + anki.SINE_QUA_NON + "\n- (nada)\n"))
        self.assertIn("vacío", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\ntexto\n"))
        self.assertIn("enlace", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\n- ¿Algo?\n  > \n"))
        self.assertIn("«>»", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\n- ¿Algo? ([x](#r))\n"))
        many = "".join(f"- ¿{i}? ([x](#r))\n  > \n" for i in range(anki.SINE_QUA_NON_MAX + 1))
        self.assertIn("como mucho", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\n{many}"))
        self.assertIn("no existe", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\n- ¿A? ([x](#nada-de-esto))\n  > \n"))
        self.assertIn("no existe", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\n- ¿A? ([x]({log}#inventado))\n  > \n"))
        self.assertIn("desde la raíz", errs(f"# R\n\n{anki.SINE_QUA_NON}\n\n- ¿A? ([x](../2-digests/a.md))\n  > \n"))

    def test_state_is_current_and_every_point_has_its_source(self):
        batch = "003-2026-10-01-comer-dinero-y-contrastes"
        log = f"/2-digests/summary-{batch}.md#seguimiento"
        body = "".join(f"{s}\n\n- Algo cierto ([lote 003]({log})).\n\n" for s in anki.STATE_SECTIONS)
        good = f"{anki.STATE_HEADER}\n\n# Estado tras el lote {batch}\n\n{body}"
        self.assertEqual(anki.state_rules(batch, good), [])
        self.assertTrue(any("al día" in e for e in anki.state_rules("004-2026-10-08-otro", good)))
        self.assertTrue(any("necesita el enlace" in e for e in anki.state_rules(batch, good.replace(f" ([lote 003]({log}))", "", 1))))
        moving = good.replace(log, f"/1-inbox/review-{batch}.md", 1)
        self.assertTrue(any("se mueve" in e for e in anki.state_rules(batch, moving)))
        self.assertTrue(any("falta el apartado" in e for e in anki.state_rules(batch, good.replace("## Tu método", "## Otro"))))

    def test_close_batch_asks_for_frictions_review_and_state(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        batch = "999-2026-01-01-prueba"
        with tempfile.TemporaryDirectory() as tmp:
            inbox, digests = Path(tmp) / "inbox", Path(tmp) / "digests"
            inbox.mkdir(); digests.mkdir()
            (digests / f"summary-{batch}.md").write_text(anki.LOG_HEADER + "\n\n# Log\n", encoding="utf-8")
            (inbox / f"review-{batch}.md").write_text("# Review\n\n## Cómo vas\n", encoding="utf-8")
            with mock.patch.object(anki, "INBOX", inbox), mock.patch.object(anki, "DIGESTS", digests), \
                    mock.patch.object(anki, "STATE", digests / "state.md"):
                _, errors = anki.close_batch_plan(batch)
        text = " ".join(errors)
        self.assertIn("Fricciones del proceso", text)
        self.assertIn("Sine qua non", text)
        self.assertIn("state.md", text)

    def test_blackbox_writes_only_where_private_exists(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            box = Path(tmp) / "private" / "blackbox.jsonl"
            with mock.patch.object(anki, "BLACKBOX", box), mock.patch.dict("os.environ", {"ANKI_NO_BLACKBOX": ""}):
                anki.blackbox(["check"], 0, 1.0)
                self.assertFalse(box.exists())                 # sin private/ (CI, un fork): nada
                box.parent.mkdir()
                anki._RUN.update(errors=[], warnings=["w"])
                anki.blackbox(["check"], 0, 1.0)
                rec = json.loads(box.read_text(encoding="utf-8"))
        self.assertEqual((rec["argv"], rec["rc"], rec["warnings"]), (["check"], 0, ["w"]))

    def test_retro_reads_frictions_and_repeated_warnings(self):
        logs = [("004-2026-10-08-a", f"# L\n\n{anki.FRICTIONS}\n\n- check tardó mucho.\n\n## Otra\n"),
                ("005-2026-10-15-b", "# L\n")]
        rows = [{"ts": "2026-10-08", "argv": ["check"], "rc": 0, "s": 2, "warnings": ["tema largo"]}] * 3 + \
               [{"ts": "2026-10-09", "argv": ["push"], "rc": 1, "s": 9, "exc": "RuntimeError: x"}]
        out = "\n".join(anki.retro_report(logs, rows))
        self.assertIn("check tardó mucho", out)
        self.assertIn("sin apartado", out)
        self.assertIn("3 × tema largo", out)
        self.assertIn("1 fallida", out)
        self.assertIn("RuntimeError", out)

    def test_stats_groups_failures_by_entry(self):
        day = 86_400_000
        now = 100 * day
        exercises = [{"id": "x.a", "type": "listen", "targets": ["w.a"]}, {"id": "x.b", "type": "read", "targets": ["w.b"]}]
        eby = {"w.a": {"hanzi": "他", "pinyin": "tā", "meaning": {"es": "él"}},
               "w.b": {"hanzi": "她", "pinyin": "tā", "meaning": {"es": "ella"}}}
        infos = [{"cardId": 1, "lapses": 5, "fields": {"ExerciseID": {"value": "x.a"}}},
                 {"cardId": 2, "lapses": 0, "fields": {"ExerciseID": {"value": "x.b"}}},
                 {"cardId": 3, "lapses": 0, "fields": {"ExerciseID": {"value": "x.ajena"}}}]
        revs = {"1": [{"id": now - day, "ease": 1, "type": 1}, {"id": now - day, "ease": 1, "type": 2},
                      {"id": now - 2 * day, "ease": 0, "type": 4},           # reinicio manual: no cuenta
                      {"id": now - 90 * day, "ease": 1, "type": 1}],         # fuera del periodo
                "2": [{"id": now - day, "ease": 3, "type": 1}], "3": [{"id": now - day, "ease": 1, "type": 1}]}
        out = "\n".join(anki.stats_report(infos, revs, exercises, eby, 30, now))
        self.assertIn("3 repasos de 2 tarjeta(s)", out)
        self.assertIn("Retención (solo repasos de tarjetas ya aprendidas): 50 %", out)
        self.assertIn("67 %", out)
        self.assertIn("w.a 他 tā · él — 2/2 · Escuchar", out)
        self.assertNotIn("w.b 她", out.split("Lo que más cuesta")[1].split("Olvidadas")[0])
        self.assertIn("x.a · 5 lapsos", out)


@unittest.skipUnless(shutil.which("node"), "sin node: no se prueba el JavaScript de las tarjetas")
class CardJavaScript(unittest.TestCase):
    """La comparación de respuestas escritas que corre dentro de Anki."""

    def test_normalized_comparison(self):
        js = anki.INPUT_JS_BACK.replace("<script>", "").replace("</script>", "")
        js = js.replace("setTimeout(function () {", "function run() {").replace("}, 0);", "}")
        cases = [("ni3 hao3", "你好", "ni3hao3", True), ("ni3 hao3", "你好", "Nǐ hǎo", True),
                 ("ni3 hao3", "你好", "ni hao", False), ("ni3 hao3", "你好", "ni2 hao3", False),
                 ("xie4 xie5", "谢谢", "xiè xie", True), ("nv3 er2", "女儿", "nǚ'ér", True),
                 ("25", "什么", "2 5", True), ("25", "什么", "24", False), ("bu4", "不", "不", True),
                 ("hěn gāoxìng rènshi nǐ", "很高兴认识你。", "很高兴认识你！", True),
                 ("hěn gāoxìng rènshi nǐ", "很高兴认识你。", "很高兴认识他", False)]
        harness = ("var store = {}, els = {};\n"
                   "var sessionStorage = {getItem: function (k) { return k in store ? store[k] : null; }};\n"
                   "var document = {getElementById: function (id) { return els[id] || null; }};\n" + js + "\n"
                   "var out = [];\n"
                   f"{json.dumps(cases, ensure_ascii=False)}.forEach(function (c) {{\n"
                   "  store = {'acs-typed': c[2]};\n"
                   "  els = {'acs-result': {className: '', textContent: ''}, 'acs-exp-py': {textContent: c[0]},"
                   " 'acs-exp-hz': {textContent: c[1]}};\n"
                   "  run(); out.push(els['acs-result'].className === 'acs-ok');\n"
                   "});\nconsole.log(JSON.stringify(out));\n")
        result = subprocess.run(["node", "-e", harness], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [c[3] for c in cases])


if __name__ == "__main__":
    unittest.main()
