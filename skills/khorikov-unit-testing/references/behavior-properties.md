# Valuable properties and user scenarios

A property states a contractual rule across permitted inputs or histories; an example shows what that rule means to a user or caller. Retain both when the general rule adds protection. Examples include rejected changes preserving saved data, old responses leaving the active search intact, and encoding followed by decoding preserving a value. Establish each rule's domain and exceptions independently of the implementation. Agreement between two mutually wrong functions does not establish their external format contract.

Choose the smallest useful variation: a few distinguishing values, generated data or controlled event sequences. Follow a user action through real coordinating code where the promise crosses boundaries. Returned commands, actual requests and completed external effects are distinct observations. Add integration or UI evidence for the missing obligation; a user scenario does not automatically require a full end-to-end test.

For a stateful boundary, use callers to identify which operations run in each relevant phase. A query or mapping step may run after every update, including while work is pending or after a failure. Exercise that obligation where its result is consumed; checking only the transition that enables work can miss a broken observation in another phase. An outcome checked after refresh or recovery does not necessarily protect the first attempt. Choose a different starting state or checkpoint when it distinguishes a plausible failure, preserving existing scenarios without enumerating the full state-by-operation product.

For a conditional or generated check, establish a witness that reaches the relevant assertion when that is uncertain. Test discovery, high case counts or visiting a broad phase can coexist with an assertion that never runs. Inspect the exercised configuration when compilation, flags or exception handling may remove or suppress it. Such a concern needs a concrete path, not a mandatory instrumentation framework.

Keep a useful successful case for promises of useful work: rejecting every request can satisfy an at-most-once rule. Fault probes must produce an observable violation on permitted inputs while leaving the tested assertions intact. A still-green equivalent change or a path ruled out by a real upstream guard is not a coverage defect. Pair claims of sensitivity with the actual outcome; inability to find a mutant is inconclusive.

Scope progress to the operation that owes a result. A long-running service can be correct, while one accepted request may require completion under stated environment assumptions. Do not invent a timeout for an interaction allowed to wait for a person.

Report the level exercised and its limits. A bounded event search or generated sample is evidence for its stated domain; it does not prove arbitrary histories. Keep a readable regression for a discovered counterexample and preserve behavior-equivalent refactors.
