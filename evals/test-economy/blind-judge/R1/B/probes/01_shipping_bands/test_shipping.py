import unittest
from shipping import delivery_fee


class ShippingTests(unittest.TestCase):
    def test_negative_subtotals_are_rejected(self):
        for subtotal in (-1, -200):
            with self.subTest(subtotal=subtotal):
                with self.assertRaises(ValueError):
                    delivery_fee(subtotal)

    def test_baskets_below_5000_cost_500_to_deliver(self):
        for subtotal in (0, 1200, 4999):
            with self.subTest(subtotal=subtotal):
                self.assertEqual(delivery_fee(subtotal), 500)

    def test_baskets_from_5000_to_9999_cost_250_to_deliver(self):
        for subtotal in (5000, 7500, 9999):
            with self.subTest(subtotal=subtotal):
                self.assertEqual(delivery_fee(subtotal), 250)

    def test_baskets_from_10000_have_free_delivery(self):
        for subtotal in (10000, 12000, 10**30):
            with self.subTest(subtotal=subtotal):
                self.assertEqual(delivery_fee(subtotal), 0)
