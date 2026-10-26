import unittest
from discounts import discounted_total


class DiscountTests(unittest.TestCase):
    def test_no_discount(self):
        self.assertEqual(discounted_total(1200, 0), 1200)

    def test_percentage_discount(self):
        self.assertEqual(discounted_total(1000, 15), 850)

    def test_discount_rounds_down_to_whole_cents(self):
        self.assertEqual(discounted_total(999, 15), 850)

    def test_full_discount(self):
        self.assertEqual(discounted_total(1000, 100), 0)

    def test_invalid_subtotal(self):
        with self.assertRaises(ValueError):
            discounted_total(-1, 15)

    def test_invalid_percent(self):
        for percent in [-1, 101]:
            with self.subTest(percent=percent), self.assertRaises(ValueError):
                discounted_total(1000, percent)


class DiscountCapTests(unittest.TestCase):
    def test_cap_relations_to_computed_discount(self):
        for limit, expected in [(None, 850), (200, 850), (150, 850), (100, 900), (0, 1000)]:
            with self.subTest(limit=limit):
                self.assertEqual(
                    discounted_total(1000, 15, max_discount_cents=limit), expected
                )

    def test_negative_cap_is_invalid_even_without_a_discount(self):
        with self.assertRaises(ValueError):
            discounted_total(1000, 0, max_discount_cents=-1)

    def test_cap_is_keyword_only(self):
        with self.assertRaises(TypeError):
            discounted_total(1000, 15, 100)


class DiscountValidationInteractions(unittest.TestCase):
    def test_zero_cap_preserves_subtotal_and_percent_validation(self):
        for subtotal, percent in [(-1, 15), (1000, -1), (1000, 101)]:
            with self.subTest(subtotal=subtotal, percent=percent), self.assertRaises(ValueError):
                discounted_total(subtotal, percent, max_discount_cents=0)

    def test_zero_subtotal_does_not_bypass_negative_cap_validation(self):
        with self.assertRaises(ValueError):
            discounted_total(0, 15, max_discount_cents=-1)
