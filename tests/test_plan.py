"""plan.py tests: side checks, R:R, minimum R:R, better limit entry, sizing."""

import json
import os
import subprocess
import sys
import unittest

from _load import SCRIPTS

PLAN = os.path.join(SCRIPTS, "plan.py")


def run(*args):
    p = subprocess.run([sys.executable, PLAN, *map(str, args), "--json"],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (json.loads(p.stdout) if p.stdout.strip().startswith("{") else None), p.stderr


class Plan(unittest.TestCase):
    def test_short_valid(self):
        code, r, _ = run("--side", "short", "--entry", 28295, "--sl", 28375, "--tp", 28150, 28100)
        self.assertEqual(code, 0)
        self.assertTrue(r["valid"])
        self.assertAlmostEqual(r["risk_per_unit"], 80)
        self.assertAlmostEqual(r["targets"][0]["rr"], 145 / 80)
        self.assertAlmostEqual(r["targets"][1]["rr"], 195 / 80)

    def test_long_valid_and_sell_buy_aliases(self):
        code, r, _ = run("--side", "buy", "--entry", 100, "--sl", 98, "--tp", 104)
        self.assertEqual(code, 0)
        self.assertEqual(r["side"], "long")
        self.assertAlmostEqual(r["targets"][0]["rr"], 2.0)
        code, r, _ = run("--side", "sell", "--entry", 100, "--sl", 102, "--tp", 96)
        self.assertEqual((code, r["side"]), (0, "short"))

    def test_stop_wrong_side(self):
        code, r, _ = run("--side", "long", "--entry", 100, "--sl", 101, "--tp", 105)
        self.assertEqual(code, 1)
        self.assertIn("mauvais côté", r["errors"][0])
        code, r, _ = run("--side", "short", "--entry", 100, "--sl", 99, "--tp", 95)
        self.assertEqual(code, 1)

    def test_tp_wrong_side(self):
        code, r, _ = run("--side", "long", "--entry", 100, "--sl", 98, "--tp", 99)
        self.assertEqual(code, 1)
        self.assertTrue(any("TP" in e for e in r["errors"]))

    def test_stop_too_tight(self):
        code, r, _ = run("--side", "long", "--entry", 100, "--sl", 99.99, "--tp", 101)
        self.assertEqual(code, 1)
        self.assertTrue(any("serré" in e for e in r["errors"]))

    def test_min_rr_refused_with_better_entry(self):
        code, r, _ = run("--side", "short", "--entry", 28205, "--sl", 28320, "--tp", 28100)
        self.assertEqual(code, 1)
        self.assertTrue(any("R:R" in e for e in r["errors"]))
        self.assertTrue(any("28 232" in w for w in r["warnings"]))
        # that better entry passes
        code, r, _ = run("--side", "short", "--entry", 28232, "--sl", 28320, "--tp", 28100)
        self.assertEqual(code, 0)

    def test_custom_min_rr(self):
        code, _, _ = run("--side", "long", "--entry", 100, "--sl", 98, "--tp", 102, "--min-rr", 1)
        self.assertEqual(code, 0)

    def test_sizing_stock(self):
        code, r, _ = run("--side", "long", "--entry", 364.18, "--sl", 358.32, "--tp", 375.90,
                         "--account", 5000, "--risk-pct", 1)
        self.assertEqual(code, 0)
        self.assertAlmostEqual(r["size"]["risk_budget"], 50)
        self.assertAlmostEqual(r["size"]["max_loss"], 50)
        self.assertAlmostEqual(r["size"]["qty"], 50 / 5.86, places=4)

    def test_sizing_forex_lot_and_leverage_warning(self):
        code, r, _ = run("--side", "long", "--entry", 1.0850, "--sl", 1.0822, "--tp", 1.0910,
                         "--account", 2000, "--risk-pct", 1, "--point-value", 100000)
        self.assertEqual(code, 0)
        self.assertAlmostEqual(r["size"]["qty"], 20 / (0.0028 * 100000), places=4)
        self.assertTrue(any("levier" in w for w in r["warnings"]))

    def test_sizing_futures_risk_amount(self):
        code, r, _ = run("--side", "short", "--entry", 28295, "--sl", 28375, "--tp", 28150,
                         "--risk-amount", 160, "--point-value", 2)
        self.assertEqual(code, 0)
        self.assertAlmostEqual(r["size"]["qty"], 1.0)

    def test_high_risk_pct_warning(self):
        _, r, _ = run("--side", "long", "--entry", 100, "--sl", 98, "--tp", 104, "--account", 1000, "--risk-pct", 5)
        self.assertTrue(any("5 %" in w for w in r["warnings"]))

    def test_invalid_prices(self):
        code, _, err = run("--side", "long", "--entry", 0, "--sl", -1, "--tp", 1)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
