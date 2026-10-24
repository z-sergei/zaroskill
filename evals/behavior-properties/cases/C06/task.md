Use state-machine-verification. Analyze this design; implementation is not requested.
Product contract: the agent service runs continuously. For each submitted export,
poll the backend at most three times; show Ready on success, otherwise show
StillProcessing after the third Pending reply. A later explicit user Refresh
starts a new attempt. Each scheduled poll receives a response, and enabled polls
are eventually scheduled. No clock deadline is promised.
Design: submit sets remaining=3 and sends a poll. On Ready, show Ready and stop
this attempt. On Pending, set remaining=3 from the server's suggested poll budget,
then subtract one; if remaining>0 send another poll, otherwise show StillProcessing.
The server may keep replying Pending with suggested budget 3 indefinitely.
Find any supported issue with a concrete trace and say what evidence would be useful.
