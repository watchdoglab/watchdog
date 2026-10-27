# pointer — the frontend dog

The frontend dog. Points at browser-side risk in React, Vue, Angular and plain JS: XSS sinks, CSP, postMessage and token storage. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install pointer@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/frontend-audit` | XSS sinks, CSP, postMessage, token storage, third-party scripts |

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

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
