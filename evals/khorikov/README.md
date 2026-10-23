# Khorikov testing skill evaluations

This package tests whether an agent using the [portable skill](../../skills/khorikov-unit-testing/SKILL.md) writes useful tests: correct behavior passes, meaningful faults fail, and equivalent refactors remain green. It also runs a bounded, autonomous improvement campaign. Test count, prose length, and line coverage are not optimization targets.

All portable tasks, fixtures, tests, prompts, and reports are in English. This copy contains the portable evaluator and fictional fixtures; previous project-specific calibration and historical run outputs are not included.

## Run the package

Use Python 3.11 or newer on macOS/Linux. Fixture verification and grading use only the Python standard library; process timeout cleanup uses POSIX process groups. Agent generation and research additionally require an authenticated `codex` CLI on `PATH`. They inherit the CLI's configured model and reasoning settings; the runner does not supply a model override or require a separate API key. Each model call uses ephemeral mode with the CLI's `workspace-write` sandbox. The host still needs access to its normal Codex authentication and runtime state.

Run commands from the repository root. Output directories must not already exist; choose a fresh directory for every run.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s evals/khorikov/tests -v

PYTHONDONTWRITEBYTECODE=1 python3 evals/khorikov/runner.py verify-fixtures \
  --output /tmp/khorikov-fixture-check

PYTHONDONTWRITEBYTECODE=1 python3 evals/khorikov/runner.py research \
  --skill skills/khorikov-unit-testing \
  --output /tmp/khorikov-research \
  --rounds 2 --repeats 2 --workers 2 --max-agent-calls 61 --agent-timeout 600
```

`verify-fixtures` checks that every variant applies once and compiles, then executes reference tests against the original, all faults, and all refactors. It fails unless the references detect every fault and pass every equivalent refactor. `research` performs this preflight itself before any agent calls. The runner's tests check evaluation and comparison behavior; they do not substitute for fixture execution.

Independent generations run two at a time by default, each in its own workspace. Use `--workers 1` for sequential execution. The research budget defaults to 61 agent calls and is enforced across workers. A failed call cancels queued work, waits for already running calls, and preserves completed results.

To generate and grade tests without proposing a skill revision:

```sh
python3 evals/khorikov/runner.py evaluate \
  --skill skills/khorikov-unit-testing \
  --split development --repeats 2 --max-agent-calls 18 \
  --output /tmp/khorikov-evaluation
```

`evaluate --split holdout` and `--split all` are available for final audits. With two repeats, `--split all` needs `--max-agent-calls 20` or higher. Keep holdout results outside the feedback used to propose revisions. A successful process exit alone does not establish test quality: inspect `evaluation.json` or `campaign.json`, including eligibility and per-invariant results.

## Improve existing suites

`evaluate --starting-tests PATH` runs maintenance tasks instead of starting with an empty suite. Supply `PATH/<case>-<repeat>/tests/` for every requested case and repeat, containing at least one `test_*.py`. The runner checks every input before making an agent call, keeps a provenance snapshot, and gives the agent a separate editable test copy. Public source, task, and skill remain protected. Reports include a compact ledger of retained, strengthened, replaced or justifiably removed scenarios.

The evaluation and each record carry `starting_tests` provenance with exact `initial_test_hashes`. Compare those hashes across skill versions to establish identical starts. Missing inputs, symlinks, changed source inputs or changed snapshots fail closed; all generations remain subject to the same original/fault/refactor checks. Existing tests may be changed, so unchanged file text or increasing test counts do not prove preservation. Compare their public behavioral discrimination.

For example, prepare one starting suite per development case under `/tmp/starting-suites/<case>-0/tests/`, then run:

```sh
python3 evals/khorikov/runner.py evaluate \
  --skill skills/khorikov-unit-testing --split development --repeats 1 \
  --starting-tests /tmp/starting-suites --max-agent-calls 9 \
  --output /tmp/khorikov-maintenance
