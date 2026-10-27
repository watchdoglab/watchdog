<img src="assets/banner.gif" width="100%" alt="Pyrenees">

# pyrenees — the compliance dog

The compliance dog. Maps findings from every Watchdog dog to SOC 2, ISO 27001, PCI DSS and OWASP ASVS, and lists the evidence an auditor will ask for. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install pyrenees@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/compliance-map` | Map the pack's findings to SOC 2, ISO 27001, PCI DSS, OWASP ASVS |

The always-on lens watches SOC 2, ISO 27001, PCI DSS, ASVS, audits, controls, evidence, security questionnaires. Turn it off with `stop pyrenees`.

## What it checks

- **Collect findings** — read reports from other Watchdog dogs in the session or the report directory.
- **Map to controls** — each finding to the framework controls it breaks (e.g. SOC 2 CC6.1, ISO 27001 A.8.24, PCI DSS 3.5, ASVS V2).
- **Gaps** — controls with no evidence in the repo (logging, access reviews, backups, incident process).
- **Evidence list** — what to show an auditor: configs, policies, screenshots, tickets, with file paths.
- **Questionnaires** — draft answers from the code and config, marked where a human must confirm.
- **Honesty** — never claim compliance; state coverage and what is unverified.

## Tools it wraps

reads other dogs' reports; no scanners. Missing ones are named in the report's **Not checked** section.

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
