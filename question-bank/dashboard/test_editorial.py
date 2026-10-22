import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('server',Path(__file__).with_name('server.py'))
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)

class EditorialTests(unittest.TestCase):
    def test_language_membership_and_category_override(self):
        q={'id':'test','category':'Animals','text':'original','choices':['a','b','c','d'],'correct':2,'tags':['EU','EU:en','EU:uk','category:animals','difficulty:category-default:2','pool:eu-uk:potential-unassessed','screen:eu:en:candidate','screen:eu:uk:candidate']}
        edited=server.editorial.apply(q,{'category':'Movies','status':{'en':'hold','uk':'exclude'},'tags':['custom:manual:check']},{'Movies':3})
        self.assertEqual(q['category'],'Animals');self.assertEqual(edited['category'],'Movies')
        self.assertEqual(edited['choices'],q['choices']);self.assertEqual(edited['correct'],2)
        self.assertNotIn('EU',edited['tags']);self.assertNotIn('pool:eu-uk:potential-unassessed',edited['tags'])
        self.assertIn('category:movies',edited['tags']);self.assertIn('custom:manual:check',edited['tags'])

    def test_missing_translation_and_reserved_statuses_rejected(self):
        missing=next(q['id'] for q in server.MASTER if q['id'] not in server.TRANSLATIONS)
        with self.assertRaises(ValueError):server.validate_edit({'id':missing,'status':{'uk':'candidate'}})
        with self.assertRaises(ValueError):server.validate_edit({'id':server.MASTER[0]['id'],'status':{'en':'invented'}})
        with self.assertRaises(ValueError):server.validate_edit({'id':'missing'})

    def test_tags_normalized_and_empty_override_restores_values(self):
        q=server.MASTER[0]
        qid,edit=server.validate_edit({'id':q['id'],'category':'','status':{},'tags':['Party Favourite','party-favourite']})
        self.assertEqual(edit['tags'],['custom:manual:party-favourite'])
        self.assertEqual(server.editorial.apply(q,{},{}),q)

if __name__=='__main__':unittest.main()
