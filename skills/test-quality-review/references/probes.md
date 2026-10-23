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
