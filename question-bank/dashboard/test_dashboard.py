import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('dashboard',Path(__file__).with_name('server.py'))
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)

class DashboardTests(unittest.TestCase):
    def test_sheet_membership(self):
        self.assertEqual(len(app.select({'sheet':['main']})),38926)
        eu=app.select({'sheet':['eu']})
        self.assertEqual(len(eu),27948)
        self.assertTrue(all('EU:en' in q['tags'] and q['category']!='Religion & Faith' for q in eu))
        self.assertEqual(len(app.select({'sheet':['ua']})),36614)
        self.assertEqual(len(app.select({'sheet':['ua'],'pool':['potential']})),24931)
        self.assertEqual(len(app.select({'sheet':['ua'],'pool':['included']})),799)
        self.assertEqual(len(app.select({'sheet':['ua'],'pool':['unassessed']})),24132)

    def test_tag_boolean_filters(self):
        both=app.select({'tag':['EU:en','EU:uk']})
        either=app.select({'tag':['EU:en','EU:uk'],'match':['any']})
        self.assertEqual(len(both),799);self.assertEqual(len(either),27948)
        self.assertEqual(len(app.select({'tag':['EU:en'],'without':['EU:uk']})),27149)

    def test_translation_search_and_combined_filters(self):
        q=app.MASTER[0]; t=app.TRANSLATIONS[q['id']]
        result=app.select({'sheet':['ua'],'search':[q['id']]})
        self.assertEqual(len(result),1);self.assertEqual(result[0]['choices'],t['choices'])
        self.assertEqual(result[0]['correct'],q['correct'])
        self.assertEqual(len(app.select({'translation':['missing']})),2312)
        result=app.select({'sheet':['main'],'category':['Religion & Faith'],'status':['exclude'],'without':['EU']})
        self.assertEqual(len(result),483)
        self.assertEqual(app.select({'search':['no-such-question-xyz-987']}),[])

if __name__=='__main__':unittest.main()
