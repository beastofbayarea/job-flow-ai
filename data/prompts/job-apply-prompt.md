Apply

Run locally (not VPS or cloud) parallel sub-agents, one job/tab each. Leave completed tabs open and continue until the queue is exhausted.

Reuse one Chrome debug session, open tabs in the background, skip submitted roles, and never click Submit.

Use short render timeouts: on a hang, reload the same tab once, then reopen once in a new background tab before skipping.

On errors/timeouts, clean up only the affected helper; never kill Chrome or close unrelated tabs.
