---
name: watchdog-go-frontend
description: On-demand frontend audit (XSS sinks, CSP, postMessage, token storage, third-party scripts). Use for /watchdog-go-frontend. Defensive use only.
---

# watchdog-go-frontend — frontend audit

Audit the repo (or folder the user names) as a frontend security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: React, Vue, Angular, Svelte, Next.js, HTML templates, browser JavaScript. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `semgrep` (react/javascript rulesets), `eslint-plugin-security`, `npm audit`. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the frontend skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
