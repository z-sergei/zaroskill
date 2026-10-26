# From a user scenario to a general rule

Start with the user's action and observable outcome. Keep the example that makes the promise understandable, then state the rule that should also hold for other permitted inputs or histories. For example, starting a new search before an earlier response arrives illustrates: results from an obsolete search cannot replace the active results. Derive that rule from the product contract, not a copy of the implementation.

Define the relevant inputs, reachable starting conditions, observations and exceptions in existing task notes or tests. Use a generated property test or bounded event exploration when variation creates a meaningful risk that a few examples leave open. A simple transformation can stay with ordinary examples. Formal notation and a separate model earn their cost only for a specific unresolved question.

## Observe the user's outcome

A rule may span several components. Trace the action through the real coordinating code to the promised observation: returned response, rendered state, persisted result or external request. Add the cheapest missing integration, API or UI check when wiring matters. A reducer's command proves its decision; delivery and durable completion need their own evidence if the promise includes them. Existing coverage can establish those obligations without duplicating the whole journey at every level.

## Make the property meaningful

Keep a valid successful example when useful work is promised. A service that rejects everything satisfies many prohibitions while failing its purpose. For conditional properties, supply an input or event history that reaches the condition and the assertion. Generated case counts alone cannot show this; use an explicit witness or relevant branch observation when reachability is uncertain. Check the actual test mode if assertions, feature flags or exception handlers can disable or hide the failure.

When sensitivity is uncertain, introduce a specific behavioral violation in a disposable copy and run the unchanged property. Changing the assertion itself checks the failure mechanism, not whether the test detects an implementation regression. Preserve the promised outcome through red–green; revise an invalid expectation only from an independent contract reason. Equivalent or unreachable mutations establish no missing protection.

## Scope progress and evidence

A server or listener may run indefinitely. Require progress for the operation that owes an outcome, under explicit assumptions such as a response arriving or a timeout firing. Waiting for a user need not terminate. Eventual completion and completion within a deadline are different promises.

Preserve a generated counterexample as a readable regression scenario. Report whether examples ran, a stated finite domain was explored, or a named formal property was proved with assumptions. An unfinished proof may reflect a tool limit or missing reasoning; it is not by itself a defect in the product.
