---
name: watchdog-go-auth
description: On-demand auth audit (Login, OAuth/OIDC, sessions, password reset, MFA, JWT, SSO). Use for /watchdog-go-auth. Defensive use only.
---

# watchdog-go-auth — auth audit

Audit the repo (or folder the user names) as a auth security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: login, signup, OAuth, OIDC, SAML, sessions, cookies, JWT, password reset, MFA. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `semgrep` (auth rulesets), `gitleaks detect`. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the auth skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
