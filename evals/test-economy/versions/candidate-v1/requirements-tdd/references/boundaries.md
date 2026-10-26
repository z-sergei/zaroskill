# Observe the contract at the right boundary

Test quality combines regression protection, refactor resistance, feedback speed and maintenance cost. A higher count or coverage percentage is not a substitute for a discriminating assertion.

| Boundary | Test choice and limit |
| --- | --- |
| Pure decision or deterministic in-process collaboration | Exercise real objects with explicit inputs and independent expected outputs. A unit of behavior can span classes. |
| Controlled input: time, random values, identifiers, remote reads | Supply a controlled clock/value/stub. Assert the resulting decision. Verify read counts only when the count is explicitly contractual. |
| Persistence managed by this application | Use isolated real persistence for mapping, constraints, transactions and reload semantics. Observe relevant state through a fresh read; choose a supported application query or a direct persisted-state observation appropriate to the integration boundary. An ORM cache or mocked save cannot prove durable storage. |
| Unmanaged effect visible to another system | Replace the external endpoint at the application's adapter and assert the promised payload and meaningful multiplicity or order. Exercise the real adapter against a suitable test endpoint when protocol fidelity matters. |
| Functional core returning a command | Assert the command value as the shell's input contract. Cover execution separately where the requirement includes the effect. |

Dependency categories depend on the selected system boundary and independent observability, not the class name or who owns a server. A stub supplies input; a mock or spy observes output. Preserve important integration gaps explicitly when the real dependency is unavailable.

A supplied completion proves response handling only. If the scenario claims the whole operation, observe the required request or command before supplying its result. A focused response-handler test may inject the result directly when its limited scope is explicit. Verify contractual initiation rather than incidental reads or helper traffic.

For stateful behavior, choose sequences that distinguish the contract: rejection leaves the specified state intact, recovery uses the same instance when supported, and earlier results remain stable when snapshots are promised. Assert these checkpoints before recovery or later actions can hide a failure, including required effects and their absence when promised. Use independently distinguishable identifiers and inputs when order or identity matters.

For asynchronous behavior, control completion with the framework's scheduler, events or deferred results. Observe promised state and effects at the relevant checkpoints; arbitrary sleeps are weak evidence. Where ownership can change during work, include the overlap and stale-result case justified by the requirement. A double must honor the real port's calling, cancellation and error protocol across supported implementations.

When observing rendered or serialized output, assert the consumer's meaning and contractual fields. Use an appropriate parser when optional formatting would make string matching brittle. Exact bytes belong in assertions only when byte representation is itself required.
