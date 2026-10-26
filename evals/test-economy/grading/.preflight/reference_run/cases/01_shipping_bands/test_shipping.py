import unittest
from shipping import delivery_fee


class ShippingTests(unittest.TestCase):
    def test_zero_is_a_valid_paid_basket(self):
        self.assertEqual(delivery_fee(0), 500)

    def test_first_discount_boundary(self):
        for subtotal, fee in [(4999, 500), (5000, 250)]:
            with self.subTest(subtotal=subtotal):
                self.assertEqual(delivery_fee(subtotal), fee)

    def test_free_delivery_boundary(self):
        for subtotal, fee in [(9999, 250), (10000, 0)]:
            with self.subTest(subtotal=subtotal):
                self.assertEqual(delivery_fee(subtotal), fee)

    def test_negative_subtotal_is_rejected(self):
        with self.assertRaises(ValueError):
            delivery_fee(-1)
