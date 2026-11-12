#!/usr/bin/env python3
"""Check fixture identity or score archived model answers; no model/API calls.

python tools/benchmark.py --check-fixtures
python tools/benchmark.py --answers evaluation/answers.json --output evaluation/report.json
Answers: {model, model_version, prompt_version, cases:[{id, latest_price, signal, available}]}.
Never submit expected labels as model answers; keep real held-out captures separately.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fixtures(root=ROOT):
    doc=json.loads((root/'evaluation/cases.json').read_text())
    ids=set()
    for case in doc['cases']:
        if case['id'] in ids:raise ValueError('duplicate case id')
        ids.add(case['id'])
        for image in case['images']:
            path=(root/image['path']).resolve()
            if not path.is_relative_to(root.resolve()):raise ValueError('image path outside repository')
            if hashlib.sha256(path.read_bytes()).hexdigest()!=image['sha256']:raise ValueError('fixture hash mismatch')
    return doc['cases']


def score(cases, answers):
    for key in ('model','model_version','prompt_version'):
        if not isinstance(answers.get(key),str) or not answers[key].strip():raise ValueError(key+' required')
    expected={x['id']:x['expected'] for x in cases}
    rows={}
    for row in answers.get('cases',[]):
        ident=row['id']
        if ident not in expected or ident in rows:raise ValueError('unknown/duplicate answer id')
        if row.get('signal') not in ('LONG','SHORT','NO TRADE'):raise ValueError('invalid signal')
        price=row.get('latest_price')
        if price is not None and (isinstance(price,bool) or not isinstance(price,(float,int)) or not math.isfinite(price) or price<=0):raise ValueError('invalid price')
        if type(row.get('available')) is not int or not 0<=row['available']<=5:raise ValueError('invalid denominator')
        rows[ident]=row
    correct={key:sum(row.get(key)==expected[ident][key] for ident,row in rows.items()) for key in ('latest_price','signal','available')}
    no_trade=[ident for ident in rows if expected[ident]['signal']=='NO TRADE']
    unsafe=sum(rows[x]['signal']!='NO TRADE' for x in no_trade)
    return {'scope':'synthetic development cases only; no profitability or real-image validation',
            'model':answers['model'],'model_version':answers['model_version'],'prompt_version':answers['prompt_version'],
            'expected_cases':len(cases),'answered':len(rows),'complete':len(rows)==len(cases),
            'correct':correct,'unsafe_action_on_abstention_cases':unsafe,
            'unanswered':sorted(set(expected)-set(rows))}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-fixtures',action='store_true')
    p.add_argument('--answers');p.add_argument('--output')
    a=p.parse_args()
    try:
        cases=fixtures()
        if a.check_fixtures:
            print(f'{len(cases)} synthetic fixture sets verified; no model evaluated')
            return
        if not a.answers:p.error('--answers or --check-fixtures required')
        result=score(cases,json.loads(Path(a.answers).read_text()))
        text=json.dumps(result,indent=2,allow_nan=False)+'\n'
        if a.output:Path(a.output).write_text(text)
        print(text,end='')
    except (OSError, ValueError,KeyError,TypeError) as exc:p.error(str(exc))


if __name__=='__main__':main()
