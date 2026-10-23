import unittest

from app import TTLCache


class ManualClock:
    def __init__(self, now=0):
        self.now = now
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.now


class RefusesCopy:
    def __deepcopy__(self, memo):
        raise RuntimeError("copy refused")


class CacheContractTests(unittest.TestCase):
    def setUp(self):
        self.clock = ManualClock()
        self.cache = TTLCache(2, self.clock)

    def seed_pair(self):
        self.cache.put("a", {"value": 1}, 10)
        self.cache.put("b", {"value": 2}, 20)

    def test_constructor_rejects_invalid_capacity_and_clock_without_sampling(self):
        for capacity in (0, -1, True, False, 1.5, "2", None):
            with self.subTest(capacity=capacity):
                with self.assertRaises(ValueError):
                    TTLCache(capacity, self.clock)
        with self.assertRaises(TypeError):
            TTLCache(2, 123)
        self.assertEqual(self.clock.calls, 0)
        self.assertEqual(TTLCache(1, self.clock).snapshot(), {})

    def test_deadline_is_live_before_and_expired_at_exact_boundary(self):
        self.clock.now = 5
        self.cache.put("memo", "saved", 10)
        self.clock.now = 14.999
        self.assertEqual(self.cache.get("memo"), "saved")
        self.clock.now = 15
        absent = object()
        self.assertIs(self.cache.get("memo", absent), absent)
        self.assertEqual(self.cache.snapshot(), {})

    def test_successful_read_does_not_extend_deadline(self):
        self.cache.put("memo", 7, 4)
        self.clock.now = 3
        self.assertEqual(self.cache.get("memo"), 7)
        self.clock.now = 4.5
        self.assertIsNone(self.cache.get("memo"))

    def test_live_hit_protects_entry_from_lru_eviction(self):
        self.seed_pair()
        self.assertEqual(self.cache.get("a"), {"value": 1})
        self.cache.put("c", 3, 30)
        self.assertEqual(self.cache.snapshot(), {"a": {"value": 1}, "c": 3})
        self.assertEqual(list(self.cache.snapshot()), ["a", "c"])

    def test_miss_returns_original_default_without_changing_lru_order(self):
        self.seed_pair()
        sentinel = {"missing": []}
        self.assertIs(self.cache.get("missing", sentinel), sentinel)
        self.assertEqual(list(self.cache.snapshot()), ["a", "b"])
        self.cache.put("c", 3, 30)
        self.assertEqual(self.cache.snapshot(), {"b": {"value": 2}, "c": 3})

    def test_overwrite_replaces_value_and_resets_deadline(self):
        self.cache.put("a", "old", 5)
        self.clock.now = 4
        self.assertIsNone(self.cache.put("a", "new", 10))
        self.clock.now = 6
        self.assertEqual(self.cache.get("a"), "new")
        self.clock.now = 14
        self.assertIsNone(self.cache.get("a"))

    def test_overwrite_marks_existing_key_most_recently_used(self):
        self.seed_pair()
        self.cache.put("a", {"value": 11}, 30)
        self.assertEqual(list(self.cache.snapshot()), ["b", "a"])
        self.cache.put("c", 3, 30)
        self.assertEqual(self.cache.snapshot(), {"a": {"value": 11}, "c": 3})

    def test_expired_recent_entry_is_removed_before_capacity_eviction(self):
        self.cache.put("long", 1, 20)
        self.cache.put("short", 2, 2)
        self.clock.now = 3
        self.cache.put("new", 3, 20)
        self.assertEqual(self.cache.snapshot(), {"long": 1, "new": 3})
        self.assertEqual(list(self.cache.snapshot()), ["long", "new"])

    def test_rounded_expired_writes_never_displace_live_entries(self):
        clock = ManualClock(1.0)
        tiny = 2 ** -54
        self.assertEqual(1.0 + tiny, 1.0)
        with self.subTest(operation="single insertion"):
            cache = TTLCache(1, clock)
            cache.put("long", "keep", 10)
            cache.put("instant", "discard", tiny)
            self.assertEqual(cache.snapshot(), {"long": "keep"})
        with self.subTest(operation="batch insertion"):
            cache = TTLCache(2, clock)
            cache.put("long", "keep", 10)
            cache.put_many([("instant", "discard", tiny), ("later", "new", 10)])
            self.assertEqual(list(cache.snapshot().items()), [("long", "keep"), ("later", "new")])
        with self.subTest(operation="replacement"):
            cache = TTLCache(2, clock)
            cache.put_many([("keep", 1, 10), ("replace", 2, 10)])
            cache.put("replace", 3, tiny)
            self.assertEqual(cache.snapshot(), {"keep": 1})

    def test_expired_get_is_a_miss_and_does_not_displace_live_entry(self):
        self.cache.put("short", 1, 2)
        self.cache.put("long", 2, 20)
        self.clock.now = 3
        sentinel = []
        self.assertIs(self.cache.get("short", sentinel), sentinel)
        self.cache.put("new", 3, 20)
        self.assertEqual(self.cache.snapshot(), {"long": 2, "new": 3})

    def test_snapshot_reports_recency_without_changing_it(self):
        self.seed_pair()
        self.cache.get("a")
        first = self.cache.snapshot()
        second = self.cache.snapshot()
        self.assertIs(type(first), dict)
        self.assertEqual(list(first), ["b", "a"])
        self.assertEqual(list(second), ["b", "a"])
        self.cache.put("c", 3, 20)
        self.assertEqual(list(self.cache.snapshot()), ["a", "c"])

    def test_stored_value_is_detached_from_nested_input_mutations(self):
        original = {"rows": [{"tags": ["first"]}]}
        self.cache.put("memo", original, 20)
        original["rows"][0]["tags"].append("external")
        original["rows"].append({"tags": []})
        self.assertEqual(self.cache.get("memo"), {"rows": [{"tags": ["first"]}]})

    def test_get_result_is_detached_from_nested_stored_value(self):
        self.cache.put("memo", {"rows": [[1, 2]]}, 20)
        result = self.cache.get("memo")
        result["rows"][0].append(3)
        result["extra"] = True
        self.assertEqual(self.cache.get("memo"), {"rows": [[1, 2]]})

    def test_snapshot_and_its_nested_values_are_detached(self):
        self.cache.put("memo", {"rows": [[1, 2]]}, 20)
        snapshot = self.cache.snapshot()
        snapshot["memo"]["rows"][0].append(3)
        snapshot["new"] = 4
        self.assertEqual(self.cache.snapshot(), {"memo": {"rows": [[1, 2]]}})

    def test_nonempty_batch_samples_time_once_for_all_deadlines(self):
        self.clock.now = 10
        records = iter([("a", 1, 2), ("b", 2, 4)])
        self.assertIsNone(self.cache.put_many(records))
        self.assertEqual(self.clock.calls, 1)
        self.clock.now = 12
        self.assertEqual(self.cache.snapshot(), {"b": 2})
        self.clock.now = 14
        self.assertEqual(self.cache.snapshot(), {})

    def test_duplicate_batch_keys_use_last_value_ttl_and_recency(self):
        self.cache.put_many([("a", 1, 20), ("b", 2, 20), ("a", 3, 2)])
        self.assertEqual(self.cache.snapshot(), {"b": 2, "a": 3})
        self.assertEqual(list(self.cache.snapshot()), ["b", "a"])
        self.clock.now = 2
        self.assertEqual(self.cache.snapshot(), {"b": 2})

    def test_batch_enforces_capacity_after_each_entry_in_order(self):
        self.cache.put_many([("a", 1, 20), ("b", 2, 20), ("c", 3, 20), ("a", 4, 20)])
        self.assertEqual(self.cache.snapshot(), {"c": 3, "a": 4})
        self.assertEqual(list(self.cache.snapshot()), ["c", "a"])
        single = TTLCache(1, self.clock)
        single.put_many([("x", 1, 20), ("y", 2, 20), ("x", 3, 20)])
        self.assertEqual(single.snapshot(), {"x": 3})

    def test_invalid_batch_key_preserves_values_deadlines_and_recency(self):
        self.seed_pair()
        self.clock.now = 5
        calls_before = self.clock.calls
        with self.assertRaises(ValueError):
            self.cache.put_many([("a", {"value": 99}, 100), ("", 3, 5)])
        self.assertEqual(self.clock.calls, calls_before)
        self.assertEqual(self.cache.snapshot(), {"a": {"value": 1}, "b": {"value": 2}})
        self.assertEqual(list(self.cache.snapshot()), ["a", "b"])
        self.clock.now = 11
        self.assertEqual(self.cache.snapshot(), {"b": {"value": 2}})

    def test_invalid_batch_ttl_does_not_commit_earlier_insertion_or_eviction(self):
        self.seed_pair()
        calls_before = self.clock.calls
        with self.assertRaises(ValueError):
            self.cache.put_many([("c", 3, 20), ("d", 4, 0)])
        self.assertEqual(self.clock.calls, calls_before)
        self.assertEqual(self.cache.snapshot(), {"a": {"value": 1}, "b": {"value": 2}})
        self.cache.put("e", 5, 20)
        self.assertEqual(list(self.cache.snapshot()), ["b", "e"])

    def test_malformed_batch_entry_does_not_commit_earlier_write(self):
        self.seed_pair()
        for malformed in (None, ("x",), ("x", 1, 2, 3)):
            with self.subTest(malformed=malformed):
                calls_before = self.clock.calls
                with self.assertRaises(ValueError):
                    self.cache.put_many([("c", 3, 20), malformed])
                self.assertEqual(self.clock.calls, calls_before)
                self.assertEqual(list(self.cache.snapshot()), ["a", "b"])

    def test_iterator_failure_leaves_existing_state_and_clock_untouched(self):
        self.seed_pair()

        def failing_records():
            yield ("c", 3, 20)
            raise RuntimeError("iteration interrupted")

        calls_before = self.clock.calls
        with self.assertRaises(RuntimeError):
            self.cache.put_many(failing_records())
        self.assertEqual(self.clock.calls, calls_before)
        self.assertEqual(list(self.cache.snapshot()), ["a", "b"])

    def test_value_copy_failure_rolls_back_whole_batch_before_clock_read(self):
        self.seed_pair()
        calls_before = self.clock.calls
        with self.assertRaises(RuntimeError):
            self.cache.put_many([("c", 3, 20), ("d", RefusesCopy(), 20)])
        self.assertEqual(self.clock.calls, calls_before)
        self.assertEqual(self.cache.snapshot(), {"a": {"value": 1}, "b": {"value": 2}})

    def test_invalid_single_writes_preserve_old_value_and_deadline(self):
        invalid_ttls = (0, -1, True, False, None, "3", float("inf"), float("-inf"), float("nan"), 10 ** 400)
        for ttl in invalid_ttls:
            with self.subTest(ttl=ttl):
                clock = ManualClock()
                cache = TTLCache(1, clock)
                cache.put("a", "old", 2)
                clock.now = 1
                calls_before = clock.calls
                with self.assertRaises(ValueError):
                    cache.put("a", "changed", ttl)
                self.assertEqual(clock.calls, calls_before)
                self.assertEqual(cache.get("a"), "old")
                clock.now = 2
                self.assertIsNone(cache.get("a"))
        for key in ("", None, 1, True):
            with self.subTest(key=key):
                calls_before = self.clock.calls
                with self.assertRaises(ValueError):
                    self.cache.put(key, 1, 2)
                self.assertEqual(self.clock.calls, calls_before)

    def test_empty_batch_returns_none_without_reading_clock_or_affecting_lru(self):
        self.seed_pair()
        calls_before = self.clock.calls
        self.assertIsNone(self.cache.put_many(iter(())))
        self.assertEqual(self.clock.calls, calls_before)
        self.cache.put("c", 3, 20)
        self.assertEqual(list(self.cache.snapshot()), ["b", "c"])

    def test_reads_sample_once_and_invalid_get_does_not_sample_or_change_lru(self):
        self.seed_pair()
        for read in (lambda: self.cache.get("a"), lambda: self.cache.get("absent"), self.cache.snapshot):
            calls_before = self.clock.calls
            read()
            self.assertEqual(self.clock.calls, calls_before + 1)
        for key in ("", None, 1, True):
            with self.subTest(key=key):
                calls_before = self.clock.calls
                with self.assertRaises(ValueError):
                    self.cache.get(key)
                self.assertEqual(self.clock.calls, calls_before)
        self.assertEqual(list(self.cache.snapshot()), ["b", "a"])


if __name__ == "__main__":
    unittest.main()
