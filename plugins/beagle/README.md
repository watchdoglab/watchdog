# beagle — the privacy dog

The privacy dog. Sniffs out personal data flowing into logs, analytics, third-party SDKs and storage, and maps findings to GDPR and India's DPDP Act. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install beagle@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/privacy-audit` | Personal data in code, logs, analytics and SDKs; retention; consent; GDPR/DPDP mapping |

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

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
