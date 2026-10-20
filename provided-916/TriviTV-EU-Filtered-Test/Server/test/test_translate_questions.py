import importlib.util
import json
import io
import os
import sys
from contextlib import redirect_stdout
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

class TranslationBudgetTests(unittest.TestCase):
    setUpClass = TranslationWorkflowTests.__dict__["setUpClass"]
    document = TranslationWorkflowTests.document
    def test_stratified_trial_samples_all_categories_and_skips_completed(self):
        source = list(self.source.values())
        chosen = module.pending_questions(source, set(), set(), 100, True)
        self.assertEqual(len(chosen), 100)
        self.assertEqual(len({q['category'] for q in chosen}), 20)
        counts = {category: sum(q['category'] == category for q in chosen) for category in {q['category'] for q in chosen}}
        self.assertTrue(all(n == 5 for n in counts.values()))
        excluded = {q['id'] for q in chosen[:50]}
        self.assertTrue(all(q['id'] not in excluded for q in module.pending_questions(source, excluded, set(), 100, True)))

    def test_budget_survives_restart_and_refuses_next_request(self):
        from decimal import Decimal
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'usage.json'
            ledger = module.load_usage(path)
            row = module.reserve_request(ledger, path, 'gpt-4.1-mini', b'{}', 1000, Decimal('0.01'))
            module.record_usage(ledger,path,row,{'usage':{'prompt_tokens':100,'completion_tokens':200}})
            restored = module.load_usage(path)
            self.assertEqual(module.used_budget(restored), Decimal('0.00036'))
            with self.assertRaises(SystemExit):
                module.reserve_request(restored,path,'gpt-4.1-mini',b'{}',1000,Decimal('0.0005'))
            self.assertEqual(len(module.load_usage(path)['requests']),1)

    def test_usage_lock_rejects_concurrent_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'usage.json'
            with module.usage_lock(path):
                with self.assertRaises(SystemExit):
                    with module.usage_lock(path):
                        self.fail('Second run must not enter')
            self.assertFalse(Path(str(path)+'.lock').exists())

    def test_incomplete_or_invalid_output_is_billed_before_rejection(self):
        for reason,choices in [('length',['Один','Два','Три','Чотири']),('stop',['Один']*4)]:
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as folder:
                target=Path(folder)/'uk.json'
                doc=self.document()
                target.write_text(json.dumps(doc,ensure_ascii=False),encoding='utf-8')
                next_id=next(id for id in self.source if id != doc['questions'][0]['id'])
                content={'questions':[{'id':next_id,'text':'Тестове запитання','choices':choices}],'excluded':[]}
                response={'id':'test-response','usage':{'prompt_tokens':100,'completion_tokens':200},
                    'choices':[{'finish_reason':reason,'message':{'content':json.dumps(content,ensure_ascii=False)}}]}
                usage=Path(folder)/'usage.json'
                argv=['translate_questions.py','--translate','--limit','1','--usage-file',str(usage)]
                with patch.object(module,'TARGET',target), patch.object(sys,'argv',argv), patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}), patch.object(module.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(response).encode())) as request, redirect_stdout(io.StringIO()):
                    with self.assertRaises((SystemExit,ValueError)):
                        module.main()
                self.assertEqual(request.call_count,1)
                sent=json.loads(request.call_args.args[0].data)
                payload=json.loads(sent['messages'][1]['content'])
                self.assertNotIn('correct',payload[0])
                self.assertEqual(payload[0]['choices'],self.source[next_id]['choices'])
                self.assertEqual(module.load_usage(usage)['requests'][0]['state'],'complete')
                self.assertEqual(json.loads(target.read_text(encoding='utf-8')),doc)

    def test_successful_runs_resume_without_retranslating_and_accumulate_usage(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'uk.json'
            initial=self.document()
            target.write_text(json.dumps(initial),encoding='utf-8')
            usage=Path(folder)/'usage.json'
            ids=[]
            def reply(request, **kwargs):
                payload=json.loads(json.loads(request.data)['messages'][1]['content'])
                id=payload[0]['id']
                ids.append(id)
                result={'questions':[{'id':id,'text':'Тестове запитання','choices':['Один','Два','Три','Чотири']}],'excluded':[]}
                return io.BytesIO(json.dumps({'usage':{'prompt_tokens':100,'completion_tokens':200},'choices':[{'finish_reason':'stop','message':{'content':json.dumps(result)}}]}).encode())
            argv=['translate_questions.py','--translate','--limit','1','--usage-file',str(usage)]
            with patch.object(module,'TARGET',target),patch.object(sys,'argv',argv),patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}),patch.object(module.urllib.request,'urlopen',side_effect=reply),redirect_stdout(io.StringIO()):
                module.main()
                module.main()
            self.assertEqual(len(set(ids)),2)
            result=json.loads(target.read_text(encoding='utf-8'))
            self.assertEqual(len(result['questions']),len(initial['questions'])+2)
            self.assertTrue(all('correct' not in q for q in result['questions']))
            self.assertEqual(len(module.load_usage(usage)['requests']),2)
            self.assertEqual(str(module.used_budget(module.load_usage(usage))),'0.00072')

    def test_budget_prevents_network_request(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'uk.json'
            target.write_text(json.dumps(self.document()),encoding='utf-8')
            argv=['translate_questions.py','--translate','--limit','1','--budget-usd','0.000001','--usage-file',str(Path(folder)/'usage.json')]
            with patch.object(module,'TARGET',target),patch.object(sys,'argv',argv),patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}),patch.object(module.urllib.request,'urlopen') as request:
                with self.assertRaises(SystemExit):
                    module.main()
                request.assert_not_called()

    def test_failed_request_keeps_reservation_without_spending_again(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'uk.json'
            target.write_text(json.dumps(self.document()),encoding='utf-8')
            usage=Path(folder)/'usage.json'
            argv=['translate_questions.py','--translate','--limit','1','--usage-file',str(usage)]
            with patch.object(module,'TARGET',target),patch.object(sys,'argv',argv),patch.dict(os.environ,{'OPENAI_API_KEY':'test-only'}),patch.object(module.urllib.request,'urlopen',side_effect=TimeoutError()):
                with self.assertRaises(SystemExit):
                    module.main()
            restored=module.load_usage(usage)
            self.assertEqual(restored['requests'][0]['state'],'reserved')
            self.assertGreater(module.used_budget(restored),0)

if __name__ == '__main__':
    unittest.main()
