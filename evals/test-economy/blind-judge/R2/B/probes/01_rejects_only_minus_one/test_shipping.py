import unittest
from shipping import delivery_fee


class ShippingTests(unittest.TestCase):
    def test_standard_fee_below_5000_cents(self):
        for subtotal in (0, 1200, 4999):
            with self.subTest(subtotal_cents=subtotal):
                self.assertEqual(delivery_fee(subtotal), 500)

    def test_reduced_fee_from_5000_through_9999_cents(self):
        for subtotal in (5000, 7500, 9999):
            with self.subTest(subtotal_cents=subtotal):
                self.assertEqual(delivery_fee(subtotal), 250)

    def test_free_delivery_from_10000_cents(self):
        for subtotal in (10000, 20000):
            with self.subTest(subtotal_cents=subtotal):
                self.assertEqual(delivery_fee(subtotal), 0)

    def test_negative_subtotals_are_rejected(self):
        for subtotal in (-1, -200):
            with self.subTest(subtotal_cents=subtotal):
                with self.assertRaises(ValueError):
                    delivery_fee(subtotal)
