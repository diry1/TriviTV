import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('eu_builder', ROOT / 'scripts/build_eu_eligibility.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class EuropeRuleTests(unittest.TestCase):
    def rules(self, text, choices=None, language='en', category='General Knowledge'):
        q = {'text': text, 'choices': choices or ['Alpha', 'Beta', 'Gamma', 'Delta'], 'category': category}
        return {r for hit in builder.rule_matches(q, language) for r in hit['rules']}

    def test_league_person_without_league_keyword(self):
        self.assertIn('EU01', self.rules('How many rings does Tom Brady have?'))

    def test_president_possessive_and_unrelated_distractor(self):
        self.assertIn('EU04', self.rules('What was George Washingtons first occupation?'))
        self.assertNotIn('EU04', self.rules('Who painted this work?', ['George Washington', 'Picasso', 'Dali', 'Monet']))

    def test_country_geography_is_not_country_music(self):
        self.assertNotIn('EU07', self.rules('What country is Berlin in?'))
        self.assertIn('EU07', self.rules('Which country singer played this role?'))

    def test_dates_and_quantities_and_missing_media(self):
        self.assertIn('Q02', self.rules('In what year did it happen?', ['1991', '1992', '1993', '1994']))
        self.assertIn('Q02', self.rules('How many stomachs does a starfish have?'))
        self.assertIn('Q04', self.rules('This is the victory theme to which game?'))

    def test_units_shared_and_wordplay_scoped(self):
        self.assertIn('EU09', self.rules('How tall is the statue in feet?'))
        self.assertIn('UA04', self.rules('How tall is the statue in feet?', language='uk'))
        self.assertIn('UA03', self.rules('What is the English word in this anagram?', language='uk'))
        self.assertNotIn('UA03', self.rules('What is the English word in this anagram?'))


if __name__ == '__main__':
    unittest.main()
