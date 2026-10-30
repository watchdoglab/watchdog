---
name: watchdog-go-database
description: On-demand database audit (Migrations, row-level security, DB roles, Firebase/Supabase rules, encryption). Use for /watchdog-go-database. Defensive use only.
---

# watchdog-go-database — database audit

Audit the repo (or folder the user names) as a database security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: SQL migrations, ORMs, Postgres, MySQL, Supabase, Firebase rules, Firestore, MongoDB. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `squawk` (Postgres migrations), `semgrep`, `gitleaks detect`. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the database skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
