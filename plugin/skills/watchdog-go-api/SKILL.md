---
name: watchdog-go-api
description: Static audit of a REST or GraphQL API by reading the spec and the handlers together. Use for /watchdog-go-api, "audit our API", "check the OpenAPI spec", "find IDOR/BOLA". Static, defensive only.
---

# watchdog-go-api — API audit

Audit the repo (or folder the user names) as an API-security reviewer who owns the result.

## Steps
1. **Inventory.** List every operation in the spec (OpenAPI paths + methods, GraphQL queries/mutations) and every route registered in code. Diff them: code-only routes are shadow APIs, old versions still mounted are zombies.
2. **Scanners.** Run what's installed, read-only: `spectral lint` with an OWASP ruleset, `semgrep`, `gitleaks detect`. Report rule ids.
3. **Per operation.** For each, check: who may call it (spec security vs. middleware actually applied), whose objects it touches (ownership check), which fields it reads/writes (mass assignment, over-shared responses), what bounds apply (rate, size, page, depth, amounts), and whether it fetches user-supplied URLs.
4. **Chain.** Note combinations (unauthenticated export + over-shared fields; mass assignment of `role` + admin-only route).
5. Wrap the scanners — don't reinvent them. If a tool is missing, say which to install.

## Output
Start with stack + API style + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line` (spec and handler where both apply), then — What it is / Why exploitable (concrete request) / Fix (smallest) / If ignored. Never print a secret's value — give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
