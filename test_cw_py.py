import unittest
from cw_py import valid_range


class MyTest(unittest.TestCase):
    def test_true(self):
        result = valid_range(50, 250, 70)
        self.assertTrue(result)

    def test_false_1(self):
        result = valid_range(50, 250, 40)
        self.assertFalse(result)

    def test_false_2(self):
        result = valid_range(50, 250, 270)
        self.assertFalse(result)

    def test_equal_min(self):
        result = valid_range(50, 250, 50)
        self.assertTrue(result)

    def test_equal_max(self):
        result = valid_range(50, 250, 250)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
