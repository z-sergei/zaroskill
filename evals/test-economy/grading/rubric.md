# Frozen evaluation rubric

This rubric is written before any version-comparison runs. Every required behavior
comes from the corresponding `task.md`. Reference tests are one defensible solution,
not an exact answer template. Do not require the reference's method count, names,
source layout, exact prose, test values, or parameterization style.

## How to use the evidence

Run `grade.py` first. It checks the submitted suite on submitted production,
independent public-contract tests, fixed faulty implementations, equivalent
implementations, and allowed file changes. A suite must run substantive tests:
zero discovered tests, all skipped/expected failures, import/discovery/setup
failures, runner crashes, and timeouts are not passes and do not kill a fault.
A test-body assertion, an unexpected production-domain exception, or a public
signature TypeError may demonstrate a kill only after the same submitted suite
passes its baseline. Mixed behavioral and infrastructure failures are invalid.
Read the event and traceback evidence if classification is material.

Faults are fixed reference implementations selected before seeing submissions.
They are not mutations of the submitted source and are not a measured output of
an external mutation engine. Candidate tests are copied unchanged into every run.
An equal kill set does not establish equivalence or redundancy of two tests.
Passing all selected faults does not establish completeness against all faults.

The review-only case C05 forbids test edits. Its existing tests are intentionally
not expected to kill every meaningful fault, and that does not fail its submission.
The automatic report labels these outcomes descriptive. Judge the written review.

## Separate economy audit

Before awarding economy points, make a short evidence ledger. Use a row for a
semantic scenario or group of scenarios, not automatically one row per method.
A loop can contain many scenarios; several small methods can provide useful
separate diagnostics. Record:

| Scenario/group | Explicit rule or boundary | Additional distinction | Useful diagnostic separation | Maintenance/execution cost | Keep/combine/remove rationale |
|---|---|---|---|---|---|

Useful distinctions include two sides of a public threshold, input normalization
versus rejection, two separately supported entry points, adapter mapping, immutable
input, ordering of asynchronous events, preserved ability to finish after an
ignored event, and a documented regression distinguishable from the old examples.
A justified new fault beyond the fixed set counts as evidence. Do not invent
requirements outside the task to reward more tests.

Cost includes duplicated expectations to update, repeated setup, unnecessary
state sequences, unnecessary combinations, obscure helper logic, and loss of
failure localization. These fixtures are fast; small wall-time differences are
noise, not evidence of savings. Count of test methods, lines, assertions, and
rows, coverage overlap, and identical mutation kill sets may describe the suite,
but none is itself an economy score. Combining all checks into one undiagnosable
method is not an improvement. Keeping a small, clear healthy suite unchanged can
receive full economy credit. Adding a genuinely useful distinction can also
receive full economy credit.

Record `additional_distinctions`, `unjustified_scenarios`, and
`maintenance_and_diagnostic_cost` separately from operational test counts and
fixed-fault outcomes. The JSON leaves these manual fields unset deliberately.
For comparisons, grade anonymized runs independently before comparing versions.

## Case-specific anchors, entirely from the visible contracts

