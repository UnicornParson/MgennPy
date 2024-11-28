import unittest
import mcore as mc

from common import *

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
        link.localId = mc.F.generateOID()
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
        self.assertEqual(link.localId, 333)

    def test_serialize(self):
        orig = self.__make_link()
        self.assertNotEqual(orig, None)
        self.assertNotEqual(None, orig)
        data = orig.serialize()
        self.assertTrue(bool(data))
        link = mc.Link()
        link.deserialize(data)
        self.assertEqual(link, orig)

    def test_too_small_signall(self):
        l = mc.Link()
        l.localId = mc.F.generateOID()
        l.apt = 0.1
        l.length = 10
        for i in range(99):
            l.onSignal(tick_num = 1, amplitude = 1., from_id=i) ## too small
            self.assertEqual(len(l.events), 0)
        for i in range(99):
            rc = l.onTick(i)
            self.assertEqual(rc, 0.0)

    def test_signals(self):
        l = mc.Link()
        l.localId = mc.F.generateOID()
        l.apt = 0.1
        l.length = 100
        initial = 10
        last_t = 0
        for i in range(initial, 99):
            l.onSignal(tick_num = i, amplitude = (1. + float(i)), from_id=i)
        for i in range(initial, 99):
            rc = l.onTick(l.length+i)
            last_t = l.length+i
            self.assertEqual(rc, (float(i-initial)+1.))
        self.assertEqual(len(l.events), 0)
        for i in range(last_t, last_t+99):
            rc = l.onTick(i)

    def __make_data(self):
        return  {
          "attenuationPerTick": "0.020000",
          "events": [],
          "id": mc.F.generateOID(),
          "length": 2,
          "receiverId": 64,
          "id": 333
        }