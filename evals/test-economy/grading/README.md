# Economy fixture evaluation

Six independent Python standard-library unittest cases live under `../cases`.
Give evaluated agents only their case directory plus the externally selected
skill version. Do not give them `grading/`, `reference_*`, faults, or preflight
results. The fixture author did not consult either skill version.

Run a full submission (a directory containing `cases/<id>`):

```sh
python3 grading/grade.py --run /absolute/path/to/run --output /absolute/path/to/result.json
```

Use `--case 03_capacity_boundaries` to grade a single case and `--timeout 10` to
change the per-process deadline. Exit 0 means automatic gates pass; exit 1 means
one or more fail. A passing exit code is never a completed manual economy grade.
Apply `rubric.md` and fill the separate semantic/cost fields in the report.

`preflight.py` builds an internal reference submission, checks every independent
contract, runs unchanged reference tests against every fixed fault and equivalent
refactor, checks the initial suites, verifies the TDD red/green transition, and
exercises runner failure classification. It writes `preflight.json` and detailed
evidence to `.preflight/`. This is preflight validation of authored fixtures,
not a real mutation-tool report. `reference_tests/05_mutation_report` contains
oracle tests used only for preflight; C05 submissions must keep their original
suite unchanged.

All variant executions use fresh temporary copies under `.scratch/`. Production
is replaced in the copy; submitted tests are byte-checked before and after the
run. The actual submitted directory is never edited. Python is run in isolated
mode with bytecode writing disabled. Import/discovery/setup/teardown failures,
empty or all-skipped suites, crashes, and timeouts cannot count as killed faults.
The TypeError public-call category is a pragmatic phase-based classification;
read logs when it matters. Baseline failure always prevents mutation credit.

These are trusted small development fixtures, not a sandbox for hostile Python.
The subprocess timeout limits normal hangs; the runner does not prevent arbitrary
code, filesystem/network access, forged runner output, or spawning children.
Do not run adversarial submissions. All production domains are explicitly scoped
in task.md: handling other types, concurrency, I/O, and performance guarantees
must not be invented as grading requirements.

Limitations:

- Small fixed faults and equivalence samples do not prove exhaustive correctness
  or redundancy. A new justified distinction can be useful beyond these faults.
- The independent contract tests check implementation behavior, not whether a
  candidate's own tests cover every possible requirement.
- Replacing the whole production module checks public behavior and tolerates
  architecture changes permitted by the task; it is not mutation of a candidate's
  specific syntax or measurement of an external tool's mutation score.
- File snapshots cannot prove TDD chronology. Use actual agent execution records
  and compare them with response.md; do not trust an unsupported retrospective
  red/green assertion as execution evidence.
- Economy, diagnostic value, review accuracy, and incremental distinctions require
  a human rubric. Method count, lines, overlapping coverage, and equal kill sets
  are not their substitutes.
- C02 accepts justified no-change and justified new distinctions (for example
  Unicode whitespace). C03 is a healthy control for separate public boundaries.
- C05's mutation-report.json is an explicit synthetic supplied report. M3/M4
  infrastructure statuses were not reproduced by a real mutation engine.
- A fresh module/process avoids contamination between runs, but OS scheduling and
  runtime noise make timing unsuitable as a compression score in these tiny cases.

Freeze procedure: finish successful preflight, retain `freeze_manifest.json`, and
make no case, oracle, fault, or rubric edits during compared runs. If a genuine
fixture defect requires a change, record it, create a new freeze, and rerun all
compared versions against that freeze. Never tune a fault after seeing results
from one skill version alone.
