import unittest
import mcore as mc

from common import *


class TestTapeInputsBatch(unittest.TestCase):
    def test_serialize(self):
        tape = mc.TapeInputsBatch()
        points = {
            "Alias1":{"type":"tape","name":"Alias1","receivers":[11],"args":{"components":[]}},
            "Alias2":{"type":"tape","name":"Alias2","receivers":[12],"args":{"components":[]}},
            "Alias3":{"type":"tape","name":"Alias3","receivers":[13],"args":{"components":[]}},
            "Alias4":{"type":"tape","name":"Alias4","receivers":[14],"args":{"components":[]}},
            "Alias5":{"type":"tape","name":"Alias5","receivers":[15],"args":{"components":[]}},
            "Alias6":{"type":"tape","name":"Alias6","receivers":[16],"args":{"components":[]}},
            "Alias7":{"type":"tape","name":"Alias7","receivers":[17],"args":{"components":[]}},
            "Alias8":{"type":"tape","name":"Alias8","receivers":[18],"args":{"components":[]}},
            "Alias9":{"type":"tape","name":"Alias9","receivers":[19],"args":{"components":[]}}
        }
        for name, p in points.items():
            self.assertFalse(name in tape)
            self.assertFalse(name in tape.point_names())
            tape.addPoint(p)
            self.assertTrue(name in tape)
            self.assertTrue(name in tape.point_names())
        
        self.assertEqual(len(points), len(tape))
        dump = tape.dump()
        self.assertEqual(len(points), len(dump))
        for p in dump:
            self.assertTrue(bool(p))
            self.assertTrue("name" in p)
            name = p["name"]
            self.assertTrue(bool(name))
            self.assertTrue(F.d_eq(points[name], p))
        

class TestInputComponent(unittest.TestCase):
    def test_signals(self):
        ic = mc.InputComponent()
        ic.ift = True
        ic.period = 3
        ic.amp = 2.
        expected = [
            (0, 0.),(1, 0.),(2, 0.),(3, 2.),
            (4, 0.),(5, 0.),(6, 2.),(7, 0.),
            # try again. ift ignoed
            (0, 2.),(1, 0.),(2, 0.),(3, 2.),
            (3, 2.),(3, 2.),(3, 2.),(3, 2.),

        ]
        for e in expected:
            self.assertEqual(ic.onTick(e[0]), e[1])

    def test_serialization(self):
        data = {
            mc.InputComponent.PeriodKey : 33,
            mc.InputComponent.IgnoreFirstTickKey : False,
            mc.InputComponent.AmplitudeKey : 22.2
        }
        ic = mc.InputComponent()
        ic.deserialize(data)
        self.assertEqual(ic.ift, False)
        self.assertEqual(ic.period, 33)
        self.assertEqual(ic.amp, 22.2)
        ic = None

        orig = mc.InputComponent()
        orig.ift = True
        orig.period = 3
        orig.amp = 2.
        d = orig.serialize()
        self.assertTrue(bool(d))
        restored = mc.InputComponent()
        restored.deserialize(d)
        self.assertEqual(restored.ift, True)
        self.assertEqual(restored.period, 3)
        self.assertEqual(restored.amp, 2.)

        self.assertEqual(orig, restored)

class TestClockInput(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.receivers = [99,98,97,96,95,11,12]

    def __make_data(self) -> dict:
        return {
            "type": "clockgenerator",
            "name": "Alias1",
            "receivers": self.receivers,
            "args": {
                "components": [
                    {
                        mc.InputComponent.PeriodKey : 2,
                        mc.InputComponent.IgnoreFirstTickKey : False,
                        mc.InputComponent.AmplitudeKey : 1.0
                    },
                    {
                        mc.InputComponent.PeriodKey : 3,
                        mc.InputComponent.IgnoreFirstTickKey : False,
                        mc.InputComponent.AmplitudeKey : 1.0
                    },
                    {
                        mc.InputComponent.PeriodKey : 5,
                        mc.InputComponent.IgnoreFirstTickKey : False,
                        mc.InputComponent.AmplitudeKey : 1.0
                    },
                ]
            }
        }

    def test_serialization(self):
        data = self.__make_data()
        ci = mc.ClockInput()
        ci.deserialize(data)
        self.assertEqual(ci.type, "clockgenerator")
        self.assertEqual(ci.name, "Alias1")
        self.assertEqual(ci.receivers.sort(), self.receivers.sort())
        s_data = ci.serialize()
        self.assertTrue(bool(s_data))
        restored = mc.ClockInput()
        restored.deserialize(s_data)

    def test_signals(self):
        data = self.__make_data()
        ci = mc.ClockInput()
        ci.deserialize(data)
        expected = [3.0, 0.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.0, 1.0, 1.0, 2.0]
        for tick, v in enumerate(expected):
            events = ci.makeEvents(tick)
            if v == 0.0:
                self.assertEqual(len(events), 0)
                continue
            self.assertEqual(len(events), len(self.receivers))
            for e in events:
                self.assertTrue(isinstance(e, tuple))
                self.assertEqual(len(e), 3)
                self.assertEqual(e[1], v)