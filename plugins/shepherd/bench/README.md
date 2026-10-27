# shepherd bench

Does shepherd find real mobile security issues, and how much does the model matter?

- `target/` — a Flutter payments app (AndroidManifest, network security config, Gradle, Kotlin bridge, Info.plist, Dart auth/net/deep-link/WebView code) with 18 planted issues + 3 decoys. **Deliberately insecure. Never build or ship it.** All keys are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

Two issues are cross-file: the deep-link `url` param flows from `router.dart` into the WebView in `checkout_webview.dart` (M01), and cleartext is allowed in the manifest while `api_client.dart` uses an `http://` base URL (M07). No hint comments in the source.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/mobile-audit" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/shepherd --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = M01–M04 found / 4
- **Bridge chain** = M01 reported with the deep link (`router.dart`) traced into the WebView and the JS bridge (M02) named as the impact
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", no secret values printed
