<img src="assets/banner.gif" width="100%" alt="Akita">

# akita — the secrets dog

The secrets dog. Goes past finding keys: rotation, storage, .env handling, git history cleanup and pre-commit blocking. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install akita@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/secrets-audit` | Find, rotate and properly store secrets; git history; pre-commit blocking |

The always-on lens watches .env files, config, CI secrets, vaults, key rotation, git history. Turn it off with `stop akita`.

## What it checks

- **Exposure** — secrets in source, config, Dockerfiles, CI files, notebooks, and git history.
- **Storage** — plaintext .env committed, secrets in container images or mobile/web bundles, no vault/secret manager.
- **Scope** — one key shared across environments or services; admin keys where scoped keys exist.
- **Rotation** — no rotation path; leaked keys still valid; long-lived tokens instead of short-lived/OIDC.
- **Prevention** — no pre-commit or CI secret scanning; `.gitignore` missing `.env`.
- **Cleanup** — after a leak: rotate first, then purge history (`git filter-repo`), then invalidate caches and forks.

## Tools it wraps

`gitleaks detect` (incl. history), `trufflehog filesystem .`, `pre-commit`. Missing ones are named in the report's **Not checked** section.

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
