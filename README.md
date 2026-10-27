# 🐕 Watchdog

A pack of security dogs for Claude Code. Each dog guards one surface. Install the marketplace, add the dogs you need.

## Dogs

| Dog | Guards |
|-----|--------|
| **vaptdog** | Vulnerability assessment & pen-test lens: source code, web apps, Android APKs, iOS IPAs, plus the report. |

More dogs later (api, cloud, secrets, deps).

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install vaptdog@watchdog
```

## vaptdog

A security-review lens that stays on all session, plus on-demand audits.

**Commands**
- `/vapt-code` — static audit of a source repo (SAST + dependency CVEs + secrets)
- `/vapt-web` — assessment of a running web app (scope-gated)
- `/vapt-apk` — static Android APK audit (OWASP MASVS)
- `/vapt-ipa` — static iOS IPA audit (OWASP MASVS)
- `/vapt-report` — merge the session's findings into one ranked report

**Config** (`/plugin`): `authScope` (in-scope targets you're authorized to test), `reportDir`.

Turn the lens off with `stop vaptdog`.

## ⚖️ Authorized use only

vaptdog is for **defensive security and authorized testing**. Static analysis of code and apps you own or are authorized to assess is always fine. **Active testing of a live system** (requests, scanning, fuzzing) requires written authorization and an in-scope target — the dog refuses otherwise. Findings and fixes first; exploit/PoC code only on request and in scope. You are responsible for having permission to test any target.
