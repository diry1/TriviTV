import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('translate_questions', ROOT / 'scripts/translate_questions.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TranslationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {q['id']:q for q in json.loads(module.BANK.read_text())}
        cls.revision = json.loads((module.BANK.parent / 'manifest.json').read_text())['source']['revision']

    def document(self):
        result = json.loads(module.TARGET.read_text())
        result['questions'] = result['questions'][:1]
        return result

    def test_invalid_choices_and_stale_sources_are_rejected(self):
        for field, value in [('choices',['Те саме']*4),('sourceHash','stale'),('correct',0),('text','English only')]:
            document = self.document()
            document['questions'][0][field] = value
            with self.assertRaises(ValueError):
                module.validate(document, self.source, self.revision)

    def test_exclusions_cannot_skip_unknown_or_stale_source_ids(self):
        document = self.document()
        row = document['questions'].pop()
        document['excluded'] = [{'id':row['id'],'sourceHash':row['sourceHash'],'reason':'English wordplay'}]
        self.assertEqual(module.validate(document,self.source,self.revision),set())
        document['excluded'][0]['sourceHash'] = 'stale'
        with self.assertRaises(ValueError):
            module.validate(document,self.source,self.revision)

    def test_atomic_replace_failure_keeps_previous_translation_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'uk.json'
            target.write_text('previous valid data')
            document = self.document()
            with patch.object(module,'TARGET',target), patch.object(module.Path,'replace',side_effect=OSError('disk problem')):
                with self.assertRaises(OSError):
                    module.save(document)
            self.assertEqual(target.read_text(),'previous valid data')

    def test_validation_does_not_contact_a_translation_service(self):
        with patch.object(module.urllib.request,'urlopen',side_effect=AssertionError('unexpected network')):
            document = self.document()
            self.assertEqual(module.validate(document,self.source,self.revision),{document['questions'][0]['id']})

if __name__ == '__main__':
    unittest.main()
