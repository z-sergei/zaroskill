import unittest
from discounts import discounted_total


class DiscountTests(unittest.TestCase):
    def test_discount_cannot_exceed_the_cap(self):
        self.assertEqual(
            discounted_total(1000, 30, max_discount_cents=200), 800
        )

    def test_negative_cap_is_invalid_even_when_the_discount_is_zero(self):
        for percent in (0, 30):
            with self.subTest(percent=percent), self.assertRaises(ValueError):
                discounted_total(1000, percent, max_discount_cents=-1)

    def test_none_cap_keeps_the_rounded_percentage_discount(self):
        self.assertEqual(
            discounted_total(999, 15, max_discount_cents=None), 850
        )

    def test_a_larger_cap_does_not_increase_the_percentage_discount(self):
        self.assertEqual(
            discounted_total(999, 15, max_discount_cents=200), 850
        )

    def test_zero_cap_prevents_any_discount(self):
        self.assertEqual(
            discounted_total(1000, 30, max_discount_cents=0), 1000
        )

    def test_cap_must_be_passed_by_keyword(self):
        with self.assertRaises(TypeError):
            discounted_total(1000, 30, 200)

    def test_no_discount(self):
        self.assertEqual(discounted_total(1200, 0), 1200)

    def test_percentage_discount(self):
        self.assertEqual(discounted_total(1000, 15), 850)

    def test_discount_rounds_down_to_whole_cents(self):
        self.assertEqual(discounted_total(999, 15), 850)

    def test_full_discount(self):
        self.assertEqual(discounted_total(1000, 100), 0)

    def test_invalid_subtotal(self):
        for cap in (None, 0):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                discounted_total(-1, 15, max_discount_cents=cap)

    def test_invalid_percent(self):
        for percent in [-1, 101]:
            for cap in (None, 0):
                with self.subTest(percent=percent, cap=cap), self.assertRaises(ValueError):
                    discounted_total(1000, percent, max_discount_cents=cap)
