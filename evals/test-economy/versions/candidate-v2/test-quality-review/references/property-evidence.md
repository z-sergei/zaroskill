# Review what a property actually establishes

Connect the rule to a supported user or caller promise and a concrete illustrating scenario. Identify its input/history domain, preconditions, expected observation and permitted exceptions. A rule inferred solely from the current implementation may be characterization rather than independent protection. Round trips or agreement between two implementations may miss a shared violation of the external contract.

Check these questions only where they affect a material claim:

- Does a permitted input reach the condition and the relevant assertion? A generated test can reject every input; a conditional assertion can never run. Case counts and broad state/phase coverage alone do not settle this.
- Does the assertion remain active in the configuration actually executed? A build can remove it, a feature flag can bypass it, or a catch-all can turn its failure into success. An expected domain error caught narrowly may be correct.
- Can a meaningful behavioral violation fail the unchanged check? Use the focused probe workflow when needed. Mutation of the assertion itself tests the failure mechanism only. A surviving equivalent mutation or an event rejected by a real upstream guard is not evidence of a missed regression.
- Is promised useful behavior covered? An always-rejecting implementation can satisfy a prohibition. Conversely, a safety-only test may intentionally rely on a neighboring success scenario: inspect that coverage before requesting another assertion.
- Does the observation establish the claimed user outcome? A command list is evidence of a decision; integration through the actual coordinator or adapter may be needed for dispatch, delivery or storage. Recognize existing coverage at the appropriate boundary.
- Which operation owes progress, and under what assumptions? A service may remain alive, and a user-driven interaction may wait indefinitely. A missing whole-process termination proof is not a defect. A finite timeout scenario also does not establish arbitrary eventual progress.

Use a witness, executed result or concrete code path to support a finding. Missing coverage counters, a separate property file, a proof or a mutation report are not findings on their own. Ordinary tests can already express the rule well. Preserve healthy controls and the skill's no-findings outcome.

Distinguish a false property, a product defect, a weak test, a model/code mismatch and an unfinished proof. Each needs a different correction; proof-tool failure alone does not identify which occurred.
