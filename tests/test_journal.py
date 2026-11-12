"""journal.py tests: add, result, R multiples under both management styles, stats."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _load import SCRIPTS

JOURNAL = os.path.join(SCRIPTS, "journal.py")


class Journal(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.file = os.path.join(self.dir, "journal.csv")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_j(self, *args):
        p = subprocess.run([sys.executable, JOURNAL, "--file", self.file, *map(str, args)],
                           capture_output=True, text=True, encoding="utf-8")
        return p.returncode, p.stdout, p.stderr

    def add(self, side, entry=None, sl=None, tp1=None, tp2=None, **kw):
        args = ["add", "--asset", kw.get("asset", "EURUSD"), "--tf", kw.get("tf", "15m"), "--side", side,
                "--setup", kw.get("setup", "pullback"), "--date", "2026-11-12"]
        for k, v in (("entry", entry), ("sl", sl), ("tp1", tp1), ("tp2", tp2), ("confidence", kw.get("conf"))):
            if v is not None:
                args += [f"--{k}", v]
        return self.run_j(*args)

    def stats(self, *extra):
        code, out, _ = self.run_j("stats", "--json", *extra)
        self.assertEqual(code, 0)
        return json.loads(out)

    def test_add_and_list(self):
        code, out, _ = self.add("short", 1.0850, 1.0870, 1.0810, 1.0790, conf=3)
        self.assertEqual(code, 0)
        self.assertIn("#1", out)
        code, out, _ = self.add("none", setup="range")
        self.assertIn("#2", out)
        self.assertIn("PAS DE TRADE", out)
        code, out, _ = self.run_j("list")
        self.assertIn("EURUSD", out)
        self.assertIn("PAS DE TRADE", out)

    def test_refuses_bad_levels(self):
        self.assertEqual(self.add("long", 100, 101, 105)[0], 1)
        self.assertEqual(self.add("long", 100, 98, 99)[0], 1)
        self.assertEqual(self.add("long", 100, 98, 104, 103)[0], 1)  # TP2 before TP1
        self.assertEqual(self.add("long", 100)[0], 1)  # missing stop
        self.assertFalse(os.path.exists(self.file))

    def test_r_multiples_both_managements(self):
        # long 100 / 98 / TP1 104 (2R) / TP2 106 (3R)
        for outcome in ("sl", "tp1", "tp2", "be"):
            self.add("long", 100, 98, 104, 106)
        for i, outcome in enumerate(("sl", "tp1", "tp2", "be"), 1):
            self.assertEqual(self.run_j("result", i, "--outcome", outcome)[0], 0)
        s = self.stats()["global"]
        self.assertEqual(s["closed"], 4)
        # tout à TP1 : -1, 2, 2, 0
        self.assertAlmostEqual(s["tp1"]["total_r"], 3.0)
        self.assertAlmostEqual(s["tp1"]["win_rate"], 50.0)
        # moitié : -1, 1, 2.5, 0
        self.assertAlmostEqual(s["split"]["total_r"], 2.5)
        self.assertAlmostEqual(s["tp1"]["profit_factor"], 4.0)

    def test_short_exit_price(self):
        self.add("short", 28295, 28375, 28150, 28100)
        code, out, _ = self.run_j("result", 1, "--outcome", "exit", "--exit", 28255)
        self.assertEqual(code, 0)
        self.assertIn("+0.50R", out)
        self.assertEqual(self.run_j("result", 1, "--outcome", "exit")[0], 1)  # needs --exit

    def test_nofill_open_and_no_trade_excluded(self):
        self.add("long", 100, 98, 104)
        self.add("long", 100, 98, 104)
        self.add("none")
        self.add("long", 100, 98, 104)
        self.run_j("result", 1, "--outcome", "nofill")
        self.run_j("result", 2, "--outcome", "sl")
        s = self.stats()["global"]
        self.assertEqual((s["signals"], s["no_trade"], s["nofill"], s["open"], s["closed"]), (4, 1, 1, 1, 1))
        self.assertEqual(self.run_j("result", 3, "--outcome", "sl")[0], 1)  # PAS DE TRADE has no result

    def test_tp2_requires_tp2(self):
        self.add("long", 100, 98, 104)
        self.assertEqual(self.run_j("result", 1, "--outcome", "tp2")[0], 1)

    def test_unknown_id(self):
        self.assertEqual(self.run_j("result", 9, "--outcome", "sl")[0], 1)

    def test_stats_by_confidence_and_streak(self):
        for _ in range(3):
            self.add("long", 100, 98, 104, conf=2)
        self.add("long", 100, 98, 104, conf=4)
        for i in (1, 2, 3):
            self.run_j("result", i, "--outcome", "sl")
        self.run_j("result", 4, "--outcome", "tp1")
        s = self.stats("--by", "confidence")
        self.assertEqual(s["2"]["tp1"]["max_losing_streak"], 3)
        self.assertIsNone(s["2"]["tp1"]["profit_factor"] if s["2"]["tp1"]["win_rate"] else None)
        self.assertAlmostEqual(s["4"]["tp1"]["avg_r"], 2.0)

    def test_small_sample_note(self):
        self.add("long", 100, 98, 104)
        self.run_j("result", 1, "--outcome", "tp1")
        _, out, _ = self.run_j("stats")
        self.assertIn("moins de 30", out)

    def test_empty(self):
        code, out, _ = self.run_j("stats")
        self.assertEqual(code, 0)
        self.assertIn("vide", out)


if __name__ == "__main__":
    unittest.main()
