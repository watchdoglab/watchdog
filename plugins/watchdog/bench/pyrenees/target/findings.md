# Watchdog findings: ledgerly (merged from other dogs)

| # | Dog | Sev | Where | Finding |
|---|---|---|---|---|
| 1 | gatekeeper | critical | db/schema.sql:9 | `cards.pan` and `cards.cvv` are plain TEXT columns |
| 2 | husky | critical | scripts/backup.sh:5 | nightly dump copied to S3 with no server-side encryption flag |
| 3 | gatekeeper | high | config/app.yaml:18 | live payment provider key committed in config |
| 4 | bloodhound | high | config/app.yaml:11 | admin login does not require a second factor |
| 5 | bloodhound | high | config/app.yaml:10 | password minimum length is 6 |
| 6 | husky | high | config/app.yaml:4 | TLS 1.0 still accepted |
| 7 | husky | high | .github/workflows/ci.yml:25 | production deploy runs straight from a push to main |
| 8 | bloodhound | medium | config/app.yaml:8 | sessions never expire when idle |
| 9 | husky | medium | .github/workflows/ci.yml:17 | dependency audit result is ignored |
| 10 | gatekeeper | medium | src/server.js:5 | full request body written to the console on /charge |
| 11 | gatekeeper | low | compliance/access-review.csv:7 | generic shared admin mailbox holds an admin role |
| 12 | gatekeeper | low | config/logging.yaml:6 | request bodies logged by the app sink |
| 13 | husky | info | config/logging.yaml:12 | auth log sink has a retention_days setting |
