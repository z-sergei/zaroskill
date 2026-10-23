import io
import unittest

from manifest import DeliveryLine, ImportSummary, InvalidManifest, Inventory, import_manifest


class ShortReader:
    """A nonseekable binary source with an independently observable lifetime."""

    def __init__(self, payload, max_fragment=2):
        self._data = io.BytesIO(payload)
        self.max_fragment = max_fragment
        self.closed = False
        self.reads = 0

    def read(self, size=-1):
        if self.closed:
            raise ValueError("closed")
        self.reads += 1
        if size is None or size < 0:
            return self._data.read()
        return self._data.read(min(size, self.max_fragment))

    def close(self):
        self.closed = True


class BrokenReader:
    def __init__(self, error):
        self.error = error
        self._data = io.BytesIO(b"sku,quantity,note\nA,8,arrived\n")
        self.closed = False

    def read(self, size=-1):
        if self.closed:
            raise ValueError("closed")
        if size == 0:
            return b""
        if size is None or size < 0:
            raise self.error
        data = self._data.read(size)
        if data:
            return data
        raise self.error

    def close(self):
        self.closed = True


class ManifestTests(unittest.TestCase):
    def test_record_fields_remain_unchanged_after_assignment_and_deletion(self):
        cases = (
            (DeliveryLine, ("A", 2, "kept"),
             (("sku", "B"), ("quantity", 9), ("note", "changed"))),
            (ImportSummary, (1, 2, ("A",)),
             (("line_count", 9), ("total_units", 8), ("skus", ("B",)))),
        )
        for record_type, original_values, changes in cases:
            for field, replacement in changes:
                for operation in ("assignment", "deletion"):
                    # Stable labels do not render a record after a faulty deletion.
                    with self.subTest(record_type=record_type.__name__,
                                      field=field, operation=operation):
                        record = record_type(*original_values)
                        # Only this deliberate attempt permits unspecified rejection.
                        try:
                            if operation == "assignment":
                                setattr(record, field, replacement)
                            else:
                                delattr(record, field)
                        except Exception:
                            pass
                        # The oracle is the promised state, even after no rejection.
                        for (original_field, _), expected in zip(changes, original_values):
                            self.assertTrue(hasattr(record, original_field),
                                            f"Field {original_field} was removed")
                            self.assertEqual(getattr(record, original_field), expected)

    def seeded_inventory(self):
        inventory = Inventory({"A": 10, "OLD": 4})
        import_manifest(io.BytesIO(b"sku,quantity,note\nOLD,2,previous\n"), inventory)
        return inventory

    def assert_seed_unchanged(self, inventory):
        self.assertEqual(inventory.quantities, {"A": 10, "OLD": 6})
        self.assertEqual(inventory.received_lines, (DeliveryLine("OLD", 2, "previous"),))

    def test_records_accumulate_and_summary_is_per_import_in_first_seen_order(self):
        inventory = self.seeded_inventory()
        result = import_manifest(
            io.BytesIO(b"sku,quantity,note\nB,3,first\n A ,2,second\nB,5,third\n"),
            inventory,
        )
        self.assertEqual(result, ImportSummary(3, 10, ("B", "A")))
        self.assertEqual(inventory.quantities, {"A": 12, "OLD": 6, "B": 8})
        self.assertEqual(inventory.received_lines, (
            DeliveryLine("OLD", 2, "previous"),
            DeliveryLine("B", 3, "first"),
            DeliveryLine("A", 2, "second"),
            DeliveryLine("B", 5, "third"),
        ))

    def test_bom_and_unicode_split_into_single_bytes(self):
        stream = ShortReader("\ufeffsku,quantity,note\n茶,2,café 🧰\n".encode("utf-8"), 1)
        inventory = Inventory()
        try:
            result = import_manifest(stream, inventory, chunk_size=1)
        except InvalidManifest as exc:
            self.fail(f"A valid UTF-8 manifest must survive byte boundaries: {exc}")
        self.assertEqual(result, ImportSummary(1, 2, ("茶",)))
        self.assertEqual(inventory.quantities, {"茶": 2})
        self.assertEqual(inventory.received_lines, (DeliveryLine("茶", 2, "café 🧰"),))
        self.assertEqual(stream.read(10), b"")

    def test_quoted_fields_preserve_commas_quotes_whitespace_and_line_endings(self):
        payload = b'sku,quantity,note\r\n A ,2,"  crate, \"\"blue\"\"\r\nsecond line  "\r\nB,1,"x\ny"'
        inventory = Inventory()
        result = import_manifest(ShortReader(payload, 3), inventory, chunk_size=7)
        self.assertEqual(result, ImportSummary(2, 3, ("A", "B")))
        self.assertEqual(inventory.received_lines, (
            DeliveryLine("A", 2, '  crate, "blue"\r\nsecond line  '),
            DeliveryLine("B", 1, "x\ny"),
        ))

    def test_quantity_boundaries_leading_zeroes_and_case_sensitive_skus(self):
        inventory = Inventory()
        result = import_manifest(io.BytesIO(
            b"sku,quantity,note\n A , 0001 ,\na,1000000,max\n"
        ), inventory)
        self.assertEqual(result, ImportSummary(2, 1_000_001, ("A", "a")))
        self.assertEqual(inventory.quantities, {"A": 1, "a": 1_000_000})
        self.assertEqual(inventory.received_lines, (
            DeliveryLine("A", 1, ""), DeliveryLine("a", 1_000_000, "max"),
        ))

    def test_invalid_quantities_roll_back_earlier_valid_records(self):
        for quantity in ("0", "-1", "+1", "1.0", "", "1000001", "٣"):
            with self.subTest(quantity=quantity):
                inventory = self.seeded_inventory()
                payload = f"sku,quantity,note\nA,8,valid\nB,{quantity},invalid\n".encode()
                with self.assertRaises(InvalidManifest):
                    import_manifest(io.BytesIO(payload), inventory, chunk_size=4)
                self.assert_seed_unchanged(inventory)

    def test_long_leading_zero_quantities_follow_numeric_bounds(self):
        for label, digits, expected in (("one", "1", 1),
                                        ("upper_bound", "1000000", 1_000_000)):
            with self.subTest(label=label):
                inventory = Inventory({"A": 7})
                quantity = "0" * 5000 + digits
                payload = f"sku,quantity,note\nA,{quantity},padded\n".encode()
                result = import_manifest(io.BytesIO(payload), inventory)
                self.assertEqual(result, ImportSummary(1, expected, ("A",)))
                self.assertEqual(inventory.quantities, {"A": 7 + expected})
                self.assertEqual(inventory.received_lines,
                                 (DeliveryLine("A", expected, "padded"),))

        for label, digits in (("zero", "0"), ("above_upper_bound", "1000001")):
            with self.subTest(label=label):
                inventory = self.seeded_inventory()
                quantity = "0" * 5000 + digits
                payload = f"sku,quantity,note\nA,8,valid\nB,{quantity},invalid\n".encode()
                with self.assertRaises(InvalidManifest):
                    import_manifest(io.BytesIO(payload), inventory)
                self.assert_seed_unchanged(inventory)

    def test_bad_record_width_and_blank_sku_are_atomic(self):
        for row in (b"B,2\n", b"B,2,x,extra\n", b"  ,2,x\n"):
            with self.subTest(row=row):
                inventory = self.seeded_inventory()
                with self.assertRaises(InvalidManifest):
                    import_manifest(io.BytesIO(b"sku,quantity,note\nA,8,valid\n" + row), inventory)
                self.assert_seed_unchanged(inventory)

    def test_missing_and_inexact_headers_are_invalid(self):
        for payload in (b"", b"sku,note,quantity\n", b"sku,quantity,note,extra\n", b"SKU,quantity,note\n"):
            with self.subTest(payload=payload):
                inventory = self.seeded_inventory()
                with self.assertRaises(InvalidManifest):
                    import_manifest(io.BytesIO(payload), inventory)
                self.assert_seed_unchanged(inventory)

    def test_empty_import_and_ignored_empty_physical_lines(self):
        inventory = self.seeded_inventory()
        self.assertEqual(import_manifest(io.BytesIO(b"\r\nsku,quantity,note\r\n\r\n"), inventory),
                         ImportSummary(0, 0, ()))
        self.assert_seed_unchanged(inventory)
        self.assertEqual(import_manifest(io.BytesIO(b"sku,quantity,note"), inventory),
                         ImportSummary(0, 0, ()))
        self.assert_seed_unchanged(inventory)

    def test_invalid_utf8_after_valid_record_is_atomic(self):
        for tail in (b"B,2,\xff\n", b"B,2,\xe2\x82"):
            with self.subTest(tail=tail):
                inventory = self.seeded_inventory()
                with self.assertRaises(InvalidManifest):
                    import_manifest(io.BytesIO(b"sku,quantity,note\nA,8,valid\n" + tail), inventory, chunk_size=1)
                self.assert_seed_unchanged(inventory)

    def test_unfinished_quoted_record_is_atomic(self):
        inventory = self.seeded_inventory()
        with self.assertRaises(InvalidManifest):
            import_manifest(io.BytesIO(b'sku,quantity,note\nA,8,valid\nB,2,"unfinished'), inventory)
        self.assert_seed_unchanged(inventory)

    def test_read_error_propagates_same_exception_and_is_atomic(self):
        inventory = self.seeded_inventory()
        error = OSError("connection interrupted")
        stream = BrokenReader(error)
        with self.assertRaises(OSError) as caught:
            import_manifest(stream, inventory)
        self.assertIs(caught.exception, error)
        self.assert_seed_unchanged(inventory)
        self.assertFalse(stream.closed)

    def test_success_keeps_caller_stream_open(self):
        stream = io.BytesIO(b"sku,quantity,note\nA,2,ok\n")
        import_manifest(stream, Inventory())
        self.assertFalse(stream.closed)
        self.assertEqual(stream.read(), b"")

    def test_validation_failure_keeps_caller_stream_open(self):
        stream = io.BytesIO(b"sku,quantity,note\nA,0,invalid\n")
        with self.assertRaises(InvalidManifest):
            import_manifest(stream, Inventory())
        self.assertFalse(stream.closed)

    def test_reading_begins_at_current_position(self):
        stream = ShortReader(b"skip!sku,quantity,note\nA,4,ok", max_fragment=5)
        self.assertEqual(stream.read(5), b"skip!")
        inventory = Inventory()
        self.assertEqual(import_manifest(stream, inventory), ImportSummary(1, 4, ("A",)))
        self.assertEqual(inventory.quantities, {"A": 4})
        self.assertFalse(stream.closed)

    def test_nonpositive_chunk_size_does_not_read_or_change_inventory(self):
        for chunk_size in (0, -1):
            with self.subTest(chunk_size=chunk_size):
                stream = ShortReader(b"sku,quantity,note\nA,2,ok\n")
                inventory = self.seeded_inventory()
                with self.assertRaises(ValueError):
                    import_manifest(stream, inventory, chunk_size=chunk_size)
                self.assertEqual(stream.reads, 0)
                self.assertFalse(stream.closed)
                self.assert_seed_unchanged(inventory)

    def test_quantity_snapshot_cannot_change_inventory(self):
        inventory = self.seeded_inventory()
        snapshot = inventory.quantities
        snapshot["A"] = 999
        snapshot["NEW"] = 1
        del snapshot["OLD"]
        self.assert_seed_unchanged(inventory)


if __name__ == "__main__":
    unittest.main()
