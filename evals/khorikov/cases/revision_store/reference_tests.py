"""Independent public-contract tests; evaluator material, not a candidate deliverable."""

import unittest

from revision_store import (
    DocumentExistsError,
    DocumentNotFoundError,
    RevisionNotFoundError,
    RevisionStore,
    VersionConflictError,
)


class RevisionStoreContractTests(unittest.TestCase):
    def setUp(self):
        self.store = RevisionStore()

    def test_rejected_create_leaves_caller_content_unchanged(self):
        content = {"tags": ["keep", None]}
        with self.assertRaises(TypeError):
            self.store.create("rejected", content)
        self.assertEqual(content, {"tags": ["keep", None]})
        with self.assertRaises(DocumentNotFoundError):
            self.store.read("rejected")

    def test_create_snapshot_and_independent_store(self):
        created = self.store.create("doc", {"title": "Draft", "tags": ["one"]})
        expected = {"document_id": "doc", "version": 1, "content": {"title": "Draft", "tags": ["one"]}}
        self.assertEqual(created, expected)
        self.assertEqual(self.store.read("doc"), expected)
        other = RevisionStore()
        with self.assertRaises(DocumentNotFoundError):
            other.read("doc")
        self.assertEqual(other.create("doc", {})["version"], 1)
        self.assertEqual(self.store.read("doc"), expected)

    def test_empty_content_and_verbatim_case_sensitive_unicode_ids(self):
        for document_id in ["A", "a", " A ", "\u00e9", "e\u0301", " "]:
            with self.subTest(document_id=document_id):
                self.assertEqual(self.store.create(document_id, {}), {"document_id": document_id, "version": 1, "content": {}})
                self.assertEqual(self.store.read(document_id)["content"], {})
        content = {"": "", "list": [], "unicode": ["\u732b", "\u00e9"]}
        self.assertEqual(self.store.create("valid", content)["content"], {"": "", "list": [], "unicode": ["\u732b", "\u00e9"]})

    def test_duplicate_creation_preserves_complete_history(self):
        self.store.create("doc", {"title": "one"})
        self.store.replace("doc", {"title": "two"}, expected_version=1)
        with self.assertRaises(DocumentExistsError):
            self.store.create("doc", {"title": "bad"})
        self.assertEqual(self.store.history("doc"), [
            {"document_id": "doc", "version": 1, "content": {"title": "one"}},
            {"document_id": "doc", "version": 2, "content": {"title": "two"}},
        ])

    def test_create_detaches_caller_content_and_does_not_modify_it(self):
        content = {"title": "draft", "tags": ["original"]}
        self.store.create("doc", content)
        self.assertEqual(content, {"title": "draft", "tags": ["original"]})
        content["tags"].append("changed")
        content["title"] = "changed"
        content["added"] = "changed"
        self.assertEqual(self.store.read("doc"), {
            "document_id": "doc", "version": 1, "content": {"title": "draft", "tags": ["original"]},
        })

    def test_create_return_value_is_detached_and_survives_later_writes(self):
        created = self.store.create("doc", {"tags": ["one"]})
        separately_read = self.store.read("doc")
        created["document_id"] = "elsewhere"
        created["version"] = 900
        created["content"]["tags"].clear()
        created["content"]["new"] = "value"
        expected = {"document_id": "doc", "version": 1, "content": {"tags": ["one"]}}
        self.assertEqual(self.store.read("doc"), expected)
        self.assertEqual(separately_read, expected)
        self.store.replace("doc", {"tags": ["two"]}, expected_version=1)
        self.assertEqual(separately_read, expected)

    def test_latest_read_tracks_replacement_and_explicit_none(self):
        self.store.create("doc", {"old": "gone", "tags": ["one"]})
        replacement = self.store.replace("doc", {"title": "new"}, expected_version=1)
        expected = {"document_id": "doc", "version": 2, "content": {"title": "new"}}
        self.assertEqual(replacement, expected)
        self.assertEqual(self.store.read("doc"), expected)
        self.assertEqual(self.store.read("doc", version=None), expected)

    def test_each_historical_version_retains_its_original_content(self):
        self.store.create("doc", {"title": "first"})
        self.store.replace("doc", {"tags": ["second"]}, expected_version=1)
        self.store.replace("doc", {}, expected_version=2)
        for version, content in [(1, {"title": "first"}), (2, {"tags": ["second"]}), (3, {})]:
            with self.subTest(version=version):
                self.assertEqual(self.store.read("doc", version=version), {
                    "document_id": "doc", "version": version, "content": content,
                })

    def test_current_reads_are_detached_from_store_and_one_another(self):
        self.store.create("doc", {"title": "kept", "tags": ["one"]})
        first = self.store.read("doc")
        second = self.store.read("doc")
        first["content"]["tags"].append("bad")
        first["content"].pop("title")
        first["version"] = 50
        expected = {"document_id": "doc", "version": 1, "content": {"title": "kept", "tags": ["one"]}}
        self.assertEqual(second, expected)
        self.assertEqual(self.store.read("doc"), expected)

    def test_historical_reads_are_detached(self):
        self.store.create("doc", {"tags": ["first"]})
        self.store.replace("doc", {"tags": ["second"]}, expected_version=1)
        historical = self.store.read("doc", version=1)
        historical["content"]["tags"].append("bad")
        historical["content"]["extra"] = "bad"
        self.assertEqual(self.store.read("doc", version=1), {
            "document_id": "doc", "version": 1, "content": {"tags": ["first"]},
        })
        self.assertEqual(self.store.read("doc"), {
            "document_id": "doc", "version": 2, "content": {"tags": ["second"]},
        })

    def test_history_is_complete_ordered_and_detached_at_every_level(self):
        self.store.create("doc", {"tags": ["first"]})
        self.store.replace("doc", {"tags": ["second"]}, expected_version=1)
        expected = [
            {"document_id": "doc", "version": 1, "content": {"tags": ["first"]}},
            {"document_id": "doc", "version": 2, "content": {"tags": ["second"]}},
        ]
        history = self.store.history("doc")
        another_history = self.store.history("doc")
        self.assertEqual(history, expected)
        history[0]["content"]["tags"].clear()
        history[1]["content"]["added"] = "bad"
        history[1]["version"] = 44
        history.reverse()
        history.pop()
        self.assertEqual(another_history, expected)
        self.assertEqual(self.store.history("doc"), expected)
        self.store.replace("doc", {}, expected_version=2)
        self.assertEqual(another_history, expected)

    def test_replacements_use_independent_document_version_sequences(self):
        self.store.create("a", {"title": "A1"})
        self.store.create("b", {"title": "B1"})
        self.store.replace("a", {"title": "A2"}, expected_version=1)
        self.assertEqual(self.store.replace("a", {"title": "A3"}, expected_version=2), {
            "document_id": "a", "version": 3, "content": {"title": "A3"},
        })
        self.assertEqual(self.store.read("b"), {"document_id": "b", "version": 1, "content": {"title": "B1"}})
        self.assertEqual(self.store.replace("b", {}, expected_version=1), {"document_id": "b", "version": 2, "content": {}})

    def test_stale_and_future_preconditions_preserve_history(self):
        for expected_version in [1, 3]:
            with self.subTest(expected_version=expected_version):
                store = RevisionStore()
                store.create("doc", {"title": "one"})
                store.replace("doc", {"title": "two"}, expected_version=1)
                with self.assertRaises(VersionConflictError):
                    store.replace("doc", {"title": "bad"}, expected_version=expected_version)
                self.assertEqual(store.history("doc"), [
                    {"document_id": "doc", "version": 1, "content": {"title": "one"}},
                    {"document_id": "doc", "version": 2, "content": {"title": "two"}},
                ])

    def test_replace_inputs_and_results_are_detached(self):
        self.store.create("doc", {})
        content = {"tags": ["saved"], "title": "saved"}
        result = self.store.replace("doc", content, expected_version=1)
        separately_read = self.store.read("doc")
        self.assertEqual(content, {"tags": ["saved"], "title": "saved"})
        content["tags"].clear()
        content.pop("title")
        result["content"]["tags"].append("bad")
        result["content"]["title"] = "bad"
        result["version"] = 9
        expected = {"document_id": "doc", "version": 2, "content": {"tags": ["saved"], "title": "saved"}}
        self.assertEqual(self.store.read("doc"), expected)
        self.assertEqual(separately_read, expected)
        self.assertEqual(self.store.read("doc", version=1)["content"], {})

    def test_equal_content_still_appends_one_revision_in_single_and_batch_writes(self):
        self.store.create("a", {"tags": ["same"]})
        self.assertEqual(self.store.replace("a", {"tags": ["same"]}, expected_version=1), {
            "document_id": "a", "version": 2, "content": {"tags": ["same"]},
        })
        self.assertEqual(self.store.replace_many([("a", 2, {"tags": ["same"]})]), [
            {"document_id": "a", "version": 3, "content": {"tags": ["same"]}},
        ])
        self.assertEqual(self.store.history("a"), [
            {"document_id": "a", "version": 1, "content": {"tags": ["same"]}},
            {"document_id": "a", "version": 2, "content": {"tags": ["same"]}},
            {"document_id": "a", "version": 3, "content": {"tags": ["same"]}},
        ])

    def test_batch_commit_preserves_input_order_and_full_replacement_semantics(self):
        self.store.create("a", {"old": "A1"})
        self.store.create("b", {"old": "B1"})
        self.store.create("untouched", {"tags": ["keep"]})
        self.store.replace("a", {"old": "A2"}, expected_version=1)
        result = self.store.replace_many([("b", 1, {"new": "B2"}), ("a", 2, {"new": "A3"})])
        self.assertEqual(result, [
            {"document_id": "b", "version": 2, "content": {"new": "B2"}},
            {"document_id": "a", "version": 3, "content": {"new": "A3"}},
        ])
        self.assertEqual(self.store.read("a"), {"document_id": "a", "version": 3, "content": {"new": "A3"}})
        self.assertEqual(self.store.read("b"), {"document_id": "b", "version": 2, "content": {"new": "B2"}})
        self.assertEqual(self.store.read("untouched"), {"document_id": "untouched", "version": 1, "content": {"tags": ["keep"]}})
        self.assertEqual(self.store.read("a", version=2)["content"], {"old": "A2"})
        self.assertEqual(self.store.read("b", version=1)["content"], {"old": "B1"})

    def test_missing_later_batch_document_leaves_everything_unchanged(self):
        self.store.create("a", {"title": "A1"})
        self.store.create("b", {"title": "B1"})
        with self.assertRaises(DocumentNotFoundError):
            self.store.replace_many([("a", 1, {"title": "bad"}), ("missing", 1, {}), ("b", 1, {})])
        self.assertEqual(self.store.history("a"), [{"document_id": "a", "version": 1, "content": {"title": "A1"}}])
        self.assertEqual(self.store.history("b"), [{"document_id": "b", "version": 1, "content": {"title": "B1"}}])
        with self.assertRaises(DocumentNotFoundError):
            self.store.read("missing")
        self.assertEqual(self.store.replace("a", {}, expected_version=1)["version"], 2)

    def test_stale_later_batch_precondition_leaves_all_histories_unchanged(self):
        self.store.create("a", {"title": "A1"})
        self.store.create("b", {"title": "B1"})
        self.store.replace("b", {"title": "B2"}, expected_version=1)
        with self.assertRaises(VersionConflictError):
            self.store.replace_many([("a", 1, {"title": "bad"}), ("b", 1, {"title": "bad"})])
        self.assertEqual(self.store.history("a"), [{"document_id": "a", "version": 1, "content": {"title": "A1"}}])
        self.assertEqual(self.store.history("b"), [
            {"document_id": "b", "version": 1, "content": {"title": "B1"}},
            {"document_id": "b", "version": 2, "content": {"title": "B2"}},
        ])

    def test_batch_inputs_and_result_list_are_detached(self):
        self.store.create("a", {})
        self.store.create("b", {})
        shared_content = {"tags": ["saved"]}
        changes = [("a", 1, shared_content), ("b", 1, shared_content)]
        result = self.store.replace_many(changes)
        self.assertEqual(changes, [("a", 1, {"tags": ["saved"]}), ("b", 1, {"tags": ["saved"]})])
        shared_content["tags"].clear()
        changes.clear()
        result[0]["content"]["tags"].append("bad")
        self.assertEqual(result[1], {"document_id": "b", "version": 2, "content": {"tags": ["saved"]}})
        result[1]["content"]["new"] = "bad"
        result.clear()
        for document_id in ["a", "b"]:
            with self.subTest(document_id=document_id):
                self.assertEqual(self.store.read(document_id), {"document_id": document_id, "version": 2, "content": {"tags": ["saved"]}})
                self.assertEqual(self.store.read(document_id, version=1)["content"], {})

    def test_empty_batch_is_a_no_op_on_empty_and_populated_stores(self):
        self.assertEqual(self.store.replace_many([]), [])
        self.store.create("doc", {"title": "saved"})
        result = self.store.replace_many([])
        self.assertEqual(result, [])
        result.append({"irrelevant": "value"})
        self.assertEqual(self.store.history("doc"), [{"document_id": "doc", "version": 1, "content": {"title": "saved"}}])

    def test_invalid_ids_are_rejected_by_every_operation_without_state_changes(self):
        class StringSubclass(str):
            pass

        self.store.create("safe", {"title": "saved"})
        for invalid, error in [(None, TypeError), (1, TypeError), (True, TypeError), ([], TypeError), (StringSubclass("safe"), TypeError), ("", ValueError)]:
            operations = [
                lambda: self.store.create(invalid, {}),
                lambda: self.store.read(invalid),
                lambda: self.store.history(invalid),
                lambda: self.store.replace(invalid, {}, expected_version=1),
                lambda: self.store.replace_many([("safe", 1, {}), (invalid, 1, {})]),
            ]
            for number, operation in enumerate(operations):
                with self.subTest(invalid=repr(invalid), operation=number):
                    with self.assertRaises(error):
                        operation()
                    self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {"title": "saved"}}])

    def test_unsupported_content_is_rejected_before_lookup_or_mutation(self):
        class DictSubclass(dict):
            pass

        class StringSubclass(str):
            pass

        class ListSubclass(list):
            pass

        self.store.create("safe", {"title": "saved"})
        invalid_contents = [None, [], DictSubclass(), {1: "value"}, {StringSubclass("key"): "value"},
                            {"key": None}, {"key": 1}, {"key": True}, {"key": {}}, {"key": ("x",)},
                            {"key": ["x", 1]}, {"key": [["x"]]}, {"key": StringSubclass("x")},
                            {"key": ListSubclass(["x"])}, {"key": [StringSubclass("x")]}]
        for content in invalid_contents:
            for number, operation in enumerate([
                lambda: self.store.create("safe", content),
                lambda: self.store.replace("absent", content, expected_version=1),
                lambda: self.store.replace_many([("safe", 1, {}), ("absent", 1, content)]),
            ]):
                with self.subTest(content=repr(content), operation=number):
                    with self.assertRaises(TypeError):
                        operation()
                    self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {"title": "saved"}}])
                    with self.assertRaises(DocumentNotFoundError):
                        self.store.read("absent")

    def test_versions_require_exact_positive_integers_and_explicit_preconditions(self):
        class IntSubclass(int):
            pass

        self.store.create("safe", {})
        for version, error in [(True, TypeError), (False, TypeError), (1.0, TypeError), ("1", TypeError), (IntSubclass(1), TypeError), (0, ValueError), (-1, ValueError)]:
            for number, operation in enumerate([
                lambda: self.store.read("absent", version=version),
                lambda: self.store.replace("absent", {}, expected_version=version),
                lambda: self.store.replace_many([("safe", 1, {}), ("absent", version, {})]),
            ]):
                with self.subTest(version=repr(version), operation=number):
                    with self.assertRaises(error):
                        operation()
                    self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {}}])
        with self.assertRaises(TypeError):
            self.store.replace("safe", {}, expected_version=None)
        with self.assertRaises(TypeError):
            self.store.replace_many([("safe", None, {})])
        with self.assertRaises(TypeError):
            self.store.replace("safe", {})
        with self.assertRaises(TypeError):
            self.store.replace("safe", {}, 1)
        with self.assertRaises(TypeError):
            self.store.read("safe", 1)
        self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {}}])

    def test_batch_shape_duplicates_and_validation_precedence(self):
        class ListSubclass(list):
            pass

        class TupleSubclass(tuple):
            pass

        self.store.create("safe", {"title": "saved"})
        invalid_batches = [None, (), {}, ListSubclass(), [None], [["safe", 1, {}]],
                           [("safe", 1)], [("safe", 1, {}, "extra")], [TupleSubclass(("safe", 1, {}))],
                           [("safe", 1, {}), ("absent", 1, {"wrong": 2})]]
        for changes in invalid_batches:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(TypeError):
                    self.store.replace_many(changes)
                self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {"title": "saved"}}])
        for changes in [[("safe", 1, {}), ("safe", 1, {})], [("absent", 1, {}), ("absent", 1, {})]]:
            with self.subTest(duplicates=changes):
                with self.assertRaises(ValueError):
                    self.store.replace_many(changes)
        with self.assertRaises(TypeError):
            self.store.replace_many([("absent", 1, {}), ("safe", 1, {"wrong": 2})])
        with self.assertRaises(TypeError):
            self.store.replace_many([("safe", 1, {}), ("safe", 1, {"wrong": 2})])
        with self.assertRaises(ValueError):
            self.store.replace("", {"wrong": 2}, expected_version=True)
        with self.assertRaises(ValueError):
            self.store.replace("absent", {"wrong": 2}, expected_version=0)
        with self.assertRaises(ValueError):
            self.store.create("", None)
        self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {"title": "saved"}}])

    def test_missing_documents_unknown_revisions_and_batch_lookup_order(self):
        for operation in [lambda: self.store.read("missing"), lambda: self.store.read("missing", version=99),
                          lambda: self.store.history("missing"), lambda: self.store.replace("missing", {}, expected_version=1)]:
            with self.assertRaises(DocumentNotFoundError):
                operation()
        self.store.create("safe", {"title": "saved"})
        with self.assertRaises(RevisionNotFoundError):
            self.store.read("safe", version=2)
        with self.assertRaises(VersionConflictError):
            self.store.replace_many([("safe", 2, {}), ("missing", 1, {})])
        with self.assertRaises(DocumentNotFoundError):
            self.store.replace_many([("missing", 1, {}), ("safe", 2, {})])
        self.assertEqual(self.store.history("safe"), [{"document_id": "safe", "version": 1, "content": {"title": "saved"}}])


if __name__ == "__main__":
    unittest.main()
