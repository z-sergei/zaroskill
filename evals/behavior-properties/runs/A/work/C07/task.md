Use state-machine-verification. Analyze this design; implementation is not requested.
A support inbox service stays alive to accept future tickets. Each accepted ticket
is independently owned and moves Queued -> Assigned -> Answered or Cancelled.
An assigned ticket may wait indefinitely for a customer's optional reply; the
contract promises neither a reply nor forced expiry. A customer can cancel it.
Once an agent's answer is submitted, the per-ticket worker must deliver it and
mark Answered, assuming the delivery endpoint eventually accepts a retried request
and the worker is eventually scheduled. Retry uses the same durable message ID;
the endpoint commits each ID once and returns the same receipt on repeats.
The worker retries until it gets that receipt, then records Answered. A supervisor
restarts interrupted workers from their durable pending record. Cancel and answer
submission are serialized for one ticket; cancel before submission prevents sending,
while cancel after submission reports that sending has already begun. There is no
deadline or whole-service termination requirement. All stated assumptions hold.
Assess safety/progress promises and whether continuing to run creates an issue.
Do not invent further product requirements or build a formal model unless needed.
