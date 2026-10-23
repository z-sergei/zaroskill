# Test a bounded expiring cache

Write a Python 3.11 `unittest` suite for `app.TTLCache`. Put your tests in `tests/` so they run with:

```text
python -m unittest discover -s tests -v
```

Use only the standard library. Exercise the public API and use an injected controllable clock; do not wait for real time. Do not change `app.py`. Your suite should protect the contract below while allowing behavior-preserving implementation changes.

## Public contract

`TTLCache(capacity, clock)` creates an empty cache. `capacity` must be a positive integer, excluding `bool`; otherwise construction raises `ValueError`. `clock` must be callable; otherwise construction raises `TypeError`. The clock returns nondecreasing times in seconds as int or float values that convert to finite floats. Times, durations, and deadlines follow Python floating-point arithmetic and rounding; exact real-number arithmetic is not promised. The caller controls the clock. No clock call occurs during construction.

The public methods are:

- `put(key, value, ttl)` inserts or replaces one entry and returns `None`.
- `put_many(entries)` accepts an iterable of `(key, value, ttl)` triples, applies them in iterable order, and returns `None`.
- `get(key, default=None)` returns the live value for `key`, or the exact supplied `default` object if the key is absent or expired.
- `snapshot()` returns a plain `dict` containing every live key and value in order from least recently used to most recently used. It does not change recency.

Keys must be nonempty strings. `put`, `put_many`, and `get` reject invalid keys with `ValueError`. A TTL must be an `int` or `float`, excluding `bool`, that converts to a positive finite float. This converted float is the duration used in deadline arithmetic; invalid TTLs, including integers outside the finite float range, raise `ValueError`. An incorrectly shaped batch entry raises `ValueError`. Values are copied according to Python’s `copy.deepcopy` protocol on input and on successful reads. Ordinary built-in mutable containers, including nested lists and dictionaries, are detached from caller inputs and returned values. Types that `deepcopy` treats as atomic or that define their own copying behavior follow that protocol’s identity and sharing semantics; their intentionally shared mutable state is outside the detachment guarantee. A default returned on a miss is not copied.

Each valid nonempty write operation reads the clock exactly once. All entries in a batch use that same time. A write at time `t` with TTL `d` is live for `now < t + d` and expired for `now >= t + d`. Replacing a key resets its deadline using the new TTL and makes it most recently used. Reading a live entry makes it most recently used but does not extend its deadline. A miss does not change recency. Each valid `get` and each `snapshot` reads the clock exactly once, including a miss or an empty snapshot.

Before serving a valid read or applying a valid nonempty write, the cache removes every expired entry. A write processes its entries in order. After each entry, an entry whose rounded deadline is already at or before the sampled time is absent; this also removes an overwritten previous value. If there are then too many live entries, the cache evicts the least recently used entry. Repeated keys in a batch are processed like repeated writes at the batch's single sampled time. Consequently, the later occurrence supplies the value and TTL if that key remains present. Even a new entry inserted earlier in a batch may be evicted by a later entry in the same batch.

A batch is atomic with respect to preparation: the whole iterable must be consumed, each entry validated, and every value copied successfully before the clock is read or cache state changes. If iteration, validation, or copying raises an exception, propagate that exception and preserve all previous entries, values, deadlines, and recency. An invalid single write has the same guarantee. An invalid `get` key raises before reading the clock or changing state. An empty batch performs no clock read and no state change.

Tests should establish expected results independently from this contract. Internal fields, helper methods, data structures, and exact exception messages are implementation details.
