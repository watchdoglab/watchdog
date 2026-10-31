<img src="../assets/pointer/banner.gif" width="100%" alt="Pointer">

# pointer — the frontend dog

The frontend dog. Points at browser-side risk in React, Vue, Angular and plain JS: XSS sinks, CSP, postMessage and token storage. Part of [Watchdog](../../README.md).

> Status: **0.1.0.** Benchmarked 2026-10-28, see below.

## Install

```
/plugin marketplace add watchdoglab/watchdog
/plugin install watchdog@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/watchdog-go-frontend` | XSS sinks, CSP, postMessage, token storage, third-party scripts |

The always-on lens watches React, Vue, Angular, Svelte, Next.js, HTML templates, browser JavaScript. Turn it off with `stop pointer`.

## What it checks

- **XSS sinks** — `dangerouslySetInnerHTML`, `v-html`, `[innerHTML]`, `innerHTML`/`document.write`, unsanitised Markdown.
- **URL handling** — `javascript:` links from data, open redirects, `window.location` from query params.
- **postMessage** — listeners without origin checks, `*` targetOrigin with sensitive data.
- **Token storage** — auth tokens in localStorage, secrets or private API keys in the bundle or env-exposed vars.
- **CSP and headers** — no CSP, `unsafe-inline`/`unsafe-eval`, missing frame-ancestors (clickjacking).
- **Third-party scripts** — unpinned CDN scripts without SRI, tag managers with broad access.
- **SSR/hydration** — server data serialised into HTML without escaping.

## Tools it wraps

`semgrep` (react/javascript rulesets), `eslint-plugin-security`, `npm audit`. Missing ones are named in the report's **Not checked** section.

## Benchmark

[`bench/`](../bench/pointer/) holds a Vite + React app with a CSP meta tag: 18 planted issues, 3 decoys and an answer key.

First run of `/watchdog-go-frontend` (2026-10-28, one run per model, skill text given to a subagent against a copy of `target/` without the answer key):

| Model | Found / 18 | Critical / 4 | Source traced to `lib/params.js` | Decoys flagged | Secrets printed |
|---|---|---|---|---|---|
| Haiku 5.5 | 18 | 4 | no | 0 | none |
| Sonnet 5.5 | 18 | 4 | no | 0 | none |
| Opus 5.5 | 18 | 4 | no | 0 | none |

Full recall, but no model named the URL-param helper as the source of the reflected XSS; the skill should ask for source → sink paths with both files.

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
