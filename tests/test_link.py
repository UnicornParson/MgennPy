import unittest
import mcore as mc

from common import *

class TestLink(unittest.TestCase):
    def test_valid_id(self):
        link = mc.Link()
        self.assertEqual(link.id(), MgennConsts.NULL_ID)