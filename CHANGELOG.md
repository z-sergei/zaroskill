# Changes

## 2026-10-24

### Behavior properties and user scenarios

- Connected concrete business scenarios with general rules over permitted data and event histories in all four personal skills.
- Added conditional checks for assertions that are unreachable, disabled by the exercised configuration or hidden by failure handling; preserved healthy controls and scoped fault probes.
- Made useful successful behavior and operation-specific progress explicit, while allowing continuously running services and optional user waits.
- Clarified how component observations connect to the user's outcome through the relevant real orchestration or integration boundary.
- Kept generated tests, UI tests and formal models conditional on a concrete risk, with independent attribution and portable references.
- Compared the first revision with the baseline in one blind eight-case paired run; results tied. Found a shared missing progress assumption, then clarified the interruption between receipt and durable completion in the temporal skill. The evaluation report separates that follow-up from the blind comparison.

### Initial portable repository

- Imported the four existing personal skills and pinned unmodified Matt Pocock domain-modeling/codebase-design packages with their license and source revision.
- Made state-machine-verification independent of its original Android project map.
- Added conditional checks for decisions under incomplete information, recovery after resource loss, and compatibility between behavioral contracts.
- Made the handoff to the three testing workflows explicit without making them dependencies.
- Added a portable installer with previews and recoverable replacements, packaging checks, installation tests and a Git transfer guide.
- Preserved the portable Khorikov evaluation harness without original application files or historical run data.
- Recorded a fresh-context comparison of the original and updated temporal skill on ten development cases; see its evaluation report for the actual outcome and limitations.
