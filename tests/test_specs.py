from __future__ import annotations
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'plugins/spec-extractor/skills/spec-extractor'
spec=importlib.util.spec_from_file_location('spec_tools',SKILL/'scripts/spec_tools.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SpecificationTests(unittest.TestCase):
    def setUp(self):self.data=json.loads((SKILL/'examples/sample-extraction.json').read_text('utf-8'))
    def field(self):return self.data['products'][0]['fields'][0]
    def test_valid_fixture(self):self.assertEqual(m.validate(self.data),[])
    def test_unresolved_not_guessed(self):
        self.data['products'][0]['fields'][-1]['value']=200
        self.assertTrue(any('unresolved' in e for e in m.validate(self.data)))
    def test_source_required(self):
        self.field()['evidence']=[];self.assertTrue(any('evidence required' in e for e in m.validate(self.data)))
    def test_broken_reference(self):
        self.field()['evidence'][0]['source_id']='unknown';self.assertTrue(any('unknown source' in e for e in m.validate(self.data)))
    def test_locator_required(self):
        self.field()['evidence'][0]['locator']='';self.assertTrue(m.validate(self.data))
    def test_quote_required(self):
        self.field()['evidence'][0]['quote']='';self.assertTrue(m.validate(self.data))
    def test_one_based_page(self):
        self.field()['evidence'][0]['page']=0;self.assertTrue(m.validate(self.data))
    def test_boolean_not_page_number(self):
        self.field()['evidence'][0]['page']=True;self.assertTrue(m.validate(self.data))
    def test_conflict_candidates_required(self):
        self.data['products'][0]['fields'][1]['candidates']=[];self.assertTrue(m.validate(self.data))
    def test_conflict_candidate_evidence(self):
        self.data['products'][0]['fields'][1]['candidates'][0]['evidence']=[];self.assertTrue(m.validate(self.data))
    def test_derived_formula_required(self):
        self.field()['status']='derived';self.assertTrue(any('derivation' in e for e in m.validate(self.data)))
    def test_duplicate_variant_rejected(self):
        self.data['products'].append(copy.deepcopy(self.data['products'][0]));self.assertTrue(any('duplicate product' in e for e in m.validate(self.data)))
    def test_same_product_different_variant_allowed(self):
        other=copy.deepcopy(self.data['products'][0]);other['variant_id']='US';self.data['products'].append(other)
        self.assertEqual(m.validate(self.data),[])
    def test_duplicate_field_rejected(self):
        self.data['products'][0]['fields'].append(copy.deepcopy(self.field()));self.assertTrue(any('duplicate field' in e for e in m.validate(self.data)))
    def test_wrong_type_is_error_not_crash(self):
        self.field()['status']=[];self.assertTrue(m.validate(self.data))
    def test_nonfinite_rejected(self):
        self.field()['value']=float('nan');self.assertTrue(m.validate(self.data))
    def test_formula_escape(self):
        for s in ['=HYPERLINK("bad")','+1','-1','@SUM(A1)','  =1','\t=1','\n=1']:
            self.assertTrue(m.csv_safe(s).startswith("'"))
        self.assertEqual(m.csv_safe('ordinary'),'ordinary')
    def test_export_bom_conflicts_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'result';m.export(self.data,out)
            self.assertTrue((out/'specifications.csv').read_bytes().startswith(b'\xef\xbb\xbf'))
            result=json.loads((out/'specifications.json').read_text('utf-8'))
            self.assertIsNone(result['products'][0]['fields'][1]['value'])
            self.assertEqual(len(result['products'][0]['fields'][1]['candidates']),2)
            self.assertIn('Candidates:',(out/'review.md').read_text('utf-8'))
            with self.assertRaises(FileExistsError):m.export(self.data,out)
    def test_real_fixture_quotes_match(self):
        text=(SKILL/'examples/sample-source.txt').read_text('utf-8')
        for f in self.data['products'][0]['fields']:
            evid=list(f['evidence'])
            for c in f.get('candidates',[]):evid+=c['evidence']
            for e in evid:self.assertIn(e['quote'],text)

if __name__=='__main__':unittest.main()
