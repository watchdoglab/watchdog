<p align="center"><img src="assets/banner.gif" width="100%" alt="Beagle — Privacy by Watchdog"></p>

# beagle — the privacy dog

The privacy dog. Sniffs out personal data flowing into logs, analytics, third-party SDKs and storage, and maps findings to GDPR and India's DPDP Act. Part of [Watchdog](../../README.md).

> Status: **0.1.0.** Benchmarked 2026-10-28, see below.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install beagle@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/go-beagle` | Personal data in code, logs, analytics and SDKs; retention; consent; GDPR/DPDP mapping |

The always-on lens watches personal data, PII, logging, analytics, SDKs, consent, data retention, GDPR, DPDP. Turn it off with `stop beagle`.

## What it checks

- **PII inventory** — fields holding names, emails, phones, government ids, location, health, financial data; where they are stored and for how long.
- **Leaks to logs and traces** — request/response bodies, user objects or tokens logged; error trackers capturing PII.
- **Third parties** — analytics, ads and crash SDKs receiving PII or device ids; data sent cross-border.
- **Consent** — tracking that fires before consent; no way to withdraw.
- **Retention and deletion** — no TTL or purge; account deletion that leaves copies in backups, caches, search indexes.
- **Minimisation** — APIs and exports returning more personal data than the screen needs; PII in URLs.
- **Rights** — no path to export or delete a user's data (GDPR Art. 15/17, DPDP s.11-13).

## Tools it wraps

`semgrep` (custom PII rules), `gitleaks detect`. Missing ones are named in the report's **Not checked** section.

## Benchmark

[`bench/`](bench/) holds a fitness-app Express API and web page with 18 planted privacy issues, 3 decoys and an answer key.

First run of `/go-beagle` (2026-10-28, one run per model, skill text given to a subagent against a copy of `target/` without the answer key):

| Model | Found / 18 | Critical / 4 | Cross-file (B03) | Decoys flagged | Secrets printed |
|---|---|---|---|---|---|
| Haiku 5.5 | 17 | 4 | yes | 2 | none |
| Sonnet 5.5 | 18 | 4 | yes | 2 | none |
| Opus 5.5 | 18 | 4 | yes | 2 | none |

All three flagged the same two decoys (masked audit log, hashed analytics event), so those rules need sharpening. Haiku missed the cross-border transfer (B15). All three also found real bugs the key missed: no auth, so `req.user` is never set (IDOR).

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
