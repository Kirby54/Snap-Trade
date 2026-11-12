"""Observable regression scenarios; not a vision benchmark or performance evidence."""
import copy
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from _load import load, SCRIPTS, FIX
assess = load('snap', 'assess')
entry = load('snap', 'entry')
exitp = load('snap', 'exit')
size = load('snap', 'size')
check = load('snap', 'check')
tm = load('snap', 'timemachine')
ticket = load('snap', 'ticket')


def observations():
    return {'asset': 'CAC40-DEMO', 'timeframe': '5m', 'side': 'short',
            'higher_timeframe': {'asset': 'CAC40-DEMO', 'timeframe': '1h', 'trend': 'down', 'fresh': True, 'observed_at': '2026-11-12T15:00:00+01:00'},
            'criteria': {'trend': True, 'level': True, 'candle': True, 'momentum': None, 'volume': None},
            'prices': {'axis': 8372, 'header': 8394, 'panel': 8361},
            'observed_at': '2026-11-12T15:00:00+01:00', 'fresh': True, 'session': 'open',
            'entry': 8372, 'sl': 8390, 'tp1': 8340, 'avg_candle': 10, 'plan_valid': True}


class ChartObservations(unittest.TestCase):
    def test_index_is_scored_only_on_available_evidence(self):
        d = observations()
        r = assess.evaluate(d)
        self.assertEqual((r['score'], r['signal'], r['confidence']), ('3/3', 'SHORT', 'medium'))
        d['criteria']['trend'] = False
        r = assess.evaluate(d)
        self.assertEqual((r['score'], r['confidence']), ('2/3', 'low'))

    def test_missing_is_not_negative_but_weak_visible_signal_counts(self):
        d = observations()
        d['criteria']['volume'] = False
        self.assertEqual(assess.evaluate(d)['score'], '3/4')
        d['criteria']['volume'] = True
        self.assertEqual(assess.evaluate(d)['confidence'], 'high')
        d['higher_timeframe']['trend'] = 'up'
        self.assertEqual(assess.evaluate(d)['confidence'], 'low')

    def test_cursor_and_panel_do_not_replace_axis_label(self):
        r = assess.evaluate(observations())
        self.assertEqual(r['latest_price'], 8372)
        self.assertEqual(len(r['warnings']), 2)
        d = observations(); d['prices'].pop('axis')
        self.assertEqual(assess.evaluate(d)['signal'], 'NO TRADE')

    def test_missing_context_and_unconfirmed_candle_block_readiness(self):
        for key, value in [('higher_timeframe', None), ('fresh', False), ('observed_at', None), ('plan_valid', False)]:
            d = observations(); d[key] = value
            self.assertEqual(assess.evaluate(d)['signal'], 'NO TRADE', key)
        d = observations(); d['criteria']['candle'] = False
        self.assertEqual(assess.evaluate(d)['score'], '2/3')
        self.assertEqual(assess.evaluate(d)['signal'], 'NO TRADE')
        d['higher_timeframe']['observed_at'] = '2026-11-10T15:00:00+01:00'
        self.assertEqual(assess.evaluate(d)['signal'], 'NO TRADE')
        d['higher_timeframe'] = {'asset': 'OTHER', 'timeframe': '5m', 'trend': 'down'}
        self.assertEqual(assess.evaluate(d)['signal'], 'NO TRADE')

    def test_closed_session_is_an_opening_plan(self):
        d = observations(); d['session'] = 'closed'
        r = assess.evaluate(d)
        self.assertEqual((r['signal'], r['mode']), ('NO TRADE', 'opening-plan'))
        self.assertEqual(r['opening_conditions']['cancel_at_or_beyond_stop'], 8390)

    def test_seven_point_stop_is_rejected_with_ten_point_mean_range(self):
        d = observations(); d['sl'] = 8379
        self.assertTrue(any('stop below' in x for x in assess.evaluate(d)['reasons']))

    def test_early_abstention_does_not_require_invented_levels(self):
        d = observations(); d.update(entry=None, tp1=None, plan_valid=False)
        r = assess.evaluate(d)
        self.assertEqual(r['signal'], 'NO TRADE')
        self.assertTrue(any('no defensible entry' in x for x in r['reasons']))
        d['session'] = 'closed'
        self.assertEqual(assess.evaluate(d)['mode'], 'opening-plan')

    def test_unknown_identity_timeframe_and_direction_are_early_abstentions(self):
        d = observations();d.update(asset=None,timeframe=None,side=None,entry=None,sl=None,tp1=None,plan_valid=False)
        r = assess.evaluate(d)
        self.assertEqual(r['signal'], 'NO TRADE')
        self.assertEqual(r['candidate_side'], 'UNDETERMINED')

    def test_malformed_observations_fail_cleanly(self):
        for value in ('true', 1, [], {}):
            d = observations(); d['criteria']['volume'] = value
            with self.assertRaises(ValueError): assess.evaluate(d)


