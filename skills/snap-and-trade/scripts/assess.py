#!/usr/bin/env python3
"""Evaluate explicit chart observations, not pixels. No network or order execution.

python assess.py --file observations.json
Unknown data is not a negative signal. Mandatory context still gates readiness.
A score is a descriptive count, never a probability or proof of profitability.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

CRITERIA = ('trend', 'level', 'candle', 'momentum', 'volume')


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name}: positive finite number required')
    return value


def timeframe(text):
    text = str(text).lower()
    if len(text) < 2 or text[-1] not in 'mhdw' or not text[:-1].isdigit() or int(text[:-1]) <= 0:
        raise ValueError('timeframe must be like 5m, 1h, 1d or 1w')
    return int(text[:-1]) * {'m': 1, 'h': 60, 'd': 1440, 'w': 10080}[text[-1]]


def evaluate(doc):
    if not isinstance(doc, dict):
        raise ValueError('observations must be an object')
    reasons, warnings = [], []
    side = doc.get('side')
    if side not in ('long', 'short', 'none', None):
        raise ValueError('side must be long, short or none')
    if side in ('none', None):
        reasons.append('no defensible directional setup')
    sign = (1 if side == 'long' else -1) if side in ('long', 'short') else None
    criteria = doc.get('criteria', {})
    if not isinstance(criteria, dict) or set(criteria) - set(CRITERIA):
        raise ValueError('unknown confluence criterion')
    for key, value in criteria.items():
        if value is not None and type(value) is not bool:
            raise ValueError(f'{key}: true, false or null required')
    available = [k for k in CRITERIA if criteria.get(k) is not None]
    points = sum(criteria[k] for k in available)
    total = len(available)
    # Structure, a tradeable level and closed-candle confirmation remain mandatory.
    if any(criteria.get(k) is None for k in CRITERIA[:3]):
        reasons.append('missing core observation: trend, level or closed candle')
    if points < 2 or total < 3:
        reasons.append('insufficient observed confluence')
    if criteria.get('level') is not True:
        reasons.append('no observed entry/invalidation level')
    if criteria.get('candle') is not True:
        reasons.append('trigger not confirmed by a closed candle')
    label = 'low'
    if total >= 3 and points >= 2 and points / total >= 0.6:
        label = 'medium'
    if total >= 4 and points / total >= 0.8:
        label = 'high'
    if criteria.get('trend') is False:
        label = 'low'
    low_tf = timeframe(doc['timeframe']) if doc.get('timeframe') is not None else None
    if low_tf is None:
        reasons.append('execution timeframe unreadable; request clarification')
    asset = str(doc.get('asset') or '').strip()
    if not asset:
        reasons.append('instrument identity unreadable; request clarification')
    htf = doc.get('higher_timeframe')
    higher_observed = None
    if htf is None:
        reasons.append('request a higher-timeframe screenshot of the same instrument')
        label = 'low'
    elif not isinstance(htf, dict):
        raise ValueError('higher_timeframe must be an object')
    else:
        if not asset or low_tf is None or htf.get('asset') != asset or htf.get('timeframe') is None or timeframe(htf['timeframe']) <= low_tf:
            reasons.append('higher-timeframe image is a different instrument or not a higher timeframe')
            label = 'low'
        if htf.get('fresh') is not True:
            reasons.append('higher-timeframe freshness unconfirmed')
            label = 'low'
        try:
            higher_observed = dt.datetime.fromisoformat(htf.get('observed_at', ''))
            if higher_observed.utcoffset() is None:
                higher_observed = None
        except (TypeError, ValueError):
            higher_observed = None
        if higher_observed is None:
            reasons.append('higher-timeframe capture timestamp with timezone required')
            label = 'low'
        trend = htf.get('trend')
        if trend not in ('up', 'down', 'range', 'unknown'):
            raise ValueError('higher-timeframe trend must be up/down/range/unknown')
        if trend == 'unknown':
            reasons.append('higher-timeframe structure unreadable')
            label = 'low'
        elif trend == ('down' if side == 'long' else 'up'):
            label = 'low'
            warnings.append('counter to higher-timeframe structure; confidence capped at low')
        elif trend == 'range' and label == 'high':
            label = 'medium'
    prices = doc.get('prices', {})
    if not isinstance(prices, dict):
        raise ValueError('prices must be an object')
    for name, value in prices.items():
        if name not in ('axis', 'header', 'panel', 'user_confirmed'):
            raise ValueError(f'unknown price source: {name}')
        if value is not None:
            positive(value, name)
    latest = prices.get('axis') or prices.get('user_confirmed')
    if latest is None:
        reasons.append('no readable latest-price axis label or user-confirmed latest price')
    for name in ('header', 'panel'):
        if latest is not None and prices.get(name) is not None and prices[name] != latest:
            warnings.append(f'{name} price differs from latest axis/user price; do not substitute cursor OHLC or another instrument')
    stamp = doc.get('observed_at')
    try:
        observed = dt.datetime.fromisoformat(stamp) if stamp else None
        if observed is None or observed.utcoffset() is None:
            reasons.append('capture date/time with timezone required')
    except (TypeError, ValueError):
        raise ValueError('observed_at must be an ISO datetime with timezone')
    if htf and higher_observed is not None and observed is not None and observed.utcoffset() is not None:
        if htf.get('timeframe') is None or abs((observed - higher_observed).total_seconds()) > timeframe(htf['timeframe']) * 60:
            reasons.append('capture timestamps do not overlap the context window')
            label = 'low'
    session = doc.get('session', 'unknown')
    if session not in ('open', 'closed', 'unknown'):
        raise ValueError('session must be open, closed or unknown')
    if session != 'open':
        reasons.append('opening plan only' if session == 'closed' else 'market session unknown')
    if doc.get('fresh') is not True:
        reasons.append('capture freshness unconfirmed; request current screenshot')
    levels = {}
    for key in ('entry', 'sl', 'tp1'):
        value = doc.get(key)
        levels[key] = positive(value, key) if value is not None else None
        if value is None:
            reasons.append(f'no defensible {key} level; do not invent one')
    entry, sl, tp1 = (levels[k] for k in ('entry', 'sl', 'tp1'))
    risk = (entry - sl) * sign if sign is not None and entry is not None and sl is not None else None
    reward = (tp1 - entry) * sign if sign is not None and entry is not None and tp1 is not None else None
    if (risk is not None and risk <= 0) or (reward is not None and reward <= 0):
        reasons.append('invalid stop or target direction')
    avg = doc.get('avg_candle')
    if avg is None:
        reasons.append('average closed-candle high-low range required for stop check')
    else:
        positive(avg, 'avg_candle')
        if risk is not None and risk < 1.5 * avg:
            reasons.append('stop below 1.5 times average closed-candle range')
    if doc.get('plan_valid') is not True:
        reasons.append('plan.py must pass using costs and instrument constraints')
    opening = None
    if session == 'closed':
        opening = {'cancel_at_or_beyond_stop': sl, 'cancel_at_or_beyond_tp1': tp1,
                   'between_bounds': 'wait for a closed trigger; refresh both images and rerun numerical checks',
                   'valid_for': 'next confirmed session only; reconfirm calendar, instrument and timezone'}
    return {'signal': 'NO TRADE' if reasons else side.upper(),
            'candidate_side': side.upper() if side in ('long', 'short') else 'UNDETERMINED', 'mode': 'opening-plan' if session == 'closed' else 'review',
            'score': f'{points}/{total}', 'points': points, 'available': total,
            'unavailable': [k for k in CRITERIA if k not in available],
            'confidence': label, 'latest_price': latest,
            'reasons': reasons, 'warnings': warnings, 'opening_conditions': opening}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(Path(args.file).read_text(encoding='utf-8')))
        print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
        return 0 if result['signal'] != 'NO TRADE' else 1
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
