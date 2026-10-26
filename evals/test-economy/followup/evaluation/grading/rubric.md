# Follow-up rubric

This is a directed check of previously found problems on two already exposed
tasks. It is not a fresh holdout and is not part of the original preregistered
comparison. The additional faults were selected after that comparison, then
frozen before the separate follow-up agent runs. Keep those results separate.
Both evaluated versions receive the same unchanged initial `task.md`, production,
and tests; hidden grading material is not agent input.

## Automatic evidence

The grader checks the submitted baseline, nonempty unittest execution, independent
public-contract checks, sixteen fixed faulty implementations, and the original
two equivalent implementations. Production is replaced only in temporary copies;
submitted tests remain byte-identical. The sixteen faults consist of twelve
original faults and four directed additions assessed in `probe_assessment.md`.

Baseline must pass before a fault can receive kill credit. Assertion failures,
production-domain exceptions, and public-call TypeErrors are distinguished from
import/discovery/setup/teardown failures, no tests, crashes, and timeouts. Mixed
behavioral and infrastructure failures are invalid. The latter outcomes cannot
be treated as successful fault detection. Read logs for ambiguous classifications.

The `integer_subclass_ids` result is an explicitly separate, non-gating diagnostic.
Ordinary “positive integer” permits a subclass of `int`; the task does not promise
the exact built-in type. A rejecting suite may expose a stronger assumption, but
record that issue separately and do not silently turn it into lost fixed-gate
points, an additional mandatory criterion, or a proven production violation.
The diagnostic cannot change `automatic_gates_passed` or the process exit code.

## Meaning, economy, and diagnosis remain separate

For each scenario/group, record its explicit contract distinction, useful failure
localization, and maintenance/execution cost. Then record separately:

| Field | What to judge |
|---|---|
| Additional distinctions | A new boundary, validation interaction, event order, exact promised output, or concrete regression that existing examples do not distinguish. |
| Unjustified scenarios | Repeated examples or event combinations with no additional behavioral or diagnostic purpose. Do not infer this solely from overlapping coverage or equal kill sets. |
| Maintenance/diagnostic cost | Repeated expectations/setup, opaque helpers, unnecessary products of inputs/events, or lost failure localization. |
| Process/scope | Allowed files preserved, requirements unchanged, actual commands/outcomes, and honest limitations. Final snapshots alone do not establish TDD chronology. |

C04's zero-cap/old-validation interaction and zero-subtotal/negative-cap interaction
are meaningful public requirements; they do not justify multiplying every value
by every cap. Existing neighboring tests should still be used where sufficient.
C06 distinguishes explicit boolean outcomes and repeated successful restarts;
a short sequence or loop can do this without a full event product. Do not promise
liveness or concurrency behavior absent from the task.

Method count, source lines, assertion count, equal kill sets, and tiny runtime
differences are not economy metrics. A concise suite can lose useful protection;
a larger suite can add a defensible distinction. Keep semantic/economy notes
separate from the automatic fault/refactor totals. No particular reference method
count, method names, layout, prose, or parameterization is required.

For each dimension independently, use 0–4 if numerical ratings are wanted:
4 = complete and well supported; 3 = a minor limitation; 2 = a meaningful gap;
1 = multiple serious gaps; 0 = no usable evidence. Rate protection, resilience to
the original refactors, economy/diagnosis, and process/scope separately. Treat an
environmental failure as inconclusive until resolved, not evidence for a version.
Do not fold the subclass diagnostic into a total without explicitly disclosing a
new interpretation and keeping it outside this frozen follow-up's fixed gates.
