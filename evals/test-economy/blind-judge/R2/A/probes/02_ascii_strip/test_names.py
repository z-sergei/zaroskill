import unittest
from names import clean_display_name


class DisplayNameTests(unittest.TestCase):
    def test_shortest_name_preserves_case(self):
        self.assertEqual(clean_display_name("A"), "A")

    def test_longest_name_is_valid_after_trimming(self):
        name = "Ab" * 10
        self.assertEqual(clean_display_name(" \t" + name + "\n "), name)

    def test_empty_name_is_invalid(self):
        with self.assertRaises(ValueError):
            clean_display_name("")

    def test_whitespace_only_is_invalid(self):
        with self.assertRaises(ValueError):
            clean_display_name(" \t\n ")

    def test_one_character_too_long(self):
        with self.assertRaises(ValueError):
            clean_display_name("x" * 21)

    def test_inner_spacing_and_mixed_case_are_preserved(self):
        self.assertEqual(clean_display_name("  Ada  LoVELace  "), "Ada  LoVELace")

    def test_length_counts_characters(self):
        self.assertEqual(clean_display_name("é" * 20), "é" * 20)

    def test_unicode_whitespace_is_trimmed_from_edges(self):
        self.assertEqual(clean_display_name("\u00a0\u2003Ada\u2003\u00a0"), "Ada")

    def test_combining_characters_are_preserved_and_count_towards_length(self):
        name = "e\u0301" * 10  # Twenty Python characters, ten visible graphemes.
        self.assertEqual(clean_display_name(name), name)
        with self.assertRaises(ValueError):
            clean_display_name(name + "e")
