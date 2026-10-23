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
