# dachshund — the database dog

The database dog. Digs into schemas, migrations, row-level security, database roles and Firebase/Supabase rules. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install dachshund@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/db-audit` | Migrations, row-level security, DB roles, Firebase/Supabase rules, encryption |

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

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
