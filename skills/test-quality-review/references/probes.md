# Focused probes for uncertain findings

A probe tests a specific review claim. It is not a search for a favorable score or a substitute for understanding the requirement.

## Establish the control

State the contract, valid stimulus and expected observation before editing anything. Use a disposable copy of the relevant real code and dependencies, preserving the original tests unchanged. Run the relevant tests on the original copy, record discovery and result, and verify that the exercised baseline is meaningful. Keep any pre-existing failure separate; a red control cannot establish new fault detection.

## Fault sensitivity

Change one relevant decision so the example violates the supported contract. Run the same tests with the same inputs and environment. Inspect what fails and why.

- A relevant assertion failure is direct sensitivity evidence.
- An unexpected domain exception can also expose a genuine behavior regression on a valid path. Report the cause and diagnostic limitation rather than pretending it was an assertion failure or no detection at all.
- A syntax/import error, missing dependency, invalid stimulus, changed discovery or broken probe setup does not establish behavioral sensitivity.
- A green faulty run is a blind spot only after showing the change is observably wrong for this contract. Equivalent or unreachable mutations are not missing tests.

Identify the assertion or new scenario that would distinguish the faulty result. If useful, demonstrate the proposed stronger test separately, while keeping it out of the measured original-suite result. Do not weaken expectations or wrap arbitrary exceptions merely to improve a score.

## Refactor resistance

Choose a transformation that preserves the contract for the reviewed inputs and relevant observers: for example, replacing an internal helper while retaining the public result. Explain why it is equivalent. Run the unchanged tests; inspect whether a failure reflects incidental coupling, a real contract change, or a probe error. A changed public interface, required ordering, timing guarantee or external effect is not automatically a valid refactor.

## Close the probe

Record the baseline, exact change, test command/result, observed consequence and conclusion. Label code reasoning as reasoning when a probe was not executed. Confirm the actual working implementation and tests remain unchanged; run final checks against that unmodified version when the probe workflow could have affected them.

One demonstrated fault or refactor supports one claim. Stop once the disputed finding is resolved, or report what remains inconclusive. A broader mutation campaign needs its own scope and should distinguish equivalent faults, error-only detections and real healthy survivors.

## Automated campaigns and suite reduction

Reuse existing red–green or fault evidence when it answers the review question. Choose an automated campaign for a consequential rule set or material uncertainty, using the repository's supported language/compiler/runner configuration. Bound target files, fault operators and execution cost; distinguish an available run from proposed tooling installation. A provided report is evidence from that report, not a campaign you executed.

Interpret significant survivors using a permitted input and contractual observation. Separate missing input coverage, weak assertions, equivalent or unreachable changes, and inconclusive outcomes. Compiler-generated code can create irrelevant mutations. A tool's timeout classification may indicate a real loop or unstable execution; investigate when it affects the finding. Build and runner errors do not establish assertion quality. State how the tool counts outcomes instead of treating its score as universal quality. Check cache assumptions after dependency/configuration changes and justify narrow exclusions.

Automatic operators can miss domain faults or entirely absent requirements. Pair them with a targeted workflow fault when needed; assess refactor resistance separately. Stop at the scoped question or budget, with unresolved results explicit rather than a demand for 100%.

When reviewing a proposed deletion, verify that its contract distinctions, boundary evidence, useful diagnosis and historical purpose survive elsewhere. A temporary reduction can be compared on relevant seeded faults and preserved behavior, but green ordinary tests or an unchanged finite kill set alone cannot establish redundancy. Equal detection in a campaign may conceal different obligations; test count and line count are supporting cost observations, not a verdict.
