---
name: state-machine-verification
description: "Specify and verify temporal contracts of stateful workflows. Use when correctness depends on event order, retries, cancellation, ownership, recovery, incomplete observations or changes to a behavioral contract; choose focused traces, bounded exploration or a formal model."
---

# Verify behavior across time

Turn a workflow's promised behavior into explicit properties, then find the smallest evidence that can distinguish a correct implementation from a plausible failure. Apply this to the requested scope: analysis ends with findings and a verification plan; implementation includes the authorized changes and checks. A small change may need one property and one trace, without a new document or model.

## 1. Choose the property and its boundary

Read the repository instructions, relevant requirements, producer/caller code and nearby tests. Establish what decides correctness independently of the current implementation. Label each claim as **required**, **observed behavior**, or **proposed guarantee**. A product ambiguity is not a confirmed implementation defect.

Write a compact contract card in existing task notes or a relevant test. For a narrow review, three or four sentences covering the decision-relevant fields suffice; the table is optional:

| Field | What to capture |
| --- | --- |
| Promise and source | Observable outcome and the requirement, consumer contract or explicit assumption supporting it |
| Boundary | Reducer, controller, SDK adapter, persistence or server; actors included and excluded |
| State and ownership | Relevant phase, active operation identity, pending work, retained resources and committed effects |
| Safety | What no permitted transition or finite trace may do |
| Progress | What must eventually happen, under which environment assumptions; omit if irrelevant |
| Distinguishing trace | Reachable start, competing event order and the observation that separates correct from wrong |
| Evidence | Existing check, actual result, uncovered boundary or proposed experiment |

Use project-local instructions and code to locate the existing transition owners, explorers and test policy. For choosing a temporal property or deciding whether TLA+ adds value, read [temporal checks](references/temporal-checks.md).

Read the relevant section of [design checks](references/design-checks.md) when a decision depends on incomplete observations, a promised recovery path loses a resource, or a change may alter an existing behavioral contract. These checks can reveal a missing requirement or mechanism before implementation; run only the branch that answers an open question.

**Ready:** the claim has a source, an observable consequence and a boundary. The reducer's current branches are evidence about behavior, not the specification of correctness.

Keep a concrete user or caller scenario alongside a general property so its meaning remains reviewable. If useful work is promised, include that positive obligation: refusing every action may satisfy the prohibition while violating the product contract. Select progress obligations per operation; a service or user-driven interaction can legitimately remain active.

## 2. Connect the abstract steps to real events

Trace a consequential path through **input → state transition → command → execution → callback/result → consumer**. Include effects that bypass the reducer. Locate the owner of pending work, the point where an identity is stamped, and the check that rejects an obsolete result. Distinguish an identifier for the user/session from one for a particular attempt.

Check actual serialization and lifecycle assumptions. A pure reducer does not establish that concurrent calls to its host are serialized. A cancellation request does not by itself establish that a queued callback or remote side effect cannot arrive. Conversely, a callback may already be rejected by its producer or owner before reaching the reducer. Preserve that distinction.

Construct short competing traces using real entry points, for example start A, start B, receive A; submit, leave, receive success; or finish, receive the same result again. For each event, identify the producer and why it remains able to deliver at that point. Supported operations or invariant-respecting fixtures establish reachable starts. Deliberately invalid input can test a defensive contract, but constructor access alone does not make it a production counterexample.

Inspect all transition observations relevant to the property: new state, feature commands, shared commands, navigation, resource disposal and external calls. A stale result may correctly leave business state unchanged while releasing its resource. A final state alone cannot establish that an earlier forbidden effect was never emitted.

**Ready:** a suspected defect has a feasible trace or is explicitly a hypothesis with the missing feasibility check. An existing guard can be the correct conclusion.

## 3. Select the smallest useful verification

| Risk | Useful evidence |
| --- | --- |
| A local transition or a short known race | Scenario through the real reducer, with observations after each relevant step |
| Several event orders and retries share a small state space | Bounded exploration of the real reducer with independent laws and a finite event domain |
| Correlation, cancellation, scheduling, lifecycle or effect delivery | Controlled producer/controller or adapter scenario through the actual boundary |
| Several participants, durable state and failures interact beyond a manageable code test | Small TLA+/PlusCal model with stated abstraction and a mapping back to code |

Combine levels only where they establish different obligations. Keep existing test infrastructure and conventions. When implementing, derive expectations from the contract, observe the relevant failure when feasible, make the cohesive change, then run the narrow affected checks within repository permissions. Hand the sourced promise, reachable trace, independent expected observations and remaining assumptions to the relevant workflow: `requirements-tdd` for test-first implementation, `khorikov-unit-testing` for the test boundary, or `test-quality-review` for an audit, when available. Otherwise use the repository's existing workflow. Preserve the requested scope and use one leading process.

For exploration, record initial states, event/data domain, depth or other bounds, assumptions and completion status. Start with a small domain that distinguishes identities and outcomes; increase it for a concrete risk. Check initial invariants and laws on every explored transition, including commands even when state is unchanged. Retain a replayable failure trace.

Deduplication must preserve everything needed for future transitions **and the property**. If a property depends on history, include a monitor such as delivered-count or consumed-resource identities in the explored state and its key. If pending requests and queued callbacks affect possible next events, include the relevant environment state too. Equal UI/reducer states alone do not justify merging those executions. A copied reducer used as the oracle gives weak independent evidence.

**Ready:** each check can expose a specific wrong outcome; its abstraction and bounds are explicit. Depth-limited traces are not an unbounded proof or a liveness check. See [temporal checks](references/temporal-checks.md) for progress, monitor state and effect semantics.

For generated or conditional checks, use the [property execution checks](references/temporal-checks.md#property-execution) when the condition, build mode or failure handling could make the result empty. A successful verifier establishes its stated property; validate the property's meaning and its correspondence to the user's observation separately.

## 4. Make the result useful for the change

For implementation, let the property guide the smallest cohesive repair: an explicit phase, an operation identity at the correct boundary, idempotent handling, a resource owner or a progress condition when needed. Do not add every mechanism to every flow. Keep the check tied to the promised behavior so equivalent refactors remain possible. Rerun checks justified by the final change; distinguish existing failures from new ones.

Report the property and its source, the decisive trace, the relevant code boundary, evidence and the next necessary action. Use calibrated labels: **inspected**, **scenario reproduced**, **bounded exploration completed** with configuration, **formal property proved** with assumptions, or **not executed**. Report tests present in source separately from tests actually run. A model's result does not establish that the code refines it; identify the correspondence checks still needed.

For an analysis-only request, a sourced feasible trace and a precise unexecuted experiment can be a complete result when execution is unavailable or unnecessary. Keep the report proportional to the question; do not repeat the entire contract card and workflow in the answer.

**Done:** requested work is complete, every material conclusion has a trace or argument and accurately scoped evidence, and proposed guarantees or unresolved assumptions remain visible. Confidence comes from these obligations, not a count of passing tests or a universal reliability score.

The workflow is an engineering synthesis of Lamport's specification, invariants, behaviors and refinement ideas. For attribution, read [sources](references/sources.md).
