import unittest
import mcore as mc

from common import *

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