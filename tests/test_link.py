import unittest
import mcore as mc

from common import *
'''
        self.finalAmplitude = 0.
        self.tick = 0
        self.from_id = 0
'''

'''
      "links": [
        {
          "attenuationPerTick": "0.020000",
          "events": [],
          "id": 10,
          "length": 2,
          "receiverId": 64
        },
    def reset(self):
        self.localId = MgennConsts.NULL_ID
        self.events = []
        self.apt = 0.
        self.length = 0
        self.receiverId = 0
        
         '''


class TestLink(unittest.TestCase):
    def test_valid_id(self):
        link = mc.Link()
        self.assertEqual(link.id(), MgennConsts.NULL_ID)

    def test_keys(self):
        link = mc.Link()
        k = link.required_keys()
        self.assertIsInstance(k, list)
        self.assertEqual(len(k), 4)

    def test_LinkEvent(self):
        le1 = mc.LinkEvent()
        le1.finalAmplitude = 99.
        le1.tick = 88
        le2 = le1.clone()
        self.assertEqual(le2, le1)
        le2.from_id = 77 # dynamic info. cam be ignored
        self.assertEqual(le2, le1)
        le1.tick = 66
        self.assertNotEqual(le2, le1)
    
    def __make_link(self):
        link = mc.Link()
        link.localId = 33
        link.apt = 44.1
        link.length = 33
        link.receiverId = 22
        for t in range(10, 50):
            e = mc.LinkEvent()
            e.tick = t
            e.finalAmplitude = t * 2.0
            e.from_id = t + 2
            link.events.append(e)
        return link

    def test_deserialize(self):
        data  = self.__make_data()
        link = mc.Link()
        link.deserialize(data)
        self.assertEqual(link.apt, 0.02)
        self.assertEqual(link.length, 2)
        self.assertEqual(link.receiverId, 64)
        self.assertEqual(link.events, [])

    def test_serialize(self):
        orig = self.__make_link()
        data = orig.serialize()
        self.assertTrue(bool(data))
        link = mc.Link()
        link.deserialize(data)
        self.assertEqual(link, orig)

    def test_signals(self):
        pass
    def __make_data(self):
        return  {
          "attenuationPerTick": "0.020000",
          "events": [],
          "id": 10,
          "length": 2,
          "receiverId": 64
        }