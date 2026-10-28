---
name: go-beagle
description: On-demand privacy audit (Personal data in code, logs, analytics and SDKs; retention; consent; GDPR/DPDP mapping). Use for /go-beagle. Defensive use only.
---

# go-beagle — privacy audit

Audit the repo (or folder the user names) as a privacy security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: personal data, PII, logging, analytics, SDKs, consent, data retention, GDPR, DPDP. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `semgrep` (custom PII rules), `gitleaks detect`. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the privacy skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
