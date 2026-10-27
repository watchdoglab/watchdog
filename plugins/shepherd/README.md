<img src="assets/banner.gif" width="100%" alt="Shepherd">

# shepherd — the mobile dog

The mobile dog. A deep dive on Android, iOS, Flutter and React Native apps: storage, pinning, deep links, WebViews and native bridges. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install shepherd@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/mobile-audit` | Android/iOS/Flutter/React Native: pinning, storage, deep links, WebViews, bridges |

The always-on lens watches Android, iOS, Flutter, React Native, AndroidManifest, Info.plist, WebView, deep links, mobile storage. Turn it off with `stop shepherd`.

## What it checks

- **Local storage** — tokens or PII in SharedPreferences/UserDefaults/AsyncStorage/Hive instead of Keystore/Keychain.
- **Transport** — cleartext allowed, no certificate pinning on sensitive calls, debug trust anchors.
- **Deep links and intents** — exported activities, unvalidated deep-link params reaching auth or WebViews, intent redirection.
- **WebViews** — JavaScript bridges exposed to remote content, file access enabled, loading untrusted URLs.
- **Secrets in the binary** — API keys, Firebase config with open rules, hardcoded endpoints.
- **Platform hardening** — debuggable builds, backups allowed, no root/jailbreak or tamper response where the app needs it.
- **Cross-platform bridges** — Flutter platform channels / RN native modules trusting JS/Dart input.

## Tools it wraps

`mobsfscan`, `apktool`, `jadx`, `semgrep`; `frida` only on in-scope builds the user owns. Missing ones are named in the report's **Not checked** section.

## Rules

Static review by default. Dynamic tooling only on builds the user owns and has put in written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
