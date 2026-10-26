import unittest
from names import clean_display_name


class Contract(unittest.TestCase):
    def test_valid_strings_preserve_interior(self):
        for value in ["Z", "x" * 20, "Zoë  X", "á" * 20, "a\tb"]:
            for padding in ["", " \n\t", "\u2003"]:
                with self.subTest(value=value, padding=padding):
                    self.assertEqual(clean_display_name(padding + value + padding), value)

    def test_invalid_cleaned_lengths(self):
        for value in ["", " \t\n", "y" * 21, " " + "é" * 21 + " "]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                clean_display_name(value)
