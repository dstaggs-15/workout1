import json,tempfile,unittest
from pathlib import Path
from analyzer.build_site import profile_read,build
class ProfileTests(unittest.TestCase):
 def test_profile_units(self):
  p=profile_read('height_inches=69\nweigh_in=2026-10-01,165,lb\nweigh_in=2026-10-02,75,kg')
  self.assertEqual(p['height_inches'],69);self.assertEqual(p['weights'][0]['weight_lb'],165);self.assertAlmostEqual(p['weights'][1]['weight_lb'],165.346696635)
 def test_history_preserves_changes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'source').mkdir();(root/'source/workout.csv').write_text('start_time,end_time,exercise_title,set_index,set_type,weight_lbs,reps\n"Sep 30, 2026, 8:00 PM","Sep 30, 2026, 9:00 PM",Bench Press,0,normal,100,8\n')
   p=root/'source/profile.txt';p.write_text('height_inches=69\nweigh_in=2026-10-01,165,lb');build(root);build(root)
   p.write_text('height_inches=69\nweigh_in=2026-10-01,167,lb');build(root)
   history=json.loads((root/'source/history/profile_history.json').read_text());self.assertEqual(len(history),2);self.assertEqual(history[0]['profile']['weights'][0]['weight_lb'],165);self.assertEqual(history[1]['profile']['weights'][0]['weight_lb'],167)
