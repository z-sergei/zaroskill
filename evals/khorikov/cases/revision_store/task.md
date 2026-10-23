# Test a document revision store

Create a maintainable, behavior-focused test suite for `revision_store.py` using only Python 3.11+ and the standard library. Add only `tests/test_*.py` files and `report.md`. Do not change production code or other supplied files. The evaluator will run `python -m unittest discover -s tests -p 'test_*.py'` from the project root. Import the public API from `revision_store`.

Use the public contract below as the authority, including when implementation details suggest another behavior. Assert meaningful observable outcomes. Avoid assertions on private state, private helpers, internal call counts, or a particular implementation strategy. Tests must be deterministic, isolated, and independent of execution order. In `report.md`, briefly explain the behaviors covered and any deliberate testing limits.

## Public API and supported inputs

The module exports a class `RevisionStore` and these exception classes:

- `DocumentExistsError`, a subclass of `LookupError`.
- `DocumentNotFoundError`, a subclass of `LookupError`.
- `RevisionNotFoundError`, a subclass of `LookupError`.
- `VersionConflictError`, a subclass of `RuntimeError`.

Each new `RevisionStore()` is empty and independent of every other store. The store is in memory and synchronous. Persistence, concurrency, and thread safety are outside this task.

A **document ID** must have exact built-in type `str` and must not be empty. A wrong type raises `TypeError`; an empty string raises `ValueError`. IDs are case-sensitive and are used verbatim: whitespace and Unicode are supported, with no trimming or normalization.

**Content** must have exact built-in type `dict`. Each key must have exact built-in type `str`. Each value must be either an exact built-in `str` or an exact built-in `list` whose elements are all exact built-in `str` values. An empty dict, empty key, empty string, and empty list are valid. Content with any unsupported type raises `TypeError`. Nested dictionaries, numbers, booleans, nulls, tuples, and subclasses of the supported built-ins are not accepted in their places. The store does not modify caller-owned input objects.

A **version** or **expected version** must have exact built-in type `int` and be positive. A wrong type, including `bool`, raises `TypeError`; zero or a negative integer raises `ValueError`. The special value `None` is additionally allowed only for the optional `version` argument of `read`, where it means the current version.

A **snapshot** is an ordinary dict with exactly these keys:

```python
{
    "document_id": "the original ID",
    "version": 1,
    "content": {"title": "Draft", "tags": ["internal"]},
}
```

Every returned snapshot and every returned outer list is detached from stored data and from other returned snapshots. This includes the snapshot's content dict and any lists inside it. Mutating input content after a successful call, or mutating any returned dict or list, must never alter stored current or historical revisions or a separately returned snapshot. Later successful writes must not change previously returned snapshots. Object identities and the sharing of immutable strings are unspecified.

## Operations

### `create(document_id, content)`

Creates a new document at version 1 and returns its snapshot. Validate the ID, then content, before checking for an existing document. An existing ID raises `DocumentExistsError` and preserves its complete history. Each document's version sequence is independent.

### `read(document_id, *, version=None)`

Returns a snapshot of the current version when `version` is omitted or `None`, or the indicated historical version otherwise. Versions are numbered from 1, with no gaps. Validate the ID, then the supplied version, before looking up the document. A missing document raises `DocumentNotFoundError`. A positive version greater than that document's current version raises `RevisionNotFoundError`.

### `history(document_id)`

Returns a list of snapshots for all of the document's revisions, in ascending version order, including the current revision. Validate the ID before looking up the document. A missing document raises `DocumentNotFoundError`.

### `replace(document_id, content, *, expected_version)`

Replaces the document's entire content; it does not merge keys. The caller must explicitly supply the expected current version. Validate the ID, expected version, and content, in that order, before looking up the document. A missing document raises `DocumentNotFoundError`. If the expected version differs from the current version, raise `VersionConflictError` and preserve all state. A successful replacement appends exactly one revision, numbered current version plus 1, and returns its snapshot. Replacing with equal content still creates a new revision. Prior revisions remain readable and unchanged.

### `replace_many(changes)`

Performs one atomic batch of replacements. `changes` must have exact built-in type `list`; every entry must have exact built-in type `tuple` and contain exactly `(document_id, expected_version, content)`. A wrong outer type, wrong entry type, or wrong tuple length raises `TypeError`.

First validate the outer list and all entries without changing store state. Validate entries left to right: tuple shape, ID, expected version, content, then ID uniqueness. An ID repeated within the batch raises `ValueError`, even if its contents and expected version are identical. These validations finish before any document existence or version-conflict checks.

Next, for each entry from left to right, check that the document exists and then that the expected version equals its current version, using `DocumentNotFoundError` and `VersionConflictError` respectively. Only after every entry passes may the batch commit. Any validation, missing-document, or conflict error leaves every document and every history unchanged; it also must not create a previously absent document.

On success, each document gains exactly one new revision, using full-content replacement and the same rules as `replace`. Return a list of the resulting snapshots in **input order**. An empty list returns `[]` and changes nothing. The call does not modify `changes`, its entry tuples, or input content.

## Error and testing boundaries

Exception classes and the validation order above are contractual; exception messages and `.args` are not. Invalid calls have no persistent effects. Normal Python argument-binding errors follow the declared method signatures. There are no deletion, persistence, listing, or patch/merge operations. Inputs mutated concurrently with an operation and subclass/custom-object side effects are outside scope. Within the supported types, use ordinary public calls and independent expected values to demonstrate outcomes.
