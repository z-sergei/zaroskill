# Directed follow-up evaluation

This portable standard-library Python harness covers the unchanged initial tasks
`04_discount_cap` and `06_upload_workflow`. It is a directed check of issues found
on already exposed tasks, not a new holdout and not part of the first preregistered
comparison. Its freeze occurs after that comparison and before the separate
follow-up runs. The fixture author did not read skill versions, participant answers, version keys,
or judge reports; the four faults and diagnostic probe were explicitly supplied.

Give agents only the corresponding case directory and the externally selected
skill version. Both versions must get identical initial files. Do not expose the
hidden faults, reference tests, independent contracts, or assessments to agents.
The tasks, their initial production/tests, and correct production references are
byte-preserved; `provenance.json` records the checks and authorized probe hashes.

Run from any working directory:

```sh
python3 -B /absolute/path/to/followup/evaluation/grading/grade.py --run /absolute/path/to/run --output /absolute/path/to/report.json
```

`run` contains `cases/04_discount_cap` and `cases/06_upload_workflow`.
Use `--case 04_discount_cap` or `--case 06_upload_workflow` for one case, and
`--timeout 10` for a different per-process deadline. The JSON summary reports:

- 16 fixed faults: 12 original plus four directed additions;
- the two original equivalent implementations;
- a separately labeled, non-gating `integer_subclass_ids` diagnostic, with both
  submitted-suite and independent-contract outcomes.

Exit 0 means the fixed automatic gates passed. Exit 1 means at least one failed.
The diagnostic cannot affect this exit code. A passing exit code does not complete
the semantic/economy evaluation; apply `rubric.md` separately.

`preflight.py` verifies initial suites, correct reference implementations,
independent contracts, all fixed faults, original refactors, runner failure
classification, reference red/green evidence, and the non-gating diagnostic.
It also checks that a synthetic suite rejecting the subclass still passes the
fixed gates when all required protection is retained. The result and full evidence
are saved in `preflight.json` and `.preflight/`; these are harness checks, not an
external mutation-engine run or proof of an evaluated agent's TDD chronology.

`freeze.py` hashes all retained follow-up material, including preflight evidence,
except its self-referential manifest, bytecode, and temporary `.scratch/` copies.
Verify the snapshot without rewriting it:

```sh
python3 -B /absolute/path/to/followup/evaluation/grading/freeze.py --check
```

After follow-up agent runs begin, do not change task, oracle, fault, rubric, or
checker files. If a defect requires repair, declare a new freeze and rerun all
compared versions. Do not tune the directed faults to one new version's outcome.

Limitations:

- The selected faults/refactors are small behavioral samples, not exhaustive
  correctness or a general mutation score. They replace fixed implementations,
  rather than mutating an evaluated implementation's syntax.
- Additional meaning, unjustified scenarios, and diagnostic/maintenance cost need
  separate judgment. Test method count and equal kill sets are not substitutes.
- The subclass diagnostic has an explicit interpretation caveat: ordinary positive
  integer includes an `int` subclass, while exact built-in type was not promised.
  Keep ambiguity separate; do not make it a hidden mandatory requirement.
- A final snapshot cannot prove red-before-green development. Use actual execution
  records and distinguish them from retrospective claims in response.md.
- Each execution uses a temporary copy under `.scratch/`; tests are byte-checked
  before and after. Import/discovery/fixture errors, no tests, crashes, and timeouts
  cannot receive kill credit. Public-call TypeError classification is heuristic;
  read evidence when material, and require a passing baseline first.
- This is a runner for trusted development submissions, not a hostile-code sandbox.
  It does not prevent arbitrary Python filesystem/network access or spawned child
  processes. It has no third-party dependencies and uses no network itself.
