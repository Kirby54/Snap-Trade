"""Clean-directory CLI install smoke test; no hosted model or broker calls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from _load import ROOT


def tool(name):
    spec=importlib.util.spec_from_file_location(name,Path(ROOT)/'tools'/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


class Distribution(unittest.TestCase):
    def test_zip_is_reproducible_and_works_outside_checkout(self):
        pack=tool('package_skill')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);one=root/'one.zip';two=root/'two.zip'
            self.assertEqual(pack.build(one),pack.build(two))
            with zipfile.ZipFile(one) as z:z.extractall(root/'install')
            skill=root/'install/snap-and-trade'
            self.assertTrue((skill/'LICENSE').is_file())
            self.assertTrue((skill/'SKILL.md').is_file())
            p=subprocess.run([sys.executable,str(skill/'scripts/plan.py'),'--side','short','--entry','8372',
                              '--sl','8390','--tp','8340','--avg-candle','10','--json'],
                             cwd=root,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue(json.loads(p.stdout)['valid'])
            p=subprocess.run([sys.executable,str(skill/'scripts/assess.py'),'--file',str(skill/'references/observations.example.json')],
                             cwd=root,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads(p.stdout)['latest_price'],8372)

    def test_fixture_hashes_and_partial_benchmark_report(self):
        bench=tool('benchmark');cases=bench.fixtures()
        answers={'model':'unit-test-only','model_version':'none','prompt_version':'none','cases':[]}
        r=bench.score(cases,answers)
        self.assertFalse(r['complete']);self.assertEqual(r['answered'],0)
        answers['cases']=[{'id':cases[0]['id'],**cases[0]['expected']}]
        r=bench.score(cases,answers)
        self.assertEqual(r['correct']['latest_price'],1)
        self.assertFalse(r['complete'])
        answers['cases']*=2
        with self.assertRaises(ValueError):bench.score(cases,answers)
