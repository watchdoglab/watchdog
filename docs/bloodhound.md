<p align="center"><img src="../assets/bloodhound/banner.gif" width="100%" alt="Bloodhound — API by Watchdog"></p>

# bloodhound — the API dog

A security lens for REST and GraphQL APIs that stays on all session, plus an on-demand audit. It reads the spec and the handlers together, because most API bugs live in the gap between them. Part of [Watchdog](../../README.md).

## Install

```
/plugin marketplace add watchdoglab/watchdog
/plugin install watchdog@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/watchdog-go-api` | Static audit of a REST or GraphQL API: inventories spec vs. routes, then checks every operation |

The always-on lens follows the OWASP API Top 10: object- and function-level authorization, broken authentication, mass assignment and over-shared fields, missing rate/size/depth limits, unbounded business flows, SSRF, misconfiguration, and shadow or zombie endpoints. Turn it off with `stop bloodhound`.

## Scanners

bloodhound wraps tools you have installed: `spectral` (OWASP ruleset), `semgrep`, `gitleaks`. Missing ones are named in the report's **Not checked** section.

## Benchmark

[`bench/`](../bench/bloodhound/) holds an Express + Apollo GraphQL ledger API with an OpenAPI spec: 18 planted issues, 2 decoys, an answer key, and no hint comments. Several criticals only show up by reading the router mount order in `app.js` against the spec.

First run of `/watchdog-go-api` (2026-10-27, one run per model, skill text given to a subagent):

| Model | Found / 18 | Critical / 5 | Mount-order bugs (H02, H04) | Decoys flagged | Tokens |
|---|---|---|---|---|---|
| Haiku 5.5 | 18 | 5 | yes | 0 | ~98k |
| Sonnet 5.5 | 18 | 5 | yes | 0 | ~74k |
| Opus 5.5 | 18 | 5 | yes | 0 | ~73k |

Removing hint comments and hiding bugs in mount order still did not separate the models. Haiku went deepest on extras (CSV injection, unhandled-rejection crash) but used ~30% more tokens and ~2.5x the time.

## Static only

bloodhound never sends requests to a live API; active testing is malinois `/watchdog-go-vapt web`, scope-gated. It never prints a found secret's value.
