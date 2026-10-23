import copy
import unittest

from app import apply_edits


class ApplyEditsTests(unittest.TestCase):
    def test_empty_collection_and_empty_text(self):
        self.assertEqual(apply_edits("plain", []), "plain")
        self.assertEqual(apply_edits("", iter(())), "")
        self.assertEqual(apply_edits("", [(0, 0, "first"), (0, 0, "last")]), "firstlast")

    def test_replacement_keeps_surrounding_text(self):
        self.assertEqual(apply_edits("abcdef", [(2, 4, "X")]), "abXef")
        self.assertEqual(apply_edits("abc", [(0, 3, "whole")]), "whole")

    def test_deletion_and_empty_insertion(self):
        self.assertEqual(apply_edits("abcdef", [(1, 3, ""), (5, 5, "")]), "adef")
        self.assertEqual(apply_edits("abc", [(0, 3, "")]), "")

    def test_unsorted_offsets_always_refer_to_original(self):
        edits = [(6, 8, "Q"), (1, 3, "LONG"), (4, 4, "++")]
        self.assertEqual(apply_edits("abcdefgh", edits), "aLONGd++efQ")

    def test_coincident_insertions_keep_encounter_order(self):
        self.assertEqual(apply_edits("ab", [(1, 1, "z"), (1, 1, "a"), (1, 1, "m")]), "azamb")

    def test_insertion_at_each_text_endpoint(self):
        self.assertEqual(apply_edits("abc", [(3, 3, ">"), (0, 0, "<")]), "<abc>")

    def test_insertions_at_both_replacement_endpoints(self):
        edits = [(1, 3, "R"), (3, 3, "after"), (1, 1, "z"), (1, 1, "a")]
        self.assertEqual(apply_edits("abcd", edits), "azaRafterd")

    def test_adjacent_replacements_with_shared_boundary_insertions(self):
        edits = [(2, 4, "R"), (2, 2, "z"), (0, 2, "L"), (2, 2, "a")]
        self.assertEqual(apply_edits("abcde", edits), "LzaRe")

    def test_unicode_offsets_are_python_character_offsets(self):
        original = "A😀e\u0301中Z"
        self.assertEqual(len(original), 6)
        edits = [(4, 5, "界"), (1, 2, "🚀"), (3, 4, "!")]
        self.assertEqual(apply_edits(original, edits), "A🚀e!界Z")

    def test_collection_and_mutable_records_are_preserved(self):
        edits = [[3, 4, "D"], [0, 1, "A"], [2, 2, "X"]]
        before = copy.deepcopy(edits)
        record_ids = [id(edit) for edit in edits]
        self.assertEqual(apply_edits("abcd", edits), "AbXcD")
        self.assertEqual(edits, before)
        self.assertEqual([id(edit) for edit in edits], record_ids)

    def test_generator_is_consumed_once_and_all_edits_are_applied(self):
        seen = []
        def edits():
            for edit in [(3, 4, "D"), (0, 1, "A"), (2, 2, "X")]:
                seen.append(edit)
                yield edit
        self.assertEqual(apply_edits("abcd", edits()), "AbXcD")
        self.assertEqual(seen, [(3, 4, "D"), (0, 1, "A"), (2, 2, "X")])

    def test_each_record_is_snapshotted_before_generator_resumes(self):
        record = [0, 1, "A"]
        def edits():
            yield record
            record[:] = [2, 3, "C"]
            yield record
        self.assertEqual(apply_edits("abcd", edits()), "AbCd")
        self.assertEqual(record, [2, 3, "C"])

    def test_delayed_iterator_exception_is_propagated_unchanged(self):
        failure = RuntimeError("upstream edit source failed")
        def edits():
            yield (0, 1, "A")
            raise failure
        with self.assertRaises(RuntimeError) as raised:
            apply_edits("abc", edits())
        self.assertIs(raised.exception, failure)

    def test_record_validation_happens_before_iterator_resumes(self):
        resumed = []
        def edits():
            yield (0, 1, object())
            resumed.append(True)
            yield (1, 2, "B")
        with self.assertRaises(TypeError):
            apply_edits("abc", edits())
        self.assertEqual(resumed, [])

    def test_non_string_text_and_non_iterable_edits_are_rejected(self):
        for text in (None, 12, b"abc", ["a", "b"]):
            with self.subTest(text=text), self.assertRaises(TypeError):
                apply_edits(text, [])
        for edits in (None, 42):
            with self.subTest(edits=edits), self.assertRaises(TypeError):
                apply_edits("abc", edits)

    def test_malformed_record_shapes_are_rejected(self):
        for edit in (None, "abc", {0: 0, 1: 1, 2: "x"}, (), (0, 1), (0, 1, "x", "extra")):
            with self.subTest(edit=edit), self.assertRaises(TypeError):
                apply_edits("abc", [edit])

    def test_bad_offset_types_and_booleans_are_rejected(self):
        for edit in ((0.0, 1, "x"), (0, "1", "x"), (False, 1, "x"), (0, True, "x"), (None, 1, "x")):
            with self.subTest(edit=edit), self.assertRaises(TypeError):
                apply_edits("abc", [edit])

    def test_non_string_replacements_are_rejected(self):
        for replacement in (None, 42, b"x", ["x"]):
            with self.subTest(replacement=replacement), self.assertRaises(TypeError):
                apply_edits("abc", [(0, 1, replacement)])

    def test_invalid_bounds_are_rejected_including_one_past_end(self):
        for start, stop in ((-1, 0), (1, 0), (0, 4), (4, 4), (0, -1)):
            with self.subTest(start=start, stop=stop), self.assertRaises(ValueError):
                apply_edits("abc", [(start, stop, "x")])

    def test_partially_overlapping_nonempty_ranges_are_rejected(self):
        with self.assertRaises(ValueError):
            apply_edits("abcdef", [(3, 5, "Y"), (1, 4, "X")])

    def test_identical_and_nested_nonempty_ranges_are_rejected(self):
        for edits in ([(1, 4, "X"), (1, 4, "Y")], [(1, 5, "X"), (2, 3, "Y")]):
            with self.subTest(edits=edits), self.assertRaises(ValueError):
                apply_edits("abcdef", edits)

    def test_insertions_strictly_inside_ranges_are_rejected_even_if_empty(self):
        for replacement in ("I", ""):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                apply_edits("abcdef", [(2, 2, replacement), (1, 4, "R")])

    def test_all_records_are_validated_before_overlap_check(self):
        with self.assertRaises(TypeError):
            apply_edits("abcdef", [(1, 4, "X"), (2, 5, "Y"), (0, 0, None)])

    def test_repeated_calls_have_no_shared_state(self):
        self.assertEqual(apply_edits("abc", [(0, 1, "X")]), "Xbc")
        self.assertEqual(apply_edits("123", [(2, 3, "Y")]), "12Y")
        self.assertEqual(apply_edits("abc", []), "abc")


if __name__ == "__main__":
    unittest.main()
