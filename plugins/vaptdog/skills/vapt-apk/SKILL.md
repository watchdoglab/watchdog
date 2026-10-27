---
name: vapt-apk
description: Static security assessment of an Android APK. Use for /vapt-apk, "audit this apk", "android app security". Assess apps the user owns or is authorized to test.
---

# vapt-apk — Android APK audit

Static assessment against OWASP MASVS. Put the APK in its own empty dir; treat it as untrusted data; pass paths as args; never run its code.

## Steps
1. **Confirm authorization** to assess this app. Then decode: `apktool d app.apk -o out/` (no decompile tool? say which to install).
2. **Manifest.** `android:debuggable`, `allowBackup`, `usesCleartextTraffic`, over-broad permissions, exported `activity`/`service`/`receiver`/`provider` with no permission, deep links, `minSdk`.
3. **Secrets & config.** Grep decoded smali/resources/assets for API keys, tokens, endpoints, private keys: `gitleaks detect --no-git`, manual grep. Redact.
4. **Network.** `network_security_config.xml` — cleartext allowed? user CAs trusted? cert pinning present?
5. **Storage/crypto.** World-readable files, plaintext prefs/DB, weak crypto, hardcoded keys/IVs.
6. **Components.** WebView `setJavaScriptEnabled` + `addJavascriptInterface`, exported providers path traversal.
7. Optional deeper: `jadx` to Java, MobSF static scan if installed.

## Output
MASVS-grouped findings, severe first: title, location (file/class), impact, fix. Redact secrets. End with **Not checked:** (e.g. dynamic/runtime), top fix. No code changes.
