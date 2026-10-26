# Dependencies and observations

Define the system boundary before classifying dependencies. Ownership of a server or a class name such as Repository does not determine its category. Ask who can observe its state or effects independently of this application.

| Dependency or output | Useful test strategy | What the evidence means |
| --- | --- | --- |
| Deterministic in-process collaborator | Use the real object with fresh test state | Collaboration inside a behavior can remain a unit test |
| Controlled input such as time, generated IDs, remote reads | Supply deterministic input or a stub at the appropriate port | Assert the decision made from that input; query call counts usually expose mechanics |
| Managed persistence: state only observable through this application | Exercise real persistence in integration tests with isolated data and cleanup | Assert relevant persisted state through a fresh read; mocked saves cannot prove mappings, constraints, or transactions |
| Unmanaged external effect: another system or recipient observes it | Replace the external endpoint at the owned adapter boundary; assert the promised message or request | Check contract fields and meaningful multiplicity; order matters only when promised |
| Declared output from a functional core, such as a command value | Assert it when the shell consumes it as the core’s contract | This proves the core decision, not delivery, serialization, or external completion |
| Internal plumbing, such as helper sequence or repository calls within a larger application boundary | Observe resulting behavior through the selected boundary | A public method or convenient mock seam alone does not make an interaction a contract |

## Test doubles

A stub supplies input; a mock or spy records an observable output for verification. Library names do not determine the role. Set up stub responses and assert their effect, without locking down incidental query traffic. Verify outgoing effects when their payload, number, or order is part of the contract. Multiple effects may need multiple verifications.

A supplied completion is evidence about response handling, not proof that work was requested. If a scenario claims the whole operation, observe its required request or command before supplying completion. A deliberately scoped response-handler test may supply the response directly; keep that limited claim explicit. Assert contractual initiation, not incidental reads or helper calls.

Put effect checks as close to the external boundary as practical, through an adapter owned by the application. A mock of an inner repository only proves that inner call; keep a separate adapter/integration check for the actual protocol. Use the real adapter against a local test endpoint when appropriate; test doubles cannot establish that a remote provider accepts a request.

An application-owned backend can still be external to a mobile client boundary. State the chosen boundary and follow the call chain before treating HTTP, repositories, notifications, or analytics as equivalent. Diagnostic logs usually are implementation details; business audit records can be observable contracts.

## Integration tests

Cover important orchestration with a few complete paths plus failures that unit tests cannot expose: mapping, protocol, schema, transaction, and recovery errors. When a test claims database semantics, use the production engine or an explicitly justified compatible configuration; an in-memory substitute or a mocked repository establishes less.

Create isolated data, use fresh read state for assertions, and make cleanup reliable. Transaction rollback is useful only if it contains the operations under test; independent connections or asynchronous work may escape it. Fresh reads avoid passing from an ORM cache while persistence is broken.

If integration infrastructure is unavailable, deliver the useful core tests and a precise integration gap. Building a parallel production implementation or a permissive fake to make tests pass gives misleading evidence.
