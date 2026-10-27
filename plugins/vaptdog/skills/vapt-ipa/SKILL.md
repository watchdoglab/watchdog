---
name: vapt-ipa
description: Static security assessment of an iOS IPA. Use for /vapt-ipa, "audit this ipa", "ios app security". Assess apps the user owns or is authorized to test.
---

# vapt-ipa — iOS IPA audit

Static assessment against OWASP MASVS. IPA in its own empty dir, untrusted data, paths as args, never execute it.

## Steps
1. **Confirm authorization.** Then unzip: `unzip app.ipa -d out/`; the app is in `out/Payload/<App>.app/`.
2. **Info.plist.** App Transport Security — `NSAllowsArbitraryLoads`? exception domains? `URL schemes`, `UIFileSharingEnabled`, debug flags.
3. **Entitlements.** `codesign -d --entitlements :- <binary>` (macOS) — app groups, keychain sharing, associated domains.
4. **Secrets.** `strings` and grep binary + bundle for keys, tokens, endpoints, private keys. Redact.
5. **Binary protections.** PIE, stack canaries, ARC, encryption (`otool -l` / `otool -hv`); no pinning evidence.
6. **Storage/crypto.** Plaintext in `NSUserDefaults`/plist/DB, Keychain misuse, weak crypto, hardcoded keys.
7. Optional: MobSF static scan if installed.

## Output
MASVS-grouped findings, severe first: title, location, impact, fix. Redact secrets. End with **Not checked:** (dynamic/jailbreak runtime), top fix. No code changes.
