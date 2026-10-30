<img src="../assets/dachshund/banner.gif" width="100%" alt="Dachshund">

# dachshund — the database dog

The database dog. Digs into schemas, migrations, row-level security, database roles and Firebase/Supabase rules. Part of [Watchdog](../../README.md).

> Status: **0.1.0.** Benchmarked 2026-10-28, see below.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install watchdog@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/watchdog-go-database` | Migrations, row-level security, DB roles, Firebase/Supabase rules, encryption |

The always-on lens watches SQL migrations, ORMs, Postgres, MySQL, Supabase, Firebase rules, Firestore, MongoDB. Turn it off with `stop dachshund`.

## What it checks

- **Backend-as-a-service rules** — Firebase/Firestore/Storage rules allowing read/write to any signed-in or anonymous user; Supabase tables without RLS.
- **Row-level security** — RLS disabled or policies using client-controlled values; service-role key used client-side.
- **Roles and grants** — app connecting as superuser/owner, `GRANT ALL`, shared credentials across services.
- **Sensitive columns** — passwords, tokens, government ids stored unencrypted or unhashed.
- **Migrations** — destructive changes without backup, locks on hot tables, data backfills exposing data.
- **Exposure** — databases reachable from the internet, default ports and credentials, no TLS.
- **Injection surface** — raw queries in ORMs, dynamic identifiers built from input.

## Tools it wraps

`squawk` (Postgres migrations), `semgrep`, `gitleaks detect`. Missing ones are named in the report's **Not checked** section.

## Benchmark

[`bench/`](../bench/dachshund/) holds Supabase migrations, Firestore/Storage rules, DB roles and client code: 18 planted issues, 4 decoys and an answer key.

First run of `/watchdog-go-database` (2026-10-28, one run per model, skill text given to a subagent against a copy of `target/` without the answer key):

| Model | Found / 18 | Critical / 5 | Cross-file RLS (Q05) | Decoys flagged | Secrets printed |
|---|---|---|---|---|---|
| Haiku 5.5 | 17 | 4 | yes | 2 | none |
| Sonnet 5.5 | 17 | 4 | yes | 1 | none |
| Opus 5.5 | 18 | 5 | yes | 0 | none |

Opus was the only full score; Haiku and Sonnet each missed one critical and over-flagged public buckets.

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
