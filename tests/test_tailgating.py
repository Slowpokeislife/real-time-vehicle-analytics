import unittest
from src.tailgating import Box,is_potential_tailgating,frame_flag
from src.analyze_log import episodes,summarize
class TailgatingTests(unittest.TestCase):
    def test_rule_true(self):self.assertTrue(is_potential_tailgating(Box(300,390,500,300),1280,720))
    def test_strict_boundaries(self):self.assertFalse(is_potential_tailgating(Box(0,0,384,648),1280,720))
    def test_not_vehicle(self):self.assertEqual(frame_flag([Box(0,400,600,300,'person')],1280,720),0)
    def test_multiple_objects_one_flag(self):
        boxes=[Box(0,0,100,100),Box(300,400,450,300),Box(350,390,500,300)]
        self.assertEqual(frame_flag(boxes,1280,720),1)
    def test_contiguous_episodes(self):self.assertEqual(episodes([0,1,1,0,1]),[(1,2),(4,4)])
    def test_summary(self):
        s=summarize([0,1,1,0],2);self.assertEqual(s['flagged_percentage'],50)
        self.assertEqual(s['flagged_duration_seconds'],1)
if __name__=='__main__':unittest.main()
