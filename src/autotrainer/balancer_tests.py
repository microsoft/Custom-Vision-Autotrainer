
import os
import unittest

from autotrainer.custom_vision.custom_vision_client import CustomVisionClient
from autotrainer.custom_vision.domain import Domain
from autotrainer.custom_vision.classification_type import ClassificationType

from autotrainer.custom_vision.balancer import Balancer
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

test_set = [ ImageUrlCreateEntry(url="", tag_ids=[ "one" ] ), 
     ImageUrlCreateEntry(url="", tag_ids=[ "two" ] ),  
     ImageUrlCreateEntry(url="", tag_ids=[ "two" ] ),  
     ImageUrlCreateEntry(url="", tag_ids=[ "three" ] ),  
     ImageUrlCreateEntry(url="", tag_ids=[ "three" ] ),  
     ImageUrlCreateEntry(url="", tag_ids=[ "three" ] ),  
     ImageUrlCreateEntry(url="", tag_ids=[ "five" ] ),
     ImageUrlCreateEntry(url="", tag_ids=[ "five" ] ),
     ImageUrlCreateEntry(url="", tag_ids=[ "five" ] ),
     ImageUrlCreateEntry(url="", tag_ids=[ "five" ] ),
     ImageUrlCreateEntry(url="", tag_ids=[ "five" ] ),
     ]

class BalancerTests(unittest.TestCase):
     def test_balance_set(self):
          balancer = Balancer(test_set, 1)
          result = balancer.apply()
          self.assertEqual(1 , sum("one" in p.tag_ids for p in result) )
          self.assertEqual(1 , sum("two" in p.tag_ids for p in result) )
          self.assertEqual(1 , sum("three" in p.tag_ids for p in result) )
          self.assertEqual(1 , sum("five" in p.tag_ids for p in result) )

          balancer = Balancer(test_set, 2)
          result = balancer.apply()
          self.assertEqual(0 , sum("one" in p.tag_ids for p in result) )
          self.assertEqual(2 , sum("two" in p.tag_ids for p in result) )
          self.assertEqual(2 , sum("three" in p.tag_ids for p in result) )
          self.assertEqual(2 , sum("five" in p.tag_ids for p in result) )

          balancer = Balancer(test_set, 5)
          result = balancer.apply()
          self.assertEqual(0 , sum("one" in p.tag_ids for p in result) )
          self.assertEqual(0 , sum("two" in p.tag_ids for p in result) )
          self.assertEqual(0 , sum("three" in p.tag_ids for p in result) )
          self.assertEqual(5 , sum("five" in p.tag_ids for p in result) )