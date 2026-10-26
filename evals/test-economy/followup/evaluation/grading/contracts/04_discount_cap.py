import unittest
from discounts import discounted_total


class Contract(unittest.TestCase):
    def test_old_and_new_calls(self):
        for subtotal in [0, 17, 107, 2001]:
            for percent in [0, 1, 27, 100]:
                computed = (subtotal * percent) // 100
                with self.subTest(subtotal=subtotal, percent=percent, limit="omitted"):
                    self.assertEqual(discounted_total(subtotal, percent), subtotal - computed)
                for cap in [None, 0, 1, computed, computed + 1]:
                    expected = subtotal - (computed if cap is None else min(cap, computed))
                    with self.subTest(subtotal=subtotal, percent=percent, cap=cap):
                        self.assertEqual(discounted_total(subtotal, percent, max_discount_cents=cap), expected)

    def test_validation(self):
        for subtotal, percent, cap in [(-1, 10, None), (10, -1, 1), (10, 101, 1), (0, 0, -1), (10, 10, -3), (-2, 27, 0), (17, -1, 0), (17, 101, 0)]:
            with self.subTest(subtotal=subtotal, percent=percent, cap=cap), self.assertRaises(ValueError):
                discounted_total(subtotal, percent, max_discount_cents=cap)

    def test_limit_cannot_be_positional(self):
        with self.assertRaises(TypeError):
            discounted_total(100, 20, 5)
