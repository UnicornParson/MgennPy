import unittest
import mcore as mc

from common import F
class TestF(unittest.TestCase):
    def test_d_eq(self):
        a = {"a":1,"b":2,"c":1,"d":2}
        b = {"a":1,"b":2,"c":1,"d":2}
        c = {"a":1,"b":2,"c":3,"d":2}
        d = {"a":1,"b":2,"c":3,"d":2, "e":{"a":1,"b":2,"c":1,"d":2}}
        d2 = {"a":1,"b":2,"c":3,"d":2, "e":{"a":1,"b":2,"c":1,"d":2}}
        e = {"a":1,"b":2,"c":3,"d":2, "e":{"a":1,"b":2,"c":2,"d":2}}
        self.assertTrue(F.d_eq(a, a))
        self.assertTrue(F.d_eq(d, d))
        self.assertTrue(F.d_eq(e, e))
        self.assertTrue(F.d_eq(None, None, maybe_none=True))
        self.assertFalse(F.d_eq(a, None, maybe_none=True))
        self.assertTrue(F.d_eq(None, None, maybe_none=True))
        self.assertFalse(F.d_eq(None, a, maybe_none=True))
        self.assertTrue(F.d_eq(a, b))
        self.assertTrue(F.d_eq(b, a))
        self.assertFalse(F.d_eq(a, c))
        self.assertFalse(F.d_eq(b, c))
        self.assertFalse(F.d_eq(c, a))
        self.assertFalse(F.d_eq(c, b))
        self.assertFalse(F.d_eq(c, d))
        self.assertFalse(F.d_eq(d, c))
        self.assertTrue(F.d_eq(d, d2))
        self.assertFalse(F.d_eq(d, e))
        self.assertFalse(F.d_eq(d2, e))
