---
name: khorikov-unit-testing
description: Design or review valuable automated tests using Khorikov’s principles. Use when adding regression tests, reducing brittle tests, choosing unit versus integration coverage, or deciding what to mock.
---

# Valuable tests

Optimize for confidence in changing behavior. A useful test catches a plausible regression, survives a behavior-preserving refactor, gives timely feedback, and costs little to understand and maintain. These four pillars guide tradeoffs; coverage and test counts are diagnostics, not goals.

This is an operational adaptation of Vladimir Khorikov’s work, not the book text. Read [sources.md](references/sources.md) when explaining the rationale or checking attribution.

## Establish the contract

Identify the requested change and the smallest meaningful behavior boundary. Read its production callers and existing tests. Discover the runner and dependency versions from the repository.

Write a compact **contract**: input or trigger → externally observable outcome; cite the requirement, caller, or established test that supports it. Public methods can expose implementation details; the boundary may span several collaborating classes. Return values, relevant state, and promised external effects are possible observations.

For legacy behavior, distinguish a supported requirement from a characterization of what the code currently does. Flag ambiguous behavior instead of turning a suspicion into a permanent expected value. Carry characterization status into the test name or a nearby comment, including the unresolved assumption; a separate report will not accompany every future test failure.

**Done:** the behavior, its consumer, the evidence for the expected outcome, and the runnable test entry point (or precise blocker) are identified.

## Choose the seam

Choose the cheapest test that exercises the real decision and can detect the named regression. Use real, deterministic in-process collaborators. A unit is a behavior, not necessarily one class; isolate tests from each other rather than automatically isolating every class.

Prefer output assertions for pure logic, then state assertions for stateful behavior. Use interaction assertions when the interaction itself is an observable contract. Read [boundaries.md](references/boundaries.md) whenever choosing test doubles, testing persistence or a remote service, or deciding whether an emitted command is an internal detail.

When important logic is buried in I/O, consider a small extraction into a functional core or a humble-object design: the shell coordinates effects and the core makes decisions. Apply it only when it simplifies this task; preserve a test through the real orchestration boundary where wiring matters. Simple glue and trivial accessors rarely repay isolated tests.

**Done:** each proposed test names a regression, an observation, and its level; each double has a reason tied to a dependency boundary. Review requests can stop at an actionable recommendation without editing code.

## Make the test earn its cost

Select distinct input or history partitions from the contract: ordinary success, relevant rejection, and meaningful boundaries or recovery. Choose representatives and boundary cases for the risks they distinguish; sharing a branch does not prove equivalence. Combine dimensions when their interaction matters, rather than taking an automatic Cartesian product.

Before adding a case, identify its contribution beyond existing tests: a missing distinction, a different integration obligation, faster feedback or useful fault diagnosis. Reuse adequate existing evidence. Similar examples and overlapping mutation kills can still serve different obligations; parameterization reduces repeated code but does not justify unnecessary cases. When pruning is requested, preserve those contributions and historical regressions, and remove a case only when its useful evidence remains represented.

Arrange explicit, deterministic inputs. Start from a reachable state, using supported operations or a direct fixture that respects the workflow's invariants. An intentionally invalid state needs a specified defensive contract and an explicit purpose. A convenient constructor alone does not justify a scenario.

Express one coherent user, business or caller scenario; several actions and assertions may be needed to establish its rule. Assert contractual checkpoints before later actions can hide a failure, including required effects and their absence when promised. Derive expected examples independently of the algorithm under test. Helpers may construct inputs; keep the important values visible at the test site. Parameterize cases that express the same rule.

For rules covering many inputs or event sequences, read [behavior properties](references/behavior-properties.md). Connect the understandable example to the general rule, then choose variation and observation boundaries that add protection. Generated tests and formal models are optional techniques, selected for the risk.

For tests you add or revise, make the name a concise claim about the observed behavior, including a condition when it distinguishes the scenario. Use the domain's vocabulary; technical library concepts are a domain too. Match the claim to the assertions' actual boundary: requesting an effect or exposing a link does not prove delivery. Follow repository naming conventions without imposing a template, DSL, actor or word limit.

Test private logic through its consumer. If complex logic lacks a usable boundary, extract a cohesive abstraction rather than exposing internals solely for tests. Keep clocks, randomness, scheduling, shared state, and cleanup under test control where they affect the result.

For every changed test ask:
- **Protection:** which believable wrong result would fail it?
- **Refactoring:** which internal change should leave it green without test edits?
- **Feedback:** is a cheaper level equally convincing?
- **Maintenance:** does each fixture, double, and assertion contribute to this behavior?

**Done:** the in-scope outcomes and selected risks have discriminating evidence or explicit gaps; each added or revised test earns its place and describes its actual observation. Stop adding examples when no uncovered distinction or useful diagnostic benefit justifies their cost. Fewest test methods or lines is not the objective.

## Verify the evidence

Run the narrowest relevant tests. For an added regression test, observe failure on the known bug before its fix when feasible. Reuse that relevant sensitivity evidence. For a material quality claim still in doubt, use a targeted fault probe in a disposable copy: alter a relevant decision, run the unchanged test, and inspect the failure. A build error, missing dependency, or zero discovered tests is not a detected regression. For automated mutation tooling or a broader campaign, read [mutation campaigns](references/mutation-campaigns.md).

When refactor resistance is in doubt, perform one small behavior-preserving transformation in a disposable copy and run the same tests unchanged. A thought experiment is useful review evidence; label it as such rather than as an executed check.

Restore every probe and rerun the relevant unchanged source. Run broader repository checks when the actual change or instructions require them. If the normal runner is blocked, report where it stopped. An isolated harness can provide narrower evidence when it compiles the real production code with real relevant dependencies; explain precisely what it excludes.

**Done:** report the changed behaviors, actual commands and results, any observed red/green evidence, and remaining limits. Stop after relevant checks pass unless a new change or unresolved failure justifies another run.
