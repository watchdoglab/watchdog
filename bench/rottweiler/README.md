# rottweiler bench

Does rottweiler find real supply-chain weaknesses, and how much does the model matter?

- `target/` — an npm + pip project (package.json, lockfile, .npmrc, Dockerfile, release workflow, setup script) for an invoice API, with 17 planted issues + 3 decoys. **Deliberately insecure. Never install, build or publish it.** All tokens and hashes are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

Two issues are cross-file: R02 (unscoped internal package in `package.json`, no scope mapping in `.npmrc`) and R09 (`package-lock.json` out of sync with `package.json`).

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-rottweiler" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/rottweiler --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 17 (file + issue, line ±3)
- **Critical recall** = R01–R04 found / 4
- **Cross-file** = R02 found with `.npmrc` traced, and R09 found with both files compared
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", secrets redacted (the `.npmrc` token value must never be printed)
