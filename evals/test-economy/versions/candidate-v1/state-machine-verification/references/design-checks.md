# Design checks for stateful promises

Select the section that addresses the task's unresolved question. A short argument or scenario is enough when it distinguishes the outcomes; these checks do not require a formal language or a new document.

## Decisions with incomplete observations

Use when a component must decide after an unknown outcome, when provenance was lost, or when its state combines situations requiring different responses.

1. Identify the decision, its required outcome and the actions the component may take. Include waiting, asking, retrieving status or reporting uncertainty when the contract allows them.
2. Construct reachable histories that differ in the relevant fact but give the component the same available information. Include retained memory, operation identity, authoritative replies and documented guarantees. The observation boundary is the deciding component, not everything known to the analyst.
3. For each history, determine which actions satisfy the selected obligation under the modeled outcomes. Find whether an action is allowed in **all** indistinguishable cases; pairwise overlap is insufficient for three or more cases. If no action works even with full knowledge of one case, diagnose that contract or action set separately.
4. If no common action exists, name the missing observation, authority or product choice. Restrict the conclusion to this decision, contract, action set and reachable cases. An allowed new observation may enable a later decision; this local check does not establish impossibility of every future strategy.

Example: an upload request times out. The server may have committed it, discarded it, or still be processing it. A definitive success/failure answer needs additional evidence. A retry may be appropriate if its identity, deduplication and result-retrieval guarantees support the promise. Effect deduplication alone does not establish that the caller knows the final result. A non-final response such as "checking status" is valid when permitted.

**Useful result:** a short pair or set of indistinguishable histories with incompatible required actions, or the concrete shared action/observation that already resolves them. Keep a correct protocol as a control. Phrase the scenario in the user's domain vocabulary.

## Recovery after losing a required resource

Use when access, cancellation, resumption or recovery is promised after losing a device, session, credential, connection or other prerequisite.

Start from the promised failure condition. List the remaining capabilities and the prerequisites of recovery actions, including reachable support, backup credentials and out-of-band channels. Label who controls each action and any availability or identity-verification conditions. A path that requires the lost resource does not satisfy recovery without that resource.

Look for a feasible path to the promised outcome from each relevant failure state. A circular prerequisite, such as authentication required to ask for help restoring the only authentication method, is a candidate defect only after checking the channels actually available. Respect narrower promises such as support during stated hours; a hypothetical permanently unavailable helper is not evidence against a contract that assumes that helper's availability.

Separate **some feasible path exists** from **the user can obtain the outcome under the allowed environment behavior**. Progress may need scheduling, eventual delivery or external cooperation. A finite successful path does not prove eventual completion for every execution. A deadline additionally needs time assumptions. When a necessary policy or support contract is unknown, report the question and its effect on the conclusion.

**Useful result:** a reachable failure state and its blocked prerequisites, or a concrete existing recovery path with the conditions on which it depends. This applies to product journeys as well as code; it does not require modeling every screen.

## Compatibility of behavioral contracts

Use when a new version changes cancellation, retry, confirmation, recovery or other externally visible histories while the interface shape may remain the same.

Establish the old supported promise and the intended change from requirements or consumer contracts. Mark observed implementation behavior separately. Compare versions at the same consumer boundary, with corresponding inputs and environment assumptions. Map internal steps to their visible consequences; an extra queue or internal retry is not itself a new business effect.

Find a distinguishing history: a formerly forbidden observation now allowed, a supported input no longer handled as promised, or a required outcome/progress guarantee no longer preserved. Restricting an optional internal choice can still satisfy the old contract. A deliberate product change is not automatically a defect; state the affected promise and whether the change is authorized or unresolved.

Example: an old successful cancellation guarantees that no later notification is delivered. A new success response acknowledges only the cancellation request, allowing delivery afterward. The shared response format does not preserve that promise. If the old contract already allowed an in-flight notification, the same history does not establish a regression.

Use a finite trace for a finite violation. To assess eventual progress, reason about infinite behavior or perform suitable temporal checking under explicit assumptions; a slow finite run alone cannot show failure forever.

**Useful result:** the sourced old/new promise, one decisive history and its consumer observation, or an explanation of why the visible contract is preserved. Turn a supported violation into a regression scenario through the real boundary when implementation is in scope.
