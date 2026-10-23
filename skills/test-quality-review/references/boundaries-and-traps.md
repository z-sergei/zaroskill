# Read evidence at the correct boundary

## Assertions and expected outcomes

Follow the assertion back to its input and source of truth. Literal examples, independently worked values and independently justified properties are useful oracles. Calling the same production helper to compute both actual and expected values can hide the same defect on both sides. A property is useful only if it constrains the promised behavior; an assertion that merely checks an object exists may leave its important values unconstrained.

A test passing does not prove that the intended code path ran. Inspect early returns, ignored exceptions, unawaited work, empty parameter sets, missing discovery and patches that replace the decision under test. Treat these as concrete evidence problems when they prevent a meaningful observation.

## Collaborators and effects

| Situation | Evidence to expect |
| --- | --- |
| Deterministic objects inside the chosen boundary | Real collaboration through the consumer's API; helper call order is usually incidental. A unit of behavior may span several classes. |
| Time, randomness, IDs or remote reads | Controlled input or a stub; assert the resulting decision. Read counts matter when explicitly contractual. |
| Persistence observable only through this application | Isolated integration checks with a suitable real engine, meaningful persisted-state observation and a fresh read. Mocked saves or ORM cache values cannot establish commits, mappings or constraints. |
| External request or message observed by another system | Verify promised payload and meaningful multiplicity/order at the owned adapter boundary. This is valid interaction evidence; a double alone does not prove the external provider accepted or delivered it. |
| A core returning a command for its shell | Assert the command as the shell's input contract. Keep command generation distinct from effect execution or durable completion. |

A dependency's role follows the system boundary and independent observability, not its name, hosting location or owner. A stub supplies input; a mock/spy observes output. Direct database observations can be appropriate integration assertions. Several assertions can describe one meaningful outcome.

A supplied completion does not prove that work was requested. For a scenario claiming the whole operation, locate the observation of its required request or command before the supplied result. A missing observation is an initiation gap; check other tests before claiming the gap is system-wide. A deliberately scoped response-handler test may inject the result directly. Preserve that useful coverage without crediting it with initiation or delivery.

## Stateful, asynchronous and structured behavior

Check the starting state's provenance: supported operations or a direct fixture respecting workflow invariants can establish a normal scenario. Constructor access alone cannot. A deliberately invalid state is appropriate for a specified defensive contract; identify that purpose instead of treating it as ordinary workflow coverage. Do not require replaying the lifecycle when a valid direct fixture suffices.

For stateful contracts, look for sequences that distinguish the rule: invalid operations preserve promised state; retries use the supported instance; success permits later reuse; snapshots remain detached when promised. Check assertions at these contractual checkpoints before later actions can hide a failure, including required effects and their absence when promised. Ordering examples need distinguishable values in conflicting orders; checking already sorted data may not discriminate between competing rules. Review identity and case sensitivity where the contract assigns them meaning.

For asynchronous contracts, inspect controlled scheduling, completion and cancellation. Confirm that the test observes the promised checkpoints and effects, including stale results or forbidden work where relevant. A fixed sleep supplies weak timing evidence. Repeated green runs do not establish determinism by themselves. Doubles must honor the port's supported calling and error protocol; a double requiring an incidental call pattern can make a valid refactor look wrong.

For rendered or serialized output, use the consumer's meaning and required fields. Optional formatting, whitespace or representation should not create failures unless it is contractual. A suitable parser may be a better observer than exact string equality. Validate the observer itself: discarded non-rendered content and permissive parsing can also hide required distinctions.

## Maintenance and scope

Prefer helpers that construct inputs while keeping the important scenario values visible. Similar-looking tests can protect different boundaries or aid diagnosis; identical behavioral evidence may justify consolidation. Integration tests cost more but can reveal wiring, mapping and transaction defects that isolated tests cannot. Recommend a cheaper level only if it preserves the relevant evidence.

A missing test is material when a supported, relevant outcome lacks protection in the reviewed scope. Distinguish that from an unspecified product decision, an intentionally excluded integration boundary or a merely possible additional partition. Preserve these limits in the verdict.
