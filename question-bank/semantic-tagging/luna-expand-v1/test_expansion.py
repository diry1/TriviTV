import collections,importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
sp=importlib.util.spec_from_file_location('expand',Path(__file__).with_name('expand.py'));e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
class ExpansionChecks(unittest.TestCase):
 def test_selection_is_balanced_until_exhaustion(self):
  rows=e.c.load(e.HERE/'selection.json');coverage=collections.Counter(e.c.load(e.HERE/'manifest.json')['initialCoverage']);left=collections.Counter(q['category'] for q in rows)
  for q in rows:
   self.assertEqual(coverage[q['category']],min(coverage[c] for c,n in left.items() if n));coverage[q['category']]+=1;left[q['category']]-=1
  self.assertEqual(sum(coverage.values()),38926)
 def test_no_reclassification(self):
  rows=e.c.load(e.HERE/'selection.json');ids={q['id'] for q in rows};known={q['id'] for q in e.c.load(e.HERE.parent/'luna-balanced-v1/selection.json')}|set(e.c.load(e.ROOT/'question-bank/tag-sources/semantic-pilot-v1.json'));self.assertEqual(len(rows),len(ids));self.assertFalse(ids&known)
 def test_budget_is_remainder_not_new_five_dollars(self):self.assertEqual(e.c.LIMIT+e.prior_cost,5);self.assertLess(e.c.LIMIT,5)
 def test_counter_preserves_gaps_and_repair_names(self):self.assertEqual(e.next_number({'continue-0001':{},'continue-0099-repair-0':{}}),100)
 def test_budget_tail_keeps_progress(self):
  self.assertFalse(e.budget_exhausted(1,10,13));self.assertTrue(e.budget_exhausted(1,10,10));self.assertFalse(e.budget_exhausted(5,10,10))
 def test_targeted_missing_id_repair(self):
  calls=[]
  def fake_request(name,rows):
   calls.append([r['id'] for r in rows]);items=[{'id':r['id']} for r in rows];items=items[:1] if len(calls)==1 else items
   return {'status':'completed','id':name,'output':[{'content':[{'type':'output_text','text':json.dumps({'records':items})}]}]}
  def fake_unpack(response,rows):return [{'id':q['id']} for q in rows]
  with patch.object(e.c,'request',fake_request),patch.object(e.c,'unpack',fake_unpack):result=e.classified_chunk('mock',[{'id':'a'},{'id':'b'}])
  self.assertEqual(calls,[['a','b'],['b']]);self.assertEqual(result[0]['responseId'],'mock');self.assertEqual(result[1]['responseId'],'mock-repair-0')
if __name__=='__main__':unittest.main()
