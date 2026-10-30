---
name: watchdog-go-vapt
description: Run Malinois, the VAPT dog. Use for /watchdog-go-vapt [code|web|apk|ipa|report], "go malinois", "pen-test this". Target defaults to code. Authorized/defensive only.
---

# watchdog-go-vapt — VAPT

Read the first word of the arguments as the target and follow that skill exactly:

| Target | Skill | What it does |
|---|---|---|
| `code` (default) | vapt-code | Static audit of the source repo |
| `web <url>` | vapt-web | Web app test; active checks need written scope |
| `apk <file>` | vapt-apk | Android APK review |
| `ipa <file>` | vapt-ipa | iOS IPA review |
| `report` | vapt-report | Write the findings report |

No target or an unknown one: run `code` and say so in one line. Pass the remaining arguments through.
