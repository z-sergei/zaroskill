---
name: requirements-tdd
description: "TDD from requirements. Use when implementing a feature, acceptance criteria, or a bug fix test-first: derive observable examples, verify a failing test, then implement and refactor one behavior at a time."
---

# Requirements to working behavior

Turn the requested outcomes into executable evidence. Plan the behavior examples first; implement them in vertical slices: **one behavior → observed red → green → refactor**. Continue through the agreed scope without routine approval pauses. A request for a test plan or tests only ends at that requested boundary.

## 1. Translate the requirements

Read repository instructions, the relevant callers and tests, and the configured test commands. Use the project's domain vocabulary. Run the narrow existing suite to establish a baseline before changing behavior; distinguish existing failures from this task's failures.

Make a compact behavior list. For each requirement record:

| Requirement | Given / When | Expected observation | Evidence / status |
| --- | --- | --- | --- |
| A user or caller outcome | Concrete input, state and trigger | Literal result, relevant state or promised external effect | Requirement source; test name or pending |

One sentence is enough for a small change. For larger work, keep this list in the task's existing plan or notes rather than creating another document by default. Cover each requested outcome with a test, existing evidence, or an explicit gap. Choose representatives of contractual input or history partitions, relevant boundaries and interactions; avoid an automatic Cartesian product. For each new example, identify the missing distinction or useful feedback it adds beyond existing tests. Already sufficient coverage can require no new test.

When a new mode, shortcut or early return changes control flow, consider whether it can bypass an existing precondition or promised effect. Choose a representative for each materially different bypass risk; an ordinary-path rejection alone does not check the new path.

When a promise covers many inputs or event orders, connect a concrete business scenario to the general rule it illustrates. Read [behavior properties](references/behavior-properties.md) when generating cases, checking a workflow-wide rule, or deciding whether evidence from a component establishes the user's outcome. A local rule may need only its ordinary examples.

Derive expected values from requirements or independently worked examples. Production code tells you where to exercise a behavior; it does not decide what the correct answer should be. Distinguish an explicit requirement from observed legacy behavior. Resolve ordinary technical choices from the repository. Ask only when an unresolved product decision would change the expected outcome, and continue independent work meanwhile.

**Ready:** the examples state observable outcomes, their source and the test entry point. Ambiguous examples remain marked unresolved rather than silently acquiring invented rules.

## 2. Choose a behavior boundary

Use the smallest stable boundary that exercises the real decision through its consumer. It may include several collaborating objects. Prefer returned values and observable state; verify interactions when the interaction itself is promised. Keep real deterministic collaborators inside the boundary.

When persistence, external effects, asynchronous work or test doubles affect the evidence, read [boundaries.md](references/boundaries.md). For a bug fix, existing implementation, unavailable runner or an unexpectedly green new test, read [existing-code.md](references/existing-code.md).

State what the selected test proves and what needs a broader integration check. Choose the seam from callers and conventions within the authorized task; routine seam selection does not require user confirmation. Avoid changing architecture solely to make mocking convenient.

**Ready:** each next example names the wrong behavior it must detect and the observation that distinguishes it.

## 3. Red: prove the next missing behavior

Select one unresolved behavior, preferably the smallest useful path through the feature. Write its test before changing the relevant production behavior. Use the project's test framework and explicit expected values. Express a coherent user, business or caller scenario; several actions and assertions may establish one rule. Parameterized examples may exercise the same rule.

Name each added or revised test with a concise claim about its observable result, including a condition when needed to distinguish the scenario. Use domain vocabulary and repository naming conventions; technical library concepts need no invented user role. Keep the claim within the assertions' boundary: a requested effect is not proven delivery. Choose a natural name without a required template, DSL or word limit.

Start from a reachable workflow state, established through supported operations or a direct fixture that respects its invariants. Intentionally invalid states belong to specified defensive contracts and need that purpose stated. Constructor access alone does not make a scenario valid.

Run the new test and inspect the failure. Establish that it reaches the intended boundary and fails because the requirement is unmet. Broken imports, invalid fixtures, unrelated exceptions, an unavailable dependency or zero discovered tests are setup problems, not behavioral red. If an API is absent, add only the declaration or inert scaffold needed to execute the assertion, then rerun before implementing its behavior. A missing-implementation exception can establish red when it is the precise missing behavior on a valid path; identify it accurately.

Record a concise red observation with the actual command and failure. Keep the test's expected outcome intact while implementing the slice. Correct a demonstrably invalid test from its requirement and rerun it; weakening an assertion to match the implementation changes the specification.

**Gate:** a valid test has run and exposed this missing behavior. An already passing example counts as existing evidence, not a new red–green cycle. The implementation step follows this gate.

## 4. Green: satisfy that behavior

Make the smallest cohesive production change that satisfies the example and preserves supported existing behavior. Minimal means bounded scope, not hard-coded answers for the test's literal inputs. Implement the actual rule without anticipating unrelated features.

Rerun the same test, then the affected existing tests. Inspect failures before editing tests. Preserve valuable existing scenarios, public compatibility and rejection-state guarantees; changing tests is justified only by an explicit requirement change or a demonstrated test defect.

**Gate:** the new test and affected regressions pass, or a separately identified pre-existing failure remains unchanged. Report such failures; they are not an all-green suite.

## 5. Refactor on green, then repeat

With the behavior protected, simplify duplication, names or structure where it improves this change. Keep the public contract and test expectations stable. Parameterization can simplify repeated examples; retain distinct risks, historical regressions and useful integration or diagnostic evidence. Similar code or identical mutation kills alone do not establish redundant tests. Rerun the affected tests after each meaningful refactor. A small slice may need no refactor.

Update the behavior list with its test and evidence, then take the next example through red and green. Plan all requirements up front, but let each completed slice inform the next executable test. Keep changes to a shared implementation sequential; delegate independent investigations or disjoint slices when useful.

**Gate:** this slice is still green and its requirement has an evidence link. Continue until every in-scope outcome is accounted for.

## 6. Verify completion

Run the broader checks justified by the touched integration boundary and repository instructions. Inspect the final diff for unrelated changes, accidental test weakening and test-only access to private internals. Read each added or revised test's name against its scenario and assertions; correct any claim they do not establish. An effect recorded by a double proves the request at that boundary; it does not prove remote delivery or persistence.

For an uncertain assertion, use a targeted disposable fault probe to check that the test detects the competing result. Reuse relevant observed red evidence; every slice does not need another fault. Use a behavior-preserving refactor probe when resistance to refactoring is uncertain. Keep probes in disposable copies and verify that the working implementation is unchanged before final checks. For an automated campaign or mutation results, read [mutation campaigns](references/mutation-campaigns.md).

Report the requirement-to-test mapping, actual red and green evidence, relevant final checks and remaining gaps. Distinguish executed checks from reasoning. Preserve useful work if a check is blocked; describe the precise limitation rather than calling an unexecuted cycle TDD-complete. Tests passing does not authorize a commit, merge or deployment.

**Done:** every requested outcome is supported by evidence or explicitly marked unresolved/blocked, the authorized implementation is complete where those outcomes are resolved, and verification claims match actual runs. Stop adding cases when no uncovered in-scope risk or useful diagnostic benefit justifies another; minimize upkeep while preserving protection, not test count alone.

For provenance or differences from upstream approaches, read [sources.md](references/sources.md).
