import unittest
from cancellation import cancellation_fee


class Contract(unittest.TestCase):
    def test_interval_boundaries_and_integer_rounding(self):
        for hours in [0, 23, 24, 47, 48, 1000]:
            for paid in [0, 1, 7, 103, 10**30 + 3]:
                expected = 0 if hours >= 48 else paid // (4 if hours >= 24 else 2)
                with self.subTest(hours=hours, paid=paid):
                    self.assertEqual(cancellation_fee(hours, paid), expected)

    def test_negative_inputs(self):
        for hours, paid in [(-1, 0), (0, -1)]:
            with self.subTest(hours=hours, paid=paid), self.assertRaises(ValueError):
                cancellation_fee(hours, paid)
