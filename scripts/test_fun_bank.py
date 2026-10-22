import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('fun',Path(__file__).with_name('build-fun-bank.py'))
fun=importlib.util.module_from_spec(spec);spec.loader.exec_module(fun)

def q(text,choices=None,category='General Knowledge'):
    return {'id':'test','text':text,'category':category,'choices':choices or ['A','B','C','D'],'tags':['custom:semantic:topic:science']}

class FunRules(unittest.TestCase):
    def test_requested_exclusions(self):
        for record in [q('Who played in the NBA final?'),q('Which river crosses Texas?'),q('A faith question',category='Religion & Faith'),q('When was it founded?',['1950','1960','1970','1980']),q('Who directed this 1985 movie?',category='Movies')]:
            self.assertEqual(fun.classify(record)['outcome'],'exclude')

    def test_scope_and_ambiguity(self):
        self.assertEqual(fun.classify(q('Who directed this movie?',category='Movies'))['outcome'],'hold')
        self.assertEqual(fun.classify(q('Who directed this 2004 movie?',category='Movies'))['outcome'],'candidate')
        self.assertEqual(fun.classify(q('Which event happened in 1960?',category='History'))['outcome'],'candidate')
        self.assertEqual(fun.classify(q('How many metres is it?',['1000','1200','1400','1600']))['outcome'],'candidate')
        self.assertEqual(fun.classify(q('Which novel has this title?',['1984','Other','Third','Fourth'],category='Literature'))['outcome'],'hold')
        self.assertEqual(fun.classify(q('Which movie stars this actor, born in 1960?',category='Movies'))['outcome'],'hold')

    def test_strict_semantic_gates(self):
        for tag in ['audience:us-specific','topic:religion','form:number-recall','form:date-recall','audience:specialist-knowledge','form:wordplay','subject:song-lyrics','form:quote-identification']:
            record=q('A neutral question');record['tags'].append('custom:semantic:'+tag)
            self.assertEqual(fun.classify(record)['outcome'],'exclude',tag)
        for tag in ['translation-uk-risk:answer-distinction','translation-uk-risk:title-localization','entity-kind:movie-title','entity-kind:book-title']:
            record=q('A neutral question');record['tags'].append('custom:semantic:'+tag)
            self.assertEqual(fun.classify(record)['outcome'],'hold',tag)
        record=q('A neutral question');record['tags'].append('custom:semantic:location-mention:usa')
        self.assertEqual(fun.classify(record)['outcome'],'candidate')

    def test_senators_and_answer_lists(self):
        self.assertEqual(fun.classify(q('What future senator was the first Ph.D. on the moon?'))['outcome'],'exclude')
        self.assertEqual(fun.classify(q('Who led the US Senate?'))['outcome'],'exclude')
        record=q('Which countries?', ['Russia, Ukraine, Belarus','Russia, Poland, Belarus','Ukraine, Poland, Latvia','Poland, Latvia, Estonia'])
        self.assertEqual(fun.classify(record)['outcome'],'hold')
        self.assertTrue(fun.multiple_item_choices(['Red and blue','Green and blue','Red and green','Black and white']))
        self.assertTrue(fun.multiple_item_choices(['А та Б','Б та В','В та Г','Г та Д']))
        self.assertFalse(fun.multiple_item_choices(['New Zealand','South Africa','United Kingdom','South Korea']))
        self.assertFalse(fun.multiple_item_choices(['Earth','Mars','Jupiter','Saturn and Neptune']))

if __name__=='__main__':unittest.main()
