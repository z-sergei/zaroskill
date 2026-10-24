import unittest
from shipping import fee

class ShippingTests(unittest.TestCase):
    def test_small_parcels_cost_four(self):
        for weight in range(1, 6):
            with self.subTest(weight=weight):
                self.assertEqual(4, fee(weight))

    def test_larger_supported_parcels_cost_seven(self):
        for weight in range(6, 21):
            with self.subTest(weight=weight):
                self.assertEqual(7, fee(weight))

    def test_unsupported_weights_are_refused(self):
        for weight in (-2, 0, 21, 99):
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    fee(weight)
