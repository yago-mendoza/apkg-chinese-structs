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
        for c in data["cards"]:
            html = c["front"] + c["back"] + c["notes"]
            self.assertNotIn("[sound:", html)
            for path in re.findall(r'data-audio="([^"]+)"', html):
                self.assertTrue((anki.ROOT / path).exists(), path)

    def test_close_batch_rejects_bad_names(self):
        _, errors = anki.close_batch_plan("2-foo")
        self.assertTrue(errors)


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
