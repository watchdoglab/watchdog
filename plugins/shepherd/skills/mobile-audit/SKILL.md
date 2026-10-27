---
name: mobile-audit
description: On-demand mobile audit (Android/iOS/Flutter/React Native: pinning, storage, deep links, WebViews, bridges). Use for /mobile-audit. Defensive use only.
---

# mobile-audit — mobile audit

Audit the repo (or folder the user names) as a mobile security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: Android, iOS, Flutter, React Native, AndroidManifest, Info.plist, WebView, deep links, mobile storage. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `mobsfscan`, `apktool`, `jadx`, `semgrep`; `frida` only on in-scope builds the user owns. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the mobile skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