```

Both compared skill versions should receive byte-identical starts and equal budgets. One output per condition is evidence about those artifacts, not a reliability estimate or proof of a causal skill effect. The autonomous `research` command retains its greenfield protocol; maintenance is an explicit `evaluate` mode and may be orchestrated separately.

## Research protocol

1. **Freeze.** Snapshot the incumbent skill and the evaluator, including the runner, test host, suite, case sources, grading rules, and reference tests. Record their hashes and verify fixtures. A changed evaluator invalidates the campaign.
2. **Measure.** Independent agents receive fresh workspaces containing the task, public source files, and the same skill snapshot. Every development case is generated the configured number of times. Each submitted suite runs against the original twice, with different hash seeds, then against the predefined faults and refactors.
3. **Propose.** A fresh agent receives development feedback: contracts whose mutated runs stayed green, uncredited execution outcomes, and refactor failures. It writes one generalizable hypothesis and edits existing skill Markdown. The runner checks unchanged metadata, file set, and non-Markdown files; valid local reference links; and Markdown growth bounded to 15 percent. Later proposers also receive prior rejected hypotheses, Markdown diffs, development feedback, and rejection decisions. They must address the observed failure or try a different hypothesis. The proposer receives no holdout feedback, quality-review outcome, or grading source.
4. **Compare.** Generate new tests with the candidate using the same cases and repeat count. For every fault, assertion-credit rate must not decrease and healthy-survival rate must not increase. Healthy survival is the fraction of repeated mutant runs on which all tests stay green. A strict improvement requires either higher assertion credit together with lower healthy survival for the same fault, or repair of an incumbent refactor failure. Converting an already failing execution into an assertion earns no strict improvement by itself. Every candidate submission must be eligible. The incumbent needs healthy original-source runs and complete measured variant evidence; a failed refactor is the only admissible eligibility defect. Missing baseline evidence is not treated as zero performance. Compare explicit case, repeat, fault, and refactor manifests. Ties are rejected.
5. **Check transfer.** Evaluate incumbent and candidate on the held-out cases. Every held-out fault must preserve or increase assertion credit and preserve or reduce healthy survival. The candidate must pass all eligibility gates; the incumbent must supply the comparable baseline and variant evidence required above. A campaign uses this gate once and then stops, preventing repeated tuning against its results.
6. **Review and keep.** An independent agent reviews both skill versions and both sets of actual development submissions without mutation scores. It checks contract evidence, independent expectations, dependency boundaries, deterministic scheduling, scope, and maintenance cost. It must reject gains caused only by score accounting, such as wrapping an already detected exception into an assertion. Acceptance requires valid structured approval with specific evidence, no material concerns, and unchanged reviewer input files. The runner then writes an experiment-local `accepted-skill/` snapshot.

Rejected proposals leave the incumbent intact. The runner never replaces the source or installed skill. Before promoting an accepted snapshot, verify that `campaign.json` says `completed`, inspect its hypothesis and evidence, and validate the resulting skill package. A budget exhaustion, timeout, or agent failure leaves an incomplete campaign and its available evidence; it is not a successful comparison. Subsequent campaigns should address a documented weakness with fresh evidence, rather than repeat until a favorable random result appears.

Suite version 9 in [suite.json](suite.json) defines nine development cases: transactional outbox persistence and notification delivery; asynchronous search ownership, cancellation, and recovery; quote boundaries and input handling; the help-centre article reader; streaming import; access-policy decisions; print-spooler scheduling; revision-store snapshots and atomic replacement; and TTL-cache expiry, recency and atomic writes. The designated holdout is `text_edits`. Read case internals when maintaining the evaluator, not while generating a blind submission.

Concrete counterexamples exposed expectations inherited from production defaults and observers that required constructors to stay silent or HTML to include explicit body tags. Dedicated development variants now exercise these weaknesses. Exposed holdouts moved into development before the fresh holdout was obtained.

## Evidence and limits

A campaign records its frozen evaluator, hashes, skill snapshots, exact prompts, proposed hypotheses, decisions, agent call count, resulting event logs, submitted tests, execution logs, and structured results. `partial.json` preserves completed evaluations if a later call fails. `campaign.json` and each `grade.json` are the starting points for an audit; no campaign outcome is asserted by this README.

Eligibility requires nonzero, consistent discovery; no failures, errors, skipped tests, or expected failures on the original; and unchanged test counts with green results on every equivalent refactor. A fault earns credit through at least one assertion failure with unchanged discovery and execution counts, no skips, and no timeout. Additional errors do not erase an observed assertion failure. Errors alone receive no automatic credit: this conservative policy can undercount useful suites whose detected domain fault surfaces solely as an uncaught exception. Feedback distinguishes these uncredited outcomes from faults on which all tests actually stayed green. The comparison gate rejects accounting-only credit gains mechanically and rejects errors becoming healthy survivors, even when assertion credit is unchanged. Independent review also checks for score gaming. Inspect uncredited outcomes rather than teaching agents to catch arbitrary exceptions for a better score.

Generated agents receive only public fixtures and the skill. The evaluator checks canonical input bytes and executes variants in neutral temporary paths so their names do not reveal whether a fault was inserted. Reading restrictions in prompts are behavioral instructions, not an operating-system confidentiality boundary. Generated Python executes locally with the caller's permissions; this harness is intended for trusted evaluation work, not hostile submissions. Its checks are not a security audit.

Repeated generations expose some model variance; they are not a statistical guarantee or proof that the skill caused every good result. Finite faults and refactors cover selected risks. An all-green suite still needs contract and maintenance review, and a saturated benchmark needs new independent scenarios rather than a claim of perfection.

## Transfer

- **Use the skill elsewhere:** copy the entire `skills/khorikov-unit-testing/` directory, preserving its relative `references/` and `agents/` files, into the destination's skill location. The skill has no dependency on this evaluator or Android project.
- **Reproduce the experiments elsewhere:** copy `evals/khorikov/` plus the skill directory. The Python cases need no Android SDK, Gradle, database server, or third-party Python packages; the persistence case uses standard-library SQLite. Adjust command paths to the copied locations.
- **Calibrate another project:** identify its real behavior boundary and consumers, add a valuable regression scenario, run its normal tests, and execute a disposable fault and equivalent refactor. Use that project's types and commands. Preserve contract uncertainties and the exact scope of the evidence.

For source attribution and book-access limits, see the [skill sources](../../skills/khorikov-unit-testing/references/sources.md). Earlier calibration results are historical and are not asserted by this package. The experiment protocol follows the hypothesis/measure/keep-or-discard pattern illustrated by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch); this package supplies its own testing-specific gates. CLI execution uses [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).
