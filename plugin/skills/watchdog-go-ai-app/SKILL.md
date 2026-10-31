---
name: watchdog-go-ai-app
description: Run the Watchdog bundle for a ai product, chatbot or agent. Use for /watchdog-go-ai-app. Static, authorized/defensive only.
---

# watchdog-go-ai-app — bundle for: AI product, chatbot or agent

1. Run these dogs' skills in static mode: `watchdog-go-ai`, `watchdog-go-api`, `watchdog-go-privacy`, `watchdog-go-secrets` (`watchdog-go-vapt`: `code`). Never run active tests here.
2. Skip a dog whose surface isn't in the repo and say which and why.
3. Merge into one report: Critical → Low, deduplicate findings several dogs raised (keep the clearest, name every dog that saw it), each with `file:line`, why it is exploitable, the smallest fix.
4. Never print a secret value. End with **Not checked** and the one thing to fix first.

For every dog at once, use `/watchdog-go-all`.
