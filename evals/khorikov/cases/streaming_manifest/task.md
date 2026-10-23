# Delivery manifest tests

Write behavioral regression tests for `manifest.py`, using Python 3.11+ and only the standard library. Put executable `unittest` tests in `tests/test_*.py` and write `report.md` explaining the behavior covered, your choice of observations, and the command you ran. Run the tests. Leave all supplied source files unchanged. The test command is:

```
python -m unittest discover -s tests -p 'test_*.py' -v
```

Focus on externally visible correctness and useful failure detection. Assertions should have independently determined expected outcomes. Tests must also remain valid when implementation details are refactored without changing this contract. Do not inspect private fields or helpers, patch the importer internals, or require a specific number of reads or calls to a private commit method.

## Public contract

`Inventory(initial_stock=None)` accepts an optional mapping of nonempty SKU strings to nonnegative integer quantities. Those preconditions may be assumed. Its `quantities` property returns a detached dictionary snapshot. Its `received_lines` property returns a tuple of `DeliveryLine(sku, quantity, note)` records accepted by successful imports, in import order and then CSV record order. Initial stock has no corresponding delivery records. Both `DeliveryLine` and `ImportSummary` are immutable dataclasses with value equality.

`import_manifest(stream, inventory, *, chunk_size=4096)` reads from the caller's current position in a binary stream. `stream.read(n)` follows the normal binary-stream contract: it returns at most `n` bytes, may return fewer, and returns `b""` only at EOF. Nonseekable streams are supported. `chunk_size` is an integer; positive values are supported and nonpositive values raise `ValueError` before reading or changing inventory. Read sizes and read counts are implementation details. On success the stream has been consumed to EOF. The importer never closes or seeks the caller-owned stream, on success or failure. Stream position after a failure is unspecified.

The manifest format is:

- Strict UTF-8, optionally beginning with one UTF-8 byte order mark. Multibyte characters and the byte order mark may span reads.
- CSV using the standard `csv.reader` Excel dialect with `strict=True`. Physical line endings are LF or CRLF. The final record may omit its terminating newline. Quoted fields can contain commas, escaped double quotes, and embedded LF or CRLF. Empty physical lines outside quoted fields are ignored, including before the header. Bare-CR physical line endings are outside the supported input contract.
- The first logical record is exactly `sku,quantity,note`, with that spelling and order. Missing or different headers are invalid. A header with no data records is a valid empty import.
- Every data record has exactly three fields. Surrounding whitespace is stripped from `sku` and `quantity` using `str.strip()`. The resulting SKU must be nonempty and remains case-sensitive.
- The stripped quantity consists only of ASCII digits, and its integer value is between 1 and 1,000,000 inclusive. Leading zeroes are accepted. Signs, decimal points, empty quantities, and non-ASCII digits are invalid.
- The note is preserved exactly, including whitespace and embedded line endings; it may be empty.

On success, every data record increments that SKU's existing quantity. Repeated SKUs accumulate, including across separate successful imports. Every accepted record is appended to `received_lines`, including repeated SKUs. The return value is `ImportSummary(line_count, total_units, skus)`, where the count and units describe this import only, and `skus` contains each normalized SKU once, in order of first appearance in this import. For an empty import the summary is `ImportSummary(0, 0, ())` and inventory is unchanged.

Malformed UTF-8, CSV syntax errors reported by the stated dialect, invalid headers, and invalid data records raise `InvalidManifest` (a `ValueError` subclass). Error-message wording is not part of the contract. An `OSError` from `stream.read` propagates unchanged. For any such failure the inventory's quantities and received lines must both remain exactly as they were before the import, even if earlier records were valid. No concurrency or recovery from memory exhaustion is in scope.
