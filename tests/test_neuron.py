import unittest
import mcore as mc

class TestNeuron(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(5, 5)

    def test_add_negative_numbers(self):
        self.assertEqual(5, -5)

    def test_add_mixed_numbers(self):
        self.assertEqual(5, 1)

if __name__ == '__main__':
    unittest.main()