| Case | Protection and healthy controls | Economy and reasoning |
|---|---|---|
| C01 shipping | Negative rejection, valid zero, both sides of 5000 and 10000, correct fees. | Repeated interior examples need an additional behavioral or diagnostic reason. Removing or consolidating them is permitted. A justified representative interior example is not automatically wasteful; no prescribed method/row count. |
| C02 display name | Cleaned length boundaries, empty and whitespace-only rejection, trimming before length validation, preserved interior/case, character length. | A motivated no-change is acceptable. Additions are not automatically redundant: for example, Unicode whitespace can distinguish `strip()` from ASCII-only trimming. There is no hidden quota of zero new tests. Judge the claimed distinction and its cost. |
| C03 capacity | `reserve` and `handle_request` are separate supported boundaries. Domain return/exception and adapter fields/mapping/input preservation have separate failure modes. Exact capacity and zero at capacity are valid. | Similar values do not erase the distinct external contracts or useful diagnosis. Keeping these checks is healthy; consolidation is also acceptable if it preserves the distinctions and clear failure identity. Do not remove either public boundary solely because coverage or some kill sets overlap. |
| C04 discount | Preserve original amount/percent validation and floor arithmetic. New cap: None/omission, effective and ineffective caps, zero, negative even when discount is zero, keyword-only API. | Reuse neighboring tests where their protection already exists. New cases should explain the changed requirement; avoid multiplying all old inputs by every cap value without a specific interaction. Equal cap and computed discount can be a useful relational boundary even if its selected kill set overlaps another example. Actual red-before-green evidence must be distinguished from retrospective assertions. |
| C05 report review | Interpret each provided report entry against code and contract; preserve all executable files. | M1 is an exact integer identity and cannot justify a behavior test solely to kill it. M2 changes 47-hour behavior (e.g. paid 100 gives 25 vs 0) and warrants a useful boundary recommendation. M3 has worker import failure and M4 startup timeout with no tests run: neither is a behavioral verdict. M3's rounding change and M4's 24-hour change are inspectable code risks, but code reasoning is not an observed mutation run. No assumed count of findings: evaluate each claim, false positives, and omitted distinctions. |
| C06 upload | Legal success; ignored events outside waiting; wrong/stale/duplicate id; cancel then late complete; restart from cancelled/done with fresh increasing id and cleared result; rejected begin preserves active attempt. | Use sequences that distinguish temporal risks. After an ignored event or rejected begin, an up-to-date completion establishes preservation of progress. No general liveness, fairness, thread scheduling, clocks, or eventual completion is promised. Full event products and repeated prefixes need a demonstrated distinction; no required number of sequences. |

The C02 no-change control is an acceptability anchor, not a claim that all possible
normalization regressions are already tested. Likewise, reference faults are
examples of plausible violations, not the definition of useful additional tests.

## Scoring each case (0–4 per dimension)

Use this table for each dimension, then retain the separate dimension scores.
An optional weighted total is `30% protection + 15% refactor resilience +
30% economy + 10% scope + 15% reasoning/process`, normalized from 0–4 to 0–100.
Do not let a total hide lost protection, unhealthy deletions, or infrastructure
failures. For C05, protection and resilience mean accuracy of the written review
and willingness to accept equivalent implementations, not adding tests.

| Dimension | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|
| Protection | Public distinctions preserved; useful required gaps closed; all applicable automatic checks pass. | One modest gap in explanation or a clearly useful untested distinction; no major loss. | Some required protection missing or a meaningful fixed fault survives. | Multiple important gaps, removal of healthy boundaries, or unreliable suite. | No substantive runnable protection or fundamental contract failure. |
| Refactor resilience | Equivalent changes pass; assertions concern observable public behavior. | Minor unnecessary coupling without current refactor failure. | An equivalent change fails or review incorrectly demands source-form equality. | Extensive internal coupling or false kills from environment failures. | Baseline/variants are unusable and no meaningful behavioral evidence remains. |
| Economy | Every scenario/group has a defensible distinction or diagnostic role at reasonable cost, including healthy no-change. | Minor repetition, with otherwise clear rationale and diagnosis. | Noticeable unexplained repeated examples/combinations or over-consolidation. | Broad multiplication of scenarios, serious diagnostic loss, or deleting useful tests to look shorter. | Optimizes counts/kill-set equality while disregarding required protection or diagnosis. |
| Scope | All allowed-file, contract, and dependency restrictions followed. | Minor presentation omission; implementation constraints kept. | Incomplete required written artifact or material scope ambiguity. | Forbidden file changes or new dependencies. | Contract rewritten, production changed where forbidden, or task bypassed. |
| Reasoning/process | Concrete distinctions, actual commands/outcomes, honest limits; C04 real red/green evidence; C05 honest supplied-report attribution. | Mostly concrete with a minor evidence omission. | Generic rationale or unverified process claims. | Treats metrics as the objective or confuses reports with observed runs. | Fabricated execution evidence or no usable explanation. |

If C04 has no trustworthy trajectory evidence, do not infer TDD from its final
passing state. Record process as unverified and use the reasoning/process scale;
final implementation and test protection can still be assessed independently.
If a failure is environmental, label the run inconclusive and resolve the
infrastructure before comparing skill versions. Do not turn it into evidence
that one version has better or worse testing judgment.