class NumericalCandleFloor(unittest.TestCase):
    def run_plan(self, *extra):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, 'plan.py'), '--side', 'short',
                               '--entry', '8372', '--sl', '8390', '--tp', '8340', '--avg-candle', '10',
                               '--json', *map(str, extra)], capture_output=True, text=True, encoding='utf-8')

    def test_floor_and_boundary_in_both_directions(self):
        self.assertEqual(self.run_plan('--sl', 8379).returncode, 1)
        self.assertEqual(self.run_plan('--sl', 8387).returncode, 0)
        self.assertEqual(self.run_plan('--side', 'long', '--sl', 8365, '--tp', 8410).returncode, 1)
        self.assertEqual(self.run_plan('--side', 'long', '--sl', 8357, '--tp', 8410).returncode, 0)
        self.assertEqual(self.run_plan('--avg-candle', 'nan').returncode, 2)
        self.assertEqual(self.run_plan('--min-candle-multiple', '.5').returncode, 2)

    def test_gap_invalidation_both_sides(self):
        for price in (8390, 8400, 8340, 8300):
            self.assertEqual(self.run_plan('--open-price', price).returncode, 1)
        self.assertEqual(self.run_plan('--open-price', 8370).returncode, 0)
        for price in (8350, 8410):
            self.assertEqual(self.run_plan('--side', 'long', '--sl', 8350, '--tp', 8410,
                                           '--open-price', price).returncode, 1)


class ShortPipeline(unittest.TestCase):
    def test_short_stop_rounds_away_and_target_is_below(self):
        c = exitp.compute(100, 'pct', Decimal('1.005'), 'r', Decimal('2'), side='sell')
        self.assertEqual(c['stop'], Decimal('101.01'))
        self.assertEqual(c['target'], Decimal('97.98'))
        with self.assertRaises(exitp.PlanError):
            exitp.compute(100, 'price', Decimal(98), 'r', Decimal(2), side='sell')

    def test_entry_exit_size_risk_chain_without_network_or_orders(self):
        # Explicitly synthetic transformation of recorded fixture bars; not market performance.
        path = Path(FIX) / 'trader-entry/TSLA-2026-10-19-5m.json'
        chart = entry.parse_chart(path.read_text(), 'TSLA')
        for b in chart['bars']:
            b['o'], b['h'], b['l'], b['c'] = 800-b['o'], 800-b['l'], 800-b['h'], 800-b['c']
        chart['prev_close'] = None
        now = entry.parse_now('2026-10-19 10:15')
        signal = entry.evaluate(chart, now, side='sell')
        self.assertEqual(signal['status'], 'triggered')
        doc = entry.entry_doc(signal, now)
        self.assertEqual(doc['side'], 'sell')
        c = exitp.compute(doc['price'], 'or_mid', None, 'r', Decimal('2'),
                          doc['opening_range']['high'], doc['opening_range']['low'], side='sell')
        plan = {'symbol': 'TSLA', 'side': 'sell', 'entry': float(c['entry']), 'stop': float(c['stop']),
                'target': float(c['target']), 'date': '2026-10-19'}
        with self.assertRaises(size.SizeError): size.size_trade(plan, {'budget': 5000})
        cfg = {'budget': 5000, 'allow_short': True, 'paper': True}
        sized = size.size_trade(plan, cfg, today='2026-10-19')
        order = size.bracket_order(sized)
        self.assertEqual(order['side'], 'sell')
        self.assertGreater(sized['qty'], 0)
        self.assertLessEqual(sized['max_loss'], 50)
        verdict = check.check([order], cfg, now=now)
        self.assertEqual(verdict['results'][0]['verdict'], 'PASS', verdict)
        ready, label, _ = ticket.status_of(order, verdict, {'orders': []}, '2026-10-19')
        self.assertFalse(ready)
        self.assertIn('short-entry execution', label)
        blocked = check.check([order], dict(cfg, allow_short=False), now=now)
        self.assertEqual(blocked['results'][0]['verdict'], 'BLOCK')
        # Existing timemachine supports both sides; normalize and simulate the resulting short.
        p = tm.normalize_plan(dict(plan, entry_bar=doc['bar_index'], setup='orb',
                                   opening_range=doc['opening_range'], stop_rule='or_mid'))
        self.assertEqual(p['side'], 'sell')
        self.assertGreater(p['risk_per_share'], 0)

    def test_short_cannot_inflate_equity_or_bypass_position_and_collateral_caps(self):
        now = check.parse_now('2026-10-19 10:15')
        order = {'symbol':'AAPL','side':'sell','qty':'20','type':'limit','limit_price':'100',
                 'plan':{'entry':100,'stop':102,'target':96}}
        cfg = {'budget':1000,'allow_short':True,'allow_margin':False,'max_order_usd':0,
               'max_position_pct':10,'max_loss_per_trade_usd':1000,'max_daily_loss_usd':1000}
        r = check.check([order], cfg, now=now)
        self.assertEqual(r['results'][0]['verdict'],'BLOCK')
        self.assertTrue(any('position:' in x for x in r['results'][0]['reasons']))
        self.assertEqual(r['cash_after'],1000)
        cfg.update(max_position_pct=100, cash_buffer_pct=0)
        first = dict(order, qty='5')
        buy = {'symbol':'MSFT','side':'buy','qty':'6','type':'limit','limit_price':'100',
               'plan':{'entry':100,'stop':98,'target':104}}
        r = check.check([first,buy],cfg,now=now)
        self.assertEqual([x['verdict'] for x in r['results']],['PASS','BLOCK'])
        # Sale proceeds remain cash, with an equal signed debt; they are restricted.
        self.assertEqual(r['cash_after'],1500)
        self.assertTrue(any('cash:' in x for x in r['results'][1]['reasons']))

    def test_short_market_sizing_uses_lower_price_for_worse_risk(self):
        p = {'symbol': 'TEST', 'side': 'sell', 'entry': 100, 'stop': 102, 'target': 94}
        s = size.size_trade(p, {'budget': 1000, 'allow_short': True}, price=99)
        self.assertEqual(s['entry'], 99)
        self.assertEqual(s['risk_per_share'], 3)
