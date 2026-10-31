<img src="../assets/saintbernard/banner.gif" width="100%" alt="Saint Bernard">

# saintbernard — the incident response dog

The incident-response dog. Comes to the rescue after something went wrong: reads logs, builds a timeline, finds blast radius and writes containment steps. Part of [Watchdog](../../README.md).

> Status: **0.1.0.** Benchmarked 2026-10-28, see below.

## Install

```
/plugin marketplace add watchdoglab/watchdog
/plugin install watchdog@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/watchdog-go-incident` | Read logs after a breach: timeline, blast radius, containment steps |

The always-on lens watches incidents, breaches, suspicious logs, alerts, compromised keys, post-mortems. Turn it off with `stop saintbernard`.

## What it checks

- **Scope the evidence** — which logs exist (app, auth, cloud audit, CDN, DB); time window; preserve originals read-only.
- **Timeline** — first sign, initial access, actions taken, last activity; with log line references.
- **Indicators** — IPs, user agents, accounts, keys, files and endpoints involved.
- **Blast radius** — data, accounts, systems and secrets the attacker could reach from what was used.
- **Containment** — keys to rotate, sessions to revoke, accounts to lock, rules to add; ordered by urgency.
- **Root cause and follow-up** — the weakness exploited and which Watchdog dog guards it next time.

## Tools it wraps

`jq`, `rg`, `chainsaw`/`sigma` rules, cloud audit-log CLIs (read-only). Missing ones are named in the report's **Not checked** section.

## Benchmark

[`bench/`](../bench/saintbernard/) holds an evidence folder (nginx, app, auth logs, CloudTrail-style events, git log, ticket) with one planted intrusion as 17 facts, 3 decoys and an answer key.

First run of `/watchdog-go-incident` (2026-10-28, one run per model, skill text given to a subagent against a copy of `target/` without the answer key):

| Model | Facts / 17 | Critical / 5 | First compromise right | Decoys flagged | Secrets printed |
|---|---|---|---|---|---|
| Haiku 5.5 | 16 | 5 | yes | 1 (partial) | none |
| Sonnet 5.5 | 16 | 5 | partial | 1 (partial) | none |
| Opus 5.5 | 17 | 5 | yes | 0 | key ID printed |

All three got the timeline order and blast radius (48,210 customer rows). Sonnet called the leaking commit the first compromise, not the key's first use. Opus printed the leaked key ID, so the redaction rule needs to cover key IDs too.

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
