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

    def test_unicode_edges_are_trimmed_without_changing_inner_characters(self):
        name = "A\tB\nC\u00a0e\u0301!"
        self.assertEqual(clean_display_name("\u2003" + name + "\u00a0"), name)

    def test_combining_codepoints_count_towards_the_length_limit(self):
        name = "e\u0301" * 10
        self.assertEqual(clean_display_name(name), name)
        with self.assertRaises(ValueError):
            clean_display_name(name + "X")
