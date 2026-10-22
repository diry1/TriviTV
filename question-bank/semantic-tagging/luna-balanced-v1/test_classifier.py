import importlib.util,unittest,json
from pathlib import Path
p=Path('question-bank/semantic-tagging/luna-balanced-v1/classify.py');spec=importlib.util.spec_from_file_location('classifier',p);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class Checks(unittest.TestCase):
 def test_cost(self):self.assertAlmostEqual(c.cost({'input_tokens':1000000,'input_tokens_details':{'cached_tokens':500000},'output_tokens':1000000}),.555)
 def test_budget_unknown_reservations(self):self.assertAlmostEqual(c.charge_total({'requests':{'a':{'reservedUsd':2,'costUsd':.3},'b':{'reservedUsd':4}}}),4.3)
 def test_bound(self):self.assertGreater(c.reserve_bound({'max_output_tokens':1000,'input':'x'*1000}),.0005)
 def test_vocabulary(self):self.assertTrue(c.valid_tag('era:1990s'));self.assertFalse(c.valid_tag('era:1999s'));self.assertFalse(c.valid_tag('subject:film-characters'));self.assertTrue(c.valid_tag('subject:screen-characters'))
 def test_cache_write_cost(self):self.assertAlmostEqual(c.cost({'input_tokens':1000000,'input_tokens_details':{'cache_write_tokens':1000000},'output_tokens':0}),.125)
 def test_evidence_hold(self):
  q={'id':'example','category':'Animals','text':'Which animal is this?','choices':['Cat','Dog','Bird','Fish'],'correct':0,'ukrainian':None,'sourceFingerprint':'s','translationFingerprint':None}
  row={'id':'example','tags':[{'tag':'topic:animals','evidence':'animal','confidence':'high'},{'tag':'location-mention:usa','evidence':'Cat','confidence':'high'},{'tag':'style:humor','evidence':'invented text','confidence':'high'}],'entities':[],'eras':[],'notes':[],'proposals':[]}
  response={'id':'mock','status':'completed','output':[{'content':[{'type':'output_text','text':json.dumps({'records':[row]})}]}]}
  parsed=c.unpack(response,[q])[0];self.assertEqual([t['tag'] for t in parsed['assignments']],['topic:animals']);self.assertEqual(len(parsed['proposals']),2)
 def test_selection(self):
  rows=c.load(c.HERE/'selection.json');counts=c.collections.Counter(q['category'] for q in rows);self.assertEqual(len({q['id'] for q in rows}),2500);self.assertEqual(set(counts.values()),{125});self.assertEqual(len(counts),20)
 def test_refuse_partial(self):
  with self.assertRaises(AssertionError):c.unpack({'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'}},[])
unittest.main()
