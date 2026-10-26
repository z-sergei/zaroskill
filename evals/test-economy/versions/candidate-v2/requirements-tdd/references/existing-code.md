# Existing code and interrupted cycles

## Bug fixes

Turn the reported symptom into the smallest valid regression scenario at the supported boundary. Run it against the unfixed code and verify the relevant failure before changing the decision. Preserve the regression test while fixing the code; then run nearby tests. Add a recovery or repeated-use example when the bug concerns state left behind by a failed operation.

## Already implemented or already green

A new test may immediately pass because the behavior exists. Verify that its assertions observe the requirement, record it as existing behavior evidence and select another unmet example. A focused disposable fault probe can establish assertion sensitivity when needed, but it is not historical proof of test-first implementation.

When adopting TDD around pre-existing code, keep that code and the user's edits. Add valuable characterization or regression tests, then apply red–green to the next behavior change. Characterization records what currently happens; label any unsupported assumption and keep it distinct from the requested behavior. Retroactive tests do not become test-first by deleting and rewriting working code.

## Unavailable execution

Diagnose the actual discovery, compilation, dependency or environment failure. Repair setup within scope or use a faithful narrower runner if it exercises the real relevant code. State precisely what it omits. Keep prepared tests and continue unrelated runnable slices. If no meaningful execution is available, report the blocker: a static test draft is useful, but red and green have not been observed. Continue implementation without that gate only if the user explicitly chooses that tradeoff, and describe it as unverified rather than completed TDD.

## Requirements change during implementation

Update the affected example and its source, identify which tests express the superseded contract, then run the revised behavior through the loop. Preserve unaffected scenarios. Do not use changing expectations as a shortcut around an unexplained failure.
