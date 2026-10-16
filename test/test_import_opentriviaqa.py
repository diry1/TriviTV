import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('importer', Path(__file__).parents[1] / 'scripts/import_opentriviaqa.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def record(prompt='Which animal is a mammal?', correct='Whale', options=None):
    options = options or ['Whale', 'Trout', 'Robin', 'Ant']
    return importer.parse('#Q ' + prompt + '\n^ ' + correct + '\n' + '\n'.join(f'{chr(65+i)} {c}' for i, c in enumerate(options)), 'animals')[0]


class ImportTests(unittest.TestCase):
    def test_entities_unicode_and_original_correct_answer(self):
        q, reason = importer.normalize(record('Which item is labelled &quot;A &amp; B&quot;?', 'A & B', ['A & B', 'C', 'D', 'E']))
        self.assertIsNone(reason)
        self.assertIn('"A & B"', q['text'])
        self.assertEqual(q['choices'][q['correct']], 'A & B')

    def test_insufficient_choices_bad_keys_and_meta_options_are_rejected(self):
        self.assertEqual(importer.normalize(record(options=['True', 'False']))[1], 'fewer-than-four-choices')
        self.assertEqual(importer.normalize(record(correct='Missing'))[1], 'answer-not-in-choices')
        self.assertEqual(importer.normalize(record(options=['Whale', 'Whale', 'Ant', 'Trout']))[1], 'duplicate-choices')
        self.assertEqual(importer.normalize(record(options=['Whale', 'Trout', 'Ant', 'All of the above']))[1], 'position-dependent-options')
        self.assertEqual(importer.normalize(record(options=['Whale', 'Trout', 'Ant', 'All of them']))[1], 'position-dependent-options')

    def test_extra_choices_keep_four_source_options_without_fabricating(self):
        choices = ['Ant', 'Trout', 'Robin', 'Spider', 'Whale']
        q, reason = importer.normalize(record(options=choices))
        self.assertIsNone(reason)
        self.assertEqual(len(q['choices']), 4)
        self.assertEqual(q['choices'][0], 'Whale')
        self.assertTrue(set(q['choices']) <= set(choices))

    def test_unusable_media_time_sensitive_and_corrupt_encoding(self):
        self.assertEqual(importer.normalize(record('Which animal is pictured here?'))[1], 'missing-media')
        self.assertEqual(importer.normalize(record('Who is currently the record holder?'))[1], 'time-sensitive')
        bad = b'Which animal is caf\xe9?'.decode('utf-8', errors='surrogateescape')
        self.assertEqual(importer.normalize(record(bad))[1], 'invalid-source-encoding')

    def test_region_cues_are_explicit_and_language_is_not_europe(self):
        self.assertEqual(importer.region('Which river flows through Vienna?'), 'Europe')
        self.assertEqual(importer.region('Which river flows past Washington?'), 'US')
        self.assertEqual(importer.region('What is the English word for a feline?'), 'Unclassified')
        self.assertEqual(importer.region('Which South American country is largest?'), 'Unclassified')
        self.assertEqual(importer.region('Which American city is twinned with London?'), 'Unclassified')

    def build(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        for name, content in files.items(): (root / name).write_text(content)
        config = {'revision': 'pinned', 'license': 'CC-BY-SA-4.0', 'categoryMap': {f: ('Animals' if f == 'animals' else 'General Knowledge') for f in files},
                  'sourceHashes': {f: hashlib.sha256((root / f).read_bytes()).hexdigest() for f in files}}
        return root, config

    def test_dedup_prefers_topics_and_preserves_all_record_provenance(self):
        text = '#Q Which animal is a mammal?\n^ Whale\nA Whale\nB Trout\nC Robin\nD Ant\n'
        root, config = self.build({'animals': text, 'newest': text})
        questions, manifest, rejected = importer.build(root, config)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]['category'], 'Animals')
        self.assertEqual(len(questions[0]['source']['records']), 2)
        self.assertEqual(manifest['duplicateRecordsMerged'], 1)
        self.assertIsNone(questions[0]['difficulty'])
        self.assertEqual(rejected, [])
        self.assertEqual(importer.build(root, config), (questions, manifest, rejected))

    def test_conflicting_answer_keys_and_tampered_sources_fail(self):
        text = '#Q Which animal is a mammal?\n^ Whale\nA Whale\nB Trout\nC Robin\nD Ant\n'
        root, config = self.build({'animals': text, 'newest': text.replace('^ Whale', '^ Trout')})
        questions, manifest, rejected = importer.build(root, config)
        self.assertEqual(questions, [])
        self.assertEqual(manifest['rejectedCount'], 2)
        self.assertTrue(all(r['reason'] == 'conflicting-correct-answers' for r in rejected))
        (root / 'animals').write_text(text + '\n')
        with self.assertRaisesRegex(ValueError, 'checksums'): importer.build(root, config)


if __name__ == '__main__': unittest.main()
