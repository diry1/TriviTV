"""Integrity and lifecycle checks for editorial metadata."""
import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tags', ROOT / 'scripts/build-question-tags.py')
tags = importlib.util.module_from_spec(spec); spec.loader.exec_module(tags)

class TagIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.master = json.loads((ROOT / 'question-bank/questions.json').read_text(encoding='utf8'))
        cls.original = json.loads((tags.ARCHIVE / 'data/opentriviaqa/questions.json').read_text(encoding='utf8'))

    def test_complete_bank_and_all_original_fields_preserved(self):
        self.assertEqual(len(self.master), 38926)
        edits=tags.editorial.load()['records']
        expected=[{**q,'category':edits.get(q['id'],{}).get('category') or q['category']} for q in self.original]
        self.assertEqual([{k:v for k,v in q.items() if k != 'tags'} for q in self.master], expected)

    def test_membership_matches_current_screen_and_is_language_scoped(self):
        with (ROOT / 'artifacts/question-bank-screen-2026-10-21/decisions.csv').open(encoding='utf-8-sig') as f:
            screen = {r['id']:r for r in csv.DictReader(f)}
        edits=tags.editorial.load()['records']
        for q in self.master:
            t = q['tags']; s = screen.get(q['id'])
            edit=edits.get(q['id'],{})
            override=edit.get('status',{}).get('uk')
            expected=override=='candidate' if override else bool(s and s['status']=='previously_screened_draft')
            self.assertEqual('EU:uk' in t,expected and q['category']!='Religion & Faith')
            self.assertEqual('EU' in t, 'EU:uk' in t or 'EU:en' in t)
            if q['category'] == 'Religion & Faith':
                self.assertNotIn('EU', t)
            self.assertEqual(t, sorted(set(t)))
        self.assertTrue(any('EU:en' in q['tags'] and 'EU:uk' not in q['tags'] for q in self.master))

    def test_multiple_sources_and_withdrawal(self):
        owned = {'known': {'generated': ['EU', 'EU:en']}}
        tags.apply_extra(owned, [(Path('a.json'), {'known':['custom:topic:space']}), (Path('b.json'), {'known':['custom:topic:space','custom:group:adult']})])
        del owned['known']['custom:a']
        self.assertIn('custom:topic:space', tags.merge_sources(owned['known']))
        del owned['known']['custom:b']
        self.assertNotIn('custom:topic:space', tags.merge_sources(owned['known']))
        owned['known']['generated'] = tags.eu_tags(False, False)
        self.assertNotIn('EU', tags.merge_sources(owned['known']))

    def test_english_subtractive_pool_ignores_translation_only_and_unassessed(self):
        q={'category':'Movies'}
        for rules in [['UNASSESSED'],['UA02'],['UA_REPAIR','EN_REASSESS'],['UA04','EU09']]:
            self.assertEqual(tags.english_filters(q,{'outcome':'hold','rules':rules},[]),[])
        self.assertEqual(tags.english_filters(q,{'outcome':'exclude','rules':['UA02','EU01']},[]),['EU01'])
        self.assertEqual(tags.english_filters(q,{'outcome':'exclude','rules':['UA02']},[{'rules':['Q04']}]),['Q04'])
        self.assertEqual(tags.english_filters({'category':'Religion & Faith'},{'outcome':'candidate','rules':[]},[],True),['NEW_RELIGION_CATEGORY'])

    def test_unknown_ids_and_manual_membership_rejected(self):
        for document in [{'unknown':['custom:test']}, {'known':['EU']}, {'known':'custom:test'}]:
            with self.assertRaises(ValueError):
                tags.apply_extra({'known':{}}, [(Path('manual.json'),document)])

    def test_csv_tags_and_answers_round_trip(self):
        with (ROOT / 'question-bank/questions.csv').open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), len(self.master))
        for row, q in zip(rows,self.master):
            self.assertEqual(json.loads(row['tags']), q['tags'])
            self.assertEqual(int(row['correct_index']), q['correct'])
            self.assertEqual([row['choice_'+c] for c in 'abcd'], q['choices'])

if __name__ == '__main__':
    unittest.main()
