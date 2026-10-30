---
name: watchdog-go-infra
description: Run the Watchdog bundle for a cloud- or infra-heavy system. Use for /watchdog-go-infra. Static, authorized/defensive only.
---

# watchdog-go-infra — bundle for: Cloud- or infra-heavy system

1. Run these dogs' skills in static mode: `watchdog-go-cloud`, `watchdog-go-secrets`, `watchdog-go-supply-chain` (`watchdog-go-vapt`: `code`). Never run active tests here.
2. Skip a dog whose surface isn't in the repo and say which and why.
3. Merge into one report: Critical → Low, deduplicate findings several dogs raised (keep the clearest, name every dog that saw it), each with `file:line`, why it is exploitable, the smallest fix.
4. Never print a secret value. End with **Not checked** and the one thing to fix first.

For every dog at once, use `/watchdog-go-all`.
