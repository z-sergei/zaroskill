# Provenance and rationale

Original operational synthesis of Vladimir Khorikov, *Unit Testing: Principles, Practices, and Patterns* (Manning, 2020), checked 2026-10-22. Full-book access was unavailable: the readable official chapter-1 excerpt establishes the aim and chapter map; the author’s articles supply detailed explanations. This skill is neither an exhaustive summary nor copied book text.

| Principle | Primary evidence |
| --- | --- |
| Sustainable development; selective investment; coverage cannot prove assertion quality | [Official chapter-1 excerpt](https://enterprisecraftsmanship.com/files/Unit-Testing-Chapter-1-Excerpt.pdf), [publisher and chapter map](https://www.manning.com/books/unit-testing) |
| Four pillars; client-relative observable behavior; how to observe persisted state | [How to Assert Database State? (2021)](https://enterprisecraftsmanship.com/posts/how-to-assert-database-state/) |
| Classical preference: independent tests can exercise several real collaborators | [Pragmatic unit testing (2016)](https://enterprisecraftsmanship.com/posts/pragmatic-unit-testing/) |
| Mocks versus stubs, internal communication versus external effects | [When to Mock (2020)](https://enterprisecraftsmanship.com/posts/when-to-mock/) |
| Managed/unmanaged depends on external observability, not hosting or ownership | [Unmanaged dependencies explained (2021)](https://khorikov.org/posts/2021-11-29-unmanaged-dependencies-explained/) |
| Output, state, and communication styles and their tradeoffs | [Styles of unit testing (2016)](https://enterprisecraftsmanship.com/posts/styles-of-unit-testing/) |
| Humble object, extracted decisions, real integration boundaries | [Interfaces for repositories (2017)](https://enterprisecraftsmanship.com/posts/interfaces-for-repositories/), [Pragmatic integration testing (2016)](https://enterprisecraftsmanship.com/posts/pragmatic-integration-testing/) |
| Fidelity of application-owned infrastructure; scope of external systems | [When to include external systems (2016)](https://enterprisecraftsmanship.com/posts/when-to-include-external-systems-into-testing-scope/) |
| Independent expected values; fixtures that retain scenario meaning | [Leaking domain knowledge (2018)](https://enterprisecraftsmanship.com/posts/leaking-domain-knowledge-tests/), [DRY vs DAMP (2020)](https://enterprisecraftsmanship.com/posts/dry-damp-unit-tests/) |
| Private logic through real clients; deterministic inputs and completion | [Unit testing private methods (2017)](https://enterprisecraftsmanship.com/posts/unit-testing-private-methods/), [Non-determinism (2018)](https://enterprisecraftsmanship.com/posts/non-determinism-tests/) |

The skill’s contract note, completion criteria, command discovery, disposable fault/refactor probes, and evaluation protocol are our agent adaptations. They operationalize the principles and are not procedures claimed to appear in the book. Android reducers, emitted command values, coroutine scheduling, and local harness limitations are applications of those principles to a particular architecture.

Use the author’s later boundary clarifications to interpret earlier articles’ broader recommendations. A single passing fault probe supports one concrete test claim; it does not establish comprehensive mutation coverage. A refactor probe similarly exercises one chosen transformation.
