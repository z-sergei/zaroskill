import unittest
from shipping import delivery_fee


class Contract(unittest.TestCase):
    def test_prices_by_published_intervals(self):
        intervals = [(0, 4999, 500), (5000, 9999, 250), (10000, 10**9, 0)]
        for start, end, price in intervals:
            for amount in (start, (start + end) // 2, end):
                with self.subTest(amount=amount):
                    self.assertEqual(delivery_fee(amount), price)

    def test_negative_inputs(self):
        for amount in (-1, -13, -10**6):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                delivery_fee(amount)
