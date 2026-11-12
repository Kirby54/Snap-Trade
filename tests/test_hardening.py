"""Regression tests for rejected inputs, executable sizing and journal integrity."""
import argparse
import csv
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from _load import load, SCRIPTS

journal = load('snap', 'journal')
check = load('snap', 'check')


def plan(*extra):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, 'plan.py'),
                           '--side', 'long', '--entry', '100', '--sl', '98', '--tp', '104',
                           '--json', *map(str, extra)], capture_output=True, text=True, encoding='utf-8')


class SizingSafety(unittest.TestCase):
    def test_nonfinite_and_nonpositive_inputs(self):
        for flag in ('entry', 'sl', 'tp', 'account', 'risk-pct', 'risk-amount',
                     'point-value', 'min-rr', 'fx-rate', 'qty-step', 'min-qty', 'max-notional'):
            for value in ('nan', 'inf', '-inf', '0', '-1'):
                with self.subTest(flag=flag, value=value):
                    p = plan(f'--{flag}={value}')
                    self.assertEqual(p.returncode, 2)
                    self.assertNotIn('Traceback', p.stderr)
        for flag in ('cost-per-unit', 'min-stop-pct'):
            for value in ('nan', 'inf', '-1'):
                self.assertEqual(plan(f'--{flag}={value}').returncode, 2)

    def test_cli_uses_utf8_even_with_legacy_windows_encoding(self):
        env = dict(os.environ, PYTHONIOENCODING='cp1252')
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'plan.py'),
                            '--side', 'long', '--entry', '100', '--sl', '98', '--tp', '104', '--json'],
                           env=env, capture_output=True)
        self.assertEqual(p.returncode, 0)
        self.assertTrue(json.loads(p.stdout.decode('utf-8'))['valid'])
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'plan.py'),
                            '--side', 'long', '--entry', 'nan', '--sl', '98', '--tp', '104'],
                           env=env, capture_output=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('nombre fini', p.stderr.decode('utf-8'))

    def test_arithmetic_overflow_fails_cleanly(self):
        p = plan('--account', '1e308', '--point-value', '1e-308', '--fx-rate', '1e-308')
        self.assertEqual(p.returncode, 2)
        self.assertNotIn('Traceback', p.stderr)

    def test_costs_can_turn_gross_valid_trade_into_rejection(self):
        p = plan('--cost-per-unit', '.5')
        r = json.loads(p.stdout)
        self.assertEqual(p.returncode, 1)
        self.assertEqual(r['targets'][0]['rr'], 2)
        self.assertAlmostEqual(r['targets'][0]['net_rr'], 1.4)

    def test_conversion_costs_and_quantity_step_respect_budget(self):
        p = plan('--account', '1000', '--point-value', '2', '--fx-rate', '.9',
                 '--cost-per-unit', '.2', '--qty-step', '.3')
        self.assertEqual(p.returncode, 0, p.stderr)
        s = json.loads(p.stdout)['size']
        self.assertEqual(s['qty'], 2.4)  # floor(10 / 3.8 / .3) * .3
        self.assertLessEqual(s['max_loss'], 10)
        self.assertAlmostEqual(s['max_loss'], 9.12)
        self.assertEqual(Decimal(str(s['qty'])) % Decimal('.3'), 0)

    def test_notional_limit_and_minimum_contract(self):
        p = plan('--account', '1000', '--qty-step', '1', '--max-notional', '300')
        self.assertEqual(json.loads(p.stdout)['size']['qty'], 3)
        self.assertEqual(plan('--risk-amount', '1', '--qty-step', '1').returncode, 1)
        self.assertEqual(plan('--risk-amount', '10', '--min-qty', '6').returncode, 1)
        self.assertEqual(plan('--qty-step', '1').returncode, 2)

    def test_high_risk_requires_explicit_override_for_both_budget_forms(self):
        for flags in (('--risk-pct', '5'), ('--risk-amount', '50')):
            p = plan('--account', '1000', *flags)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(plan('--account', '1000', *flags, '--allow-high-risk').returncode, 0)
        self.assertEqual(plan('--account', '100', '--risk-amount', '101').returncode, 2)

    def test_targets_must_be_in_exit_order_in_both_directions(self):
        for args in (('--tp', '106', '104'), ('--tp', '104', '104'),
                     ('--side', 'short', '--sl', '102', '--tp', '94', '96')):
            self.assertEqual(plan(*args).returncode, 1)


class JournalIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'journal.csv'

    def call(self, *args):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, 'journal.py'), '--file', str(self.path),
                               *map(str, args)], capture_output=True, text=True, encoding='utf-8')

    def add(self, *args):
        return self.call('add', '--asset', 'TEST', '--side', 'long', '--entry', '100',
                         '--sl', '98', '--tp1', '104', *args)

    def test_nonfinite_levels_and_bad_results_never_create_file(self):
        for args in (('--entry', 'nan'), ('--sl', 'inf'), ('--tp1', '-1'),
                     ('--cost-r', '-1'), ('--cost-r', 'nan'), ('--date', 'not-a-date'),
                     ('--outcome', 'tp2'), ('--outcome', 'exit'), ('--exit', '100')):
            with self.subTest(args=args):
                self.assertEqual(self.add(*args).returncode, 1)
                self.assertFalse(self.path.exists())
        self.assertEqual(self.call('add', '--asset', 'TEST', '--side', 'none', '--outcome', 'sl').returncode, 1)
        self.assertEqual(self.add('--asset', ' ').returncode, 1)

    def test_tp1_without_second_target_exits_full_position(self):
        self.assertEqual(self.add().returncode, 0)
        self.assertEqual(self.call('result', '1', '--outcome', 'tp1', '--cost-r', '.1').returncode, 0)
        p = self.call('stats', '--json')
        s = json.loads(p.stdout)['global']
        self.assertAlmostEqual(s['tp1']['avg_r'], 1.9)
        self.assertAlmostEqual(s['split']['avg_r'], 1.9)

    def test_rejected_update_keeps_exact_previous_bytes(self):
        self.add()
        original = self.path.read_bytes()
        for args in (('--outcome', 'exit', '--exit', 'nan'), ('--outcome', 'be', '--exit', '100'),
                     ('--outcome', 'sl', '--cost-r', '-1')):
            self.assertEqual(self.call('result', '1', *args).returncode, 1)
            self.assertEqual(self.path.read_bytes(), original)

    def test_lock_prevents_lost_updates(self):
        self.add()
        original = self.path.read_bytes()
        with journal.journal_lock(str(self.path)):
            p = self.add()
            self.assertEqual(p.returncode, 1)
            self.assertIn('occupé', p.stderr)
            self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(self.add().returncode, 0)
        self.assertEqual(len(journal.load(str(self.path))), 2)

    def test_corrupt_csv_is_not_overwritten(self):
        for content in ('oops\n', ','.join(journal.FIELDS) + '\n1,broken\n'):
            self.path.write_text(content)
            before = self.path.read_bytes()
            p = self.add()
            self.assertEqual(p.returncode, 1)
            self.assertNotIn('Traceback', p.stderr)
            self.assertEqual(self.path.read_bytes(), before)

    def test_legacy_schema_is_read_and_migrated(self):
        self.add()
        rows = journal.load(str(self.path))
        fields = [k for k in journal.FIELDS if k != 'cost_r']
        with self.path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        self.assertEqual(self.call('result', '1', '--outcome', 'sl').returncode, 0)
        self.assertEqual(journal.load(str(self.path))[0]['cost_r'], '0')

    def test_extra_columns_and_duplicate_ids_are_not_overwritten(self):
        self.add()
        original = self.path.read_text()
        duplicate = original + original.splitlines()[1] + '\n'
        extra = original.replace('cost_r', 'cost_r,unexpected', 1)
        for content in (duplicate, extra):
            self.path.write_text(content)
            before = self.path.read_bytes()
            self.assertEqual(self.add().returncode, 1)
            self.assertEqual(self.path.read_bytes(), before)

    def test_empty_stats_is_valid_json(self):
        self.assertEqual(json.loads(self.call('stats', '--json').stdout), {})


class RiskInputSafety(unittest.TestCase):
    def test_nonfinite_and_boolean_financial_fields_fail_closed(self):
        for key in ('qty', 'budget', 'entry', 'max_loss', 'cash'):
            for value in (float('nan'), float('inf'), 'NaN', 'Infinity', True):
                with self.subTest(key=key, value=value):
                    with self.assertRaises(check.RiskError):
                        check.validate_numbers({key: value})
        self.assertIsNone(check._f(float('nan')))
        self.assertIsNone(check._f(True))

    def test_cli_quote_loader_does_not_drop_invalid_prices(self):
        for value in ('NaN', 'Infinity', True, 0, -1):
            with self.subTest(value=value):
                with self.assertRaises(check.RiskError):
                    check.load_prices({'prices': {'AAPL': value}})
        prices, _ = check.load_prices({'prices': {'AAPL': '100'}})
        self.assertEqual(prices['AAPL'], 100)

    def test_bad_limits_and_percentages_fail_closed(self):
        for doc in ({'max_loss_per_trade_usd': -1}, {'cash_buffer_pct': 101}):
            with self.assertRaises(check.RiskError):
                check.validate_numbers(doc)
