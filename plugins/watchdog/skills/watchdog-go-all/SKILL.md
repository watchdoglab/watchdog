---
name: watchdog-go-all
description: Run the whole Watchdog pack. Use for /watchdog-go-all, "go pack", "run every dog", "full security audit". Static, authorized/defensive only.
---

# watchdog-go-all — the whole pack

1. List the Watchdog dogs available in this session: single-dog skills (not this one or the bundles web, mobile, ai-app, infra, marketplace, defi): vapt (malinois), cloud (husky), ai (collie), api (bloodhound), privacy (beagle), supply-chain (rottweiler), auth (doberman), mobile-app (shepherd), database (dachshund), secrets (akita), frontend (pointer), incident (saintbernard), web3 (shiba), compliance (pyrenees).
2. Skip dogs that don't fit the repo (no Terraform → skip husky, no contracts → skip shiba, no app → skip shepherd, saintbernard only with incident evidence) and say which were skipped and why.
3. Run each remaining dog's skill in static mode (malinois: `code`). Never run active tests here.
4. Merge into one report: Critical → Low, deduplicate findings several dogs raised (keep the clearest, name every dog that saw it), each with `file:line`, why it is exploitable, the smallest fix. Run pyrenees last so it maps the merged findings.
5. Never print a secret value. End with **Not checked** and the one thing to fix first.

All dogs ship in the `watchdog` plugin; if none are available, show `/plugin install watchdog@watchdog`.
