# Temporal checks

Read the sections relevant to the selected property. These are candidate contracts to derive from requirements, not rules every product must adopt.

## Identity and stale results

Choose the smallest identity that separates work whose results are not interchangeable: account, workflow, inquiry, attempt, request version or resource run. Trace it from dispatch to acceptance. Stamping a callback with the current identity after receipt does not establish which operation produced it.

The usual freshness rule is: acceptance of a result requires its operation to still be authoritative for that result. An old response can remain useful for a cache or reconciliation, so distinguish applying it to current UI state from recording it elsewhere. A documented single-flight SDK contract may establish correlation without an extra field; verify the lifecycle behavior on which that claim depends.

Useful traces include A then B then result A; cancellation followed by a queued result; and recreation followed by an old activity result. First verify which of these can occur through real producers. Cancellation, subscription removal, saved state and SDK guarantees can rule a trace out.

## Terminal states and effects

Define terminal per operation. A legitimate restart may create a new operation. After completion, old events may require resource cleanup even though they cannot change the terminal business outcome.

Separate four promises: **command emitted**, **executor invoked**, **consumer handled**, **remote effect committed**. At-most-once emission does not imply delivery; a client cannot establish exactly-once banking effects without a server-side identity/deduplication and recovery contract. A lost response leaves the outcome unknown until reconciliation resolves it. State whether retry repeats the same logical operation or starts a new authorized one.

To check at-most-once behavior over a trace, track the relevant effect count per operation in a monitor. Include that monitor in exploration equivalence. Do not infer the count from a single final state or only the last update.

## Resource ownership

A useful local law is that each owned or acquired resource ends in exactly one allowed place: retained, released, or transferred. Decide whether identity or value equality represents ownership. Account for duplicate callback aliases, late payloads, transfer of responsibility and retry.

The reducer can establish that it requests release or transfer. The executor/adapter must separately establish that the request reaches the resource owner. An asynchronous command list's order alone does not establish completion order. Inspect execution before claiming that disposal finishes before the next launch.

## Progress and retries

State both a progress goal and assumptions about participants: eventual response, scheduling of an enabled retry, bounded consecutive failures, bounded total budget, or a finite number of phase resets. Use only assumptions the system can support. A finite budget per response does not bound the whole workflow if new responses can keep enlarging it or resetting the phase.

For a decreasing counter argument, show it cannot be replenished indefinitely by other steps and that a step consuming it cannot be postponed forever. A disabled button, time advanced in one test, or no detected deadlock does not establish liveness. A deadline additionally needs time and delay assumptions.

Finite trace exploration finds finite violations and checks bounded response requirements. It does not establish eventual progress over arbitrary executions. Full finite-state temporal checking can analyze cycles under stated fairness; explain those assumptions instead of adding fairness merely to obtain a passing result.

## Abstraction and exploration

Separate the production state from the verification state. The latter may be `(production, pending work, queued results, property monitor)`. Avoid exposing test monitors to production unless the product itself needs that state.

For each reduction in the state space, explain why merged cases cannot differ for the property. Two symbolic operation identities may expose a stale-result race; they do not automatically cover an arbitrary number of outstanding operations. Event names should expose relevant identity and outcome in a counterexample. Report whether the queue was exhausted or a bound truncated exploration.

Use TLA+/PlusCal when the design question crosses multiple owners or durable boundaries and the model can omit substantial code detail. Specify permitted initial states, atomic actions, properties, environment assumptions and a finite configuration first. Model the uncertain interleavings instead of assuming an entire request/response round trip is atomic.

After checking the model, map each action and property to code, contracts or a runtime experiment. Identify internal steps that preserve the abstract state and concrete effects that the abstraction observes. Safety correspondence alone does not preserve progress. Keep the model only while it answers a maintained engineering question; simple local reducers usually need no separate formal model.
