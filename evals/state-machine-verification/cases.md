# Behavioral evaluation requests

All cases are fictional and self-contained. Treat stated contracts and environment guarantees as supplied evidence. For each, complete an analysis-only task: state a finding or no finding, the decisive history or argument, the smallest useful next check if any, and the limits of the conclusion. Do not implement or change the described systems. Keep each answer proportionate. There is no quota of findings.

## C01 — Publishing a photo

A mobile app submits a photo publication. A timeout may mean the request was discarded, is still running, or was committed with a lost reply. The client retains a unique request ID, but the server neither deduplicates it nor exposes a status query. The requirement says that immediately after timeout the UI must truthfully show either Published or Not published; Pending is forbidden. A new request may create a second publication. Assess the requirement and proposal to show Not published then retry. No other observation or recovery action is available at that decision.

## C02 — Import receipt

An import service atomically stores an operation ID, its result and the imported records. Repeating the same ID and payload returns the stored result without repeating the effect. Conflicting payloads are rejected. The client retains that ID across restarts and displays Checking until it receives the result. It retries while active. The environment contract guarantees eventual request/response delivery and execution while active, and the UI promises eventual resolution only under those conditions, with no deadline. Assess whether timeout makes these promises contradictory.

## C03 — Lost access device

A personal vault promises account recovery when the only trusted device is permanently lost. Login on a replacement requires approval on that lost device. Recovery codes were never issued. Support chat is available only after login; support has no other contact channel. A valid account can reach this situation. Assess the recovery promise and propose the smallest design question or check. You may not assume that the lost device is later found.

## C04 — Supported recovery

The same vault has a public support endpoint usable without login on any new device. Agents verify identity using an independent process that does not need the lost device or its files, then enroll a replacement. This supported path has already been exercised. The promise is that a recovery path remains available during published support hours to users who can complete that verification. There is no instantaneous or unconditional recovery promise. Does the usual login dependency on the lost device establish a defect?

## C05 — Cancellation contract change

Version 1 of a local reminder service documents that a successful Cancel(job) response guarantees no notification for that job will be delivered afterward. Pending jobs are cancellable; the executor honors cancellation before success is returned. Version 2 returns the same success response as soon as a cancellation message is queued, before it is applied. A queued job can deliver a notification between that response and application of the cancellation. The compatibility requirement is to preserve the version 1 promise. Assess the change.

## C06 — Internal queue change

Version 1 documents that Cancel(job) prevents new launches but an already executing delivery may still complete after the response. Version 2 preserves that wording and observable behavior but adds an internal queue and a retry of cancellation delivery. An integration check shows no new launches after cancellation; the queue and its retries produce no extra external notification. An already executing notification completes after Cancel returns in both versions. Assess whether this supplied history demonstrates a compatibility regression. There is no changed progress requirement.

## C07 — Choosing a recovery channel

A component must select one safe recovery channel A, B or C immediately. All three account configurations are reachable: safe channels are {A,B}, {B,C} or {A,C}. In each configuration its retained state and available observations are identical: it knows only that two channels are safe. It cannot retrieve which two, ask or defer this decision. The requirement forbids selecting an unsafe channel in any allowed configuration. The proposed reviewer says that every pair of configurations shares a safe channel, so the component can always choose safely. Assess this claim and scope the conclusion.

## C08 — Optional shared action

A component cannot distinguish whether a background export completed or is still running. It is allowed to return Processing and keep waiting. It retains an operation ID and will receive an authoritative terminal event under the documented eventual-delivery condition. The product requires truthful terminal outcomes after that event, permits Processing before it, and sets no deadline. A reviewer says identical current observations and different actual states make the feature impossible. Assess the claim.

## C09 — Local formatter

A pure function formats an already validated non-negative integer count as a decimal string with no grouping. The requirement and examples are clear: 0 → "0", 12 → "12". It has no side effects, concurrency or history. The task is to choose the next verification step before implementation, not build it. What scope of modeling is useful?

## C10 — Guarded stale callback

A controller stamps each request with an attempt ID at dispatch. On result, it checks that ID before delivering to the reducer; obsolete results release their owned payload and return without business commands. Dispatch and result handling are serialized. Cancellation clears the active attempt. A callback may still arrive after cancellation, as permitted by the SDK. The requirement forbids applying an obsolete result to business state but requires resource cleanup. Assess start A → cancel A → start B → result A. These guards and producer facts have been inspected; the question is whether the supplied trace demonstrates a defect.
