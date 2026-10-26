# Directed probe assessment against the unchanged contracts

This assessment was prepared after the original comparison, using only the
original evaluation and the five specifically authorized source files. No skill
versions, participant answers, version keys, or judge reports were read. Exact
source paths and byte hashes are recorded in `provenance.json`.

| Variant | Concrete witness | Assessment from the original task |
|---|---|---|
| C04 `zero_cap_skips_old_validation` | `discounted_total(-1, 15, max_discount_cents=0)` returns `-1`; invalid percent with zero cap also returns an amount. | Fault. The old nonnegative-subtotal and 0–100-percent validation is explicitly preserved. A zero cap does not waive it. |
| C04 `zero_subtotal_skips_cap_validation` | `discounted_total(0, 15, max_discount_cents=-1)` returns `0`. | Fault. A negative cap must raise `ValueError`, explicitly even when the computed discount is zero. |
| C06 `numeric_boolean_returns` | Idle `cancel()` returns integer `0`; an accepted `complete()` returns integer `1`. | Fault. The methods promise the Python values `False` and `True`. Truthiness and numeric equality do not establish this result contract; identity assertions distinguish it. This says nothing about the exact type of an attempt id. |
| C06 `two_id_cycle_after_success` | `begin; complete; begin; complete; begin` produces ids `1, 2, 1`. | Fault. Every successful begin in one session must return an id strictly larger than the previous one. The contract is not limited to one restart. The same reuse can also admit an older callback. |
| C06 `integer_subclass_ids` | `begin()` returns `_AttemptId(1)`, where `_AttemptId` inherits `int` and does not override behavior. | Separate equivalence diagnostic. Ordinary reading of “positive integer id” admits this subclass. Equality, ordering, positivity, increasing ids, and accepted callbacks remain correct. Exact `type(id) is int` was never promised. Do not turn this interpretation into an additional fixed gate or silently penalize it as a proven contract violation. |

Only four previously identified faults are added to the original twelve. They
are copied byte-for-byte, rather than reconstructed to match new reference tests.
The initial task files, initial production/tests, and correct production reference
implementations are copied unchanged. Follow-up reference tests and independent
contract checks are strengthened where needed:

- C04 adds zero-cap interaction with the preserved validation and a zero-subtotal
  witness for negative-cap validation. The original independent contract already
  covered a zero-subtotal negative cap; it now also covers zero-cap old validation.
- C06 uses explicit boolean results in reference tests and extends the successful
  restart sequence to distinguish the two-id cycle. The independent contract
  already checked boolean identity and now adds consecutive successful cycles.
- Both oracle suites accept an `int` subclass. The diagnostic is reported
  separately whether a submitted suite accepts or rejects it.

These observations justify the selected checks, not exhaustive correctness.
Additional tests need a meaningful distinction or diagnostic purpose; neither
counting methods nor comparing equal kill sets determines redundancy.
