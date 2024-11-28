import unittest
import mcore as mc

from common import *

class TestOutput(unittest.TestCase):
    def test_valid_id(self):
        o = mc.Output()
        self.assertEqual(o.id(), MgennConsts.NULL_ID)

    def test_keys(self):
        o = mc.Output()
        k = o.required_keys()
        self.assertIsInstance(k, list)
        self.assertEqual(len(k), 2)

    def __make_data(self):
        return  {
          "id": 33,
          "name": "name_gggg"
        }

    def test_deserialize(self):
        data  = self.__make_data()
        o = mc.Output()
        o.deserialize(data)
        self.assertEqual(o.id(), 33)
        self.assertEqual(o.localId, 33)
        self.assertEqual(o.name, "name_gggg")

    def test_serialize(self):
        orig = mc.Output()
        self.assertNotEqual(orig, None)
        self.assertNotEqual(None, orig)
        oid = mc.F.generateOID()
        orig.localId = oid
        data = orig.serialize()
        self.assertTrue(bool(data))
        o = mc.Output()
        o.deserialize(data)
        self.assertEqual(o, orig)

    def test_signals(self):
        o = mc.Output()
        signals = [0.1, 0.3, 0.5, 99., 12., 12.3, 78945.33]
        self.assertEqual(o.value, 0.)
        for s in signals:
            o.onSignal(tick_num = 3, amplitude = s, from_id = mc.F.generateOID())
        rc = o.onTick(3)
        self.assertEqual(rc, sum(signals))
        self.assertEqual(o.value, 0.)
