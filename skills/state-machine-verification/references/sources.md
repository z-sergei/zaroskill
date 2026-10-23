# Sources and adaptation

This skill adapts Lamport's ideas to reducer/controller workflows. The contract card, risk routing, event-producer checks and repository integration are engineering synthesis, not a verbatim Lamport method.

- [State the Problem Before Describing the Solution](https://lamport.azurewebsites.net/pubs/state-the-problem.pdf): define correctness separately from the algorithm.
- [Specifying Systems](https://lamport.azurewebsites.net/tla/book-21-07-04.pdf): states, actions, behaviors, specification and model checking.
- [The Temporal Logic of Actions](https://lamport.azurewebsites.net/pubs/lamport-actions.pdf): temporal specifications and correctness.
- [The Existence of Refinement Mappings](https://lamport.azurewebsites.net/pubs/abadi-existence.pdf), Abadi and Lamport: correspondence between levels of description.

This portable package keeps project maps in the consuming repository. It focuses on temporal behavior; general requirements-based implementation and the quality of test doubles belong to their existing workflows.
