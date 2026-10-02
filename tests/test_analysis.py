import csv,tempfile,unittest
from pathlib import Path
from analyzer.analyze import analyze
class AnalysisTests(unittest.TestCase):
 def run_report(self,rows,copies=1):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'export.csv'
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['start_time','end_time','exercise_title','set_index','set_type','weight_lbs','reps']);w.writeheader();w.writerows(rows)
   return analyze([p]*copies)
 def row(self,**kw):
  return dict(start_time='Sep 7, 2026, 8:00 PM',end_time='Sep 7, 2026, 9:00 PM',exercise_title='Bench Press (Barbell)',set_index='0',set_type='normal',weight_lbs='100',reps='10',**kw)
 def test_overlap_and_warmup(self):
  a=self.row();b=dict(a,set_index='1',set_type='warmup');r=self.run_report([a,b,{}],2)
  self.assertEqual(r['summary']['sets'],1);self.assertEqual(r['summary']['volume'],1000);self.assertEqual(r['summary']['minutes'],60);self.assertEqual(r['quality']['duplicate_sets_skipped'],2)
 def test_missing_weeks_and_assisted(self):
  a=self.row();b=dict(a,start_time='Sep 21, 2026, 8:00 PM',end_time='Sep 21, 2026, 9:00 PM',exercise_title='Pull Up (Assisted)')
  r=self.run_report([a,b]);self.assertEqual(r['weekly'][1]['sets'],0);self.assertEqual(r['sets'][1]['volume'],0);self.assertIsNone(r['sets'][1]['e1rm'])
 def test_invalid_number_fails(self):
  with self.assertRaises(ValueError):self.run_report([dict(self.row(),weight_lbs='NaN')])
 def test_bodyweight_no_strength_estimate(self):
  r=self.run_report([dict(self.row(),exercise_title='Push Up',weight_lbs='')]);self.assertEqual(r['summary']['sets'],1);self.assertIsNone(r['sets'][0]['e1rm'])
if __name__=='__main__':unittest.main()
