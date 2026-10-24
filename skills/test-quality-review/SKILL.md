---
name: test-quality-review
description: Review the quality of existing tests or a test diff. Use to assess regression protection, refactor resistance, reliability, maintenance cost, meaningful coverage gaps, or test doubles; produce evidence-based findings and prioritized improvements.
---

# Review the confidence tests provide

Assess whether the tests make changing the product safer at a reasonable cost. Default to a review: inspect code, run relevant local checks when useful, and keep production code and tests unchanged. Use disposable copies for probes. Implement fixes only when the user requests them. The skill is self-contained and works with the repository's existing language and runner.

## 1. Establish the scope and contract

Read the requested tests, the behavior they exercise, relevant callers, requirements and repository instructions. Discover the normal test entry point. For a diff, compare the old and new behavioral evidence when the base is available; identify both gains and lost distinctions. For a large suite, record which areas you examined and which remain outside the review. Honor an explicitly exhaustive scope.

Map important outcomes to their assertions: **requirement/source → trigger and inputs → expected observation → test evidence or gap**. A compact note is enough. Derive correctness from supported requirements and consumers, not only from the implementation being tested. Label legacy characterization and unresolved product assumptions separately. Search nearby suites before claiming a behavior is untested across the system; a local gap may be covered at another level.

Check whether the intended tests are discovered and executed, whether the original implementation passes, and whether skips, expected failures or setup failures limit that result. Run the narrowest useful check after inspecting its effects and prerequisites. If execution is unavailable or unnecessary for a static finding, say so; unknown execution evidence is not proof of poor test quality.

**Ready:** the scope, behavior boundary, source of expected results, coverage map and available execution evidence are explicit.

## 2. Assess four dimensions

| Dimension | Questions that determine value |
| --- | --- |
| Regression protection | Which plausible wrong result would fail a relevant assertion? Does the test execute the real decision? Are expected values independent? Do inputs distinguish the contractual alternatives? |
| Refactor resistance | Would a change that preserves the consumer's contract keep the test green? Are assertions on incidental helpers, private structure or formatting that the consumer does not require? |
| Feedback and reliability | Are time, scheduling, randomness, shared state and cleanup controlled? Does the chosen level give timely feedback? Separate measured execution time from setup/build cost and unmeasured CI behavior. |
| Maintainability | Do the name and scenario clearly describe one useful behavior in domain terms? Are important inputs and expected outcomes visible? Do fixtures and doubles earn their cost? Would changing a requirement require scattered unrelated edits? |

Use **strong / mixed / weak / unknown** per dimension with a short reason. Base strength on the reviewed evidence, not a guarantee. Report dimensions separately; a severe behavioral blind spot cannot be averaged away by speed or tidy style. Coverage and test counts locate questions, not certify quality. Follow a user-provided scoring rubric when present and state what remains unmeasured.

Compare each reviewed test's name with what its assertions establish. A useful name states an observable result and any distinguishing condition in user, business or caller vocabulary; technical library concepts are a domain too. Preserve coherent scenarios with several actions and assertions. Judge clarity within repository conventions, without requiring a template, DSL, actor or word limit. Separate an overclaim needing a narrower name from a requirement needing stronger tests: renaming alone cannot close a behavioral gap.

Read [boundaries-and-traps.md](references/boundaries-and-traps.md) when mocks, persistence, external effects, state transitions, asynchronous work or structured output affect the assessment. Several assertions, a real database observation or an interaction check may be exactly right for the selected contract.

For each suspected gap, identify a concrete valid scenario and the required observable difference. Consider boundaries, rejection-state preservation, recovery and reuse when the contract makes them meaningful. Assess distinct risks; avoid demanding every imaginable input combination. Judge duplicate tests by the discrimination and diagnosis they add, not textual similarity alone.

Read [property evidence](references/property-evidence.md) when tests claim a rule across generated inputs or event histories, use conditional assertions, or claim a user outcome from a narrower boundary. Assess the rule's meaning, whether its check runs, and which violation it detects. Absence of property-based tooling is not itself a finding.

**Ready:** each weakness is tied to a missing discriminator, a plausible false failure, unstable execution or a concrete maintenance burden. Style preferences and speculative extra partitions remain suggestions, not defects.

## 3. Substantiate material findings

A finding needs a test location, a contract source, a concrete counterexample or refactor, its consequence and the smallest useful correction. Check plausible alternative explanations before assigning severity: the behavior may be covered elsewhere, the alleged refactor may change the contract, or a double may intentionally observe an external promise.

Use [probes.md](references/probes.md) for a disputed or high-impact claim that a test misses a fault or rejects an equivalent implementation. Execute a focused probe when it would materially change the conclusion. A clear code-based finding can stand without an expensive campaign; identify its evidence accurately.

Classify evidence as **executed**, **demonstrated by code**, or **hypothesis requiring confirmation**. Tie severity to the supported consequence: high for a consequential regression or seriously misleading protection, medium for a material gap or recurring false failure, low for a concrete local maintenance improvement. Explain the impact; the label alone is insufficient. An uncertain claim does not become a confirmed defect through a severity label.

If the normal suite fails, distinguish a production defect, obsolete expectation, invalid double and environment failure before judging the tests. A legitimate exception on a valid path can expose a regression; failure classification alone is not a quality score. Final code cannot establish whether tests were written first: assess TDD order only when execution history is available.

**Ready:** material findings have evidence and an actionable correction; unresolved hypotheses are separated from confirmed findings. No-findings is a valid outcome.

## 4. Deliver an actionable review

Scale the report to the task. Include:

- **Verdict and scope:** sound within the reviewed scope, useful with material gaps, misleading evidence, or inconclusive. Explain the main reason and notable strengths worth retaining.
- **Four dimensions:** the assessments above, each grounded in evidence; mark unavailable evidence unknown.
- **Prioritized findings:** location, contract, concrete problem, consequence, minimal correction and evidence level. Group instances of the same cause rather than inflating the count.
- **Best next step:** the most valuable test or repair, with its distinguishing input and expected observation. Preserve useful existing coverage. Recommend retaining tests when that is the right result.
- **Checks and limits:** actual commands/results, probe outcomes, unreviewed areas and integration gaps. Distinguish completed checks from proposed work.

If no material defect is found, say so and describe the bounded evidence; inventing a quota of issues reduces review quality. Stop when the scoped assessment is supported. Review completion does not mean gaps are fixed or authorize commits, merges or deployment.

**Done:** the user can identify what protection exists, which conclusions are proven, what remains uncertain and which improvement is worth making first.

For attribution and deliberate adaptations, read [sources.md](references/sources.md).
