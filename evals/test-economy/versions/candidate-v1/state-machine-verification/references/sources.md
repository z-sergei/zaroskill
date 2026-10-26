# Sources and adaptation

This skill adapts Lamport's ideas to stateful workflows. The contract card, risk routing, event-producer checks and repository integration are engineering synthesis, not a verbatim Lamport method.

- [State the Problem Before Describing the Solution](https://lamport.azurewebsites.net/pubs/state-the-problem.pdf): define correctness separately from the algorithm.
- [Specifying Systems](https://lamport.azurewebsites.net/tla/book-21-07-04.pdf): states, actions, behaviors, specification and model checking.
- [The Temporal Logic of Actions](https://lamport.azurewebsites.net/pubs/lamport-actions.pdf): temporal specifications and correctness.
- [The Existence of Refinement Mappings](https://lamport.azurewebsites.net/pubs/abadi-existence.pdf), Abadi and Lamport: correspondence between levels of description.
- [Knowledge and Common Knowledge in a Distributed Environment](https://groups.csail.mit.edu/tds/papers/Halpern/JACM90.pdf), Halpern and Moses: local histories and indistinguishable situations. The decision check is a narrow engineering application, not a general strategy-synthesis procedure.
- [Realizable and Unrealizable Specifications of Reactive Systems](https://lamport.azurewebsites.net/pubs/abadi-realizable.pdf), Abadi, Lamport and Wolper: specifications and realizability; an unknown outcome alone is not an impossibility proof.
- [Proving Possibility Properties](https://lamport.azurewebsites.net/pubs/lamport-possibility.pdf), Lamport: checking that an allowed model admits relevant environment behavior. Applying this perspective to product recovery is our synthesis.

The compatibility check applies refinement reasoning to versioned consumer promises. It checks safety, supported inputs and progress separately and does not treat every implementation change as a contract change.

This portable package keeps project maps in the consuming repository. It focuses on temporal behavior; general requirements-based implementation and the quality of test doubles belong to their existing workflows.

The 2026-10-24 update also draws on [Anthropic / Theorem verification research](https://www.anthropic.com/research/formal-verification) and the [OSS Verify enrollment skill](https://github.com/theorem-labs/oss-verify/blob/abd10afe7dfc32050a08375c3eb9e2f332025152/.claude/skills/add-project/SKILL.md). The property-execution branch adapts those ideas to temporal models and their connection with real code; operation progress stays separate from service lifetime.

The 2026-10-26 refinement makes test contribution and stopping criteria explicit. Mutation-campaign guidance draws on [PIT scope guidance](https://pitest.org/), [equivalent mutants](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/) and [mutant outcome definitions](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/). It treats tool results as scoped evidence and preserves independent contract, integration and refactor checks.
