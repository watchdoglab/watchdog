---
name: watchdog-go-marketplace
description: Run the Watchdog bundle for a marketplace with payments. Use for /watchdog-go-marketplace. Static, authorized/defensive only.
---

# watchdog-go-marketplace — bundle for: Marketplace with payments

1. Run these dogs' skills in static mode: `watchdog-go-vapt`, `watchdog-go-api`, `watchdog-go-auth`, `watchdog-go-database`, `watchdog-go-mobile-app`, `watchdog-go-privacy` (`watchdog-go-vapt`: `code`). Never run active tests here.
2. Skip a dog whose surface isn't in the repo and say which and why.
3. Merge into one report: Critical → Low, deduplicate findings several dogs raised (keep the clearest, name every dog that saw it), each with `file:line`, why it is exploitable, the smallest fix.
4. Never print a secret value. End with **Not checked** and the one thing to fix first.

For every dog at once, use `/watchdog-go-all`.
