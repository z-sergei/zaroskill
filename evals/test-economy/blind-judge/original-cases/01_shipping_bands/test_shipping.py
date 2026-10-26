import unittest
from shipping import delivery_fee


class ShippingTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(delivery_fee(0), 500)

    def test_small_basket(self):
        self.assertEqual(delivery_fee(1200), 500)

    def test_medium_basket(self):
        self.assertEqual(delivery_fee(2400), 500)

    def test_below_first_threshold(self):
        self.assertEqual(delivery_fee(4999), 500)

    def test_at_first_threshold(self):
        self.assertEqual(delivery_fee(5000), 250)

    def test_discounted_basket(self):
        self.assertEqual(delivery_fee(5500), 250)

    def test_another_discounted_basket(self):
        self.assertEqual(delivery_fee(7500), 250)

    def test_below_free_threshold(self):
        self.assertEqual(delivery_fee(9999), 250)

    def test_at_free_threshold(self):
        self.assertEqual(delivery_fee(10000), 0)

    def test_large_basket(self):
        self.assertEqual(delivery_fee(12000), 0)

    def test_very_large_basket(self):
        self.assertEqual(delivery_fee(20000), 0)

    def test_negative_cent(self):
        with self.assertRaises(ValueError):
            delivery_fee(-1)

    def test_negative_basket(self):
        with self.assertRaises(ValueError):
            delivery_fee(-200)
