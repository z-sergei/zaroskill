# Apply edits to original text

Implement `apply_edits(text, edits)` in `app.py` using the Python standard library.

`text` must be a Python string. `edits` is any iterable of edit records, including a one-shot generator. Each record must be a tuple or list of exactly three values `(start, stop, replacement)`:

- `start` and `stop` must be integers; booleans are not accepted.
- `replacement` must be a string.
- `0 <= start <= stop <= len(text)`.

Offsets count Python Unicode characters, as ordinary Python string indexing does. They always refer to the original `text`, regardless of how long earlier replacements are. A record replaces the half-open range `[start, stop)` with `replacement`. A record with equal offsets inserts text at that position. An empty replacement deletes a nonempty range; an empty insertion is valid and still subject to the overlap rules.

Edits may arrive in any order. Apply them in increasing original offset order. Multiple insertions at the same position appear in their original encounter order. At the start of a nonempty replacement, insertions appear before that replacement's text; at its end, insertions appear after its text. Adjacent nonempty replacements are allowed, including insertions at their shared boundary.

Nonempty ranges must not overlap, including identical or nested ranges. An insertion strictly inside a nonempty range is also an overlap. Insertions exactly at either endpoint are allowed. Any overlap raises `ValueError`.

Reject a non-string `text`, a non-iterable `edits`, a record of the wrong shape, a non-integer offset (including a boolean), or a non-string replacement with `TypeError`. Reject invalid bounds with `ValueError`. Validate records and snapshot their three values as they are encountered. If an iterator itself raises an exception, propagate that exception unchanged. Do not iterate the input collection a second time. After collecting and validating records, check overlaps. No particular exception message is required.

Return the resulting string. An empty collection returns `text` unchanged. Preserve the supplied collection and every supplied record: do not reorder or modify them. Do not retain input records for later calls, and keep no state between calls.

For example:

```python
apply_edits("abcdef", [(4, 6, "Z"), (1, 3, "LONG")]) == "aLONGdZ"
apply_edits("abcd", [(1, 3, "R"), (1, 1, "A"), (3, 3, "B")]) == "aARBd"
apply_edits("ab", [(1, 1, "z"), (1, 1, "a")]) == "azab"
```
