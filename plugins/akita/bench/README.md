# akita bench

Does akita find where secrets leak across their lifecycle, and how much does the model matter?

- `target/` — a small invoice API (config, `.env`, CI workflow, app code, `.gitignore`, pre-commit config, rotation script) with 18 planted secrets issues + 3 decoys. **Deliberately leaky. Never deploy it.** Every "secret" is a labelled fake (e.g. `FAKE-STRIPE-KEY-0001`), none match a real provider format, and the model is scored on spotting where secrets live, not on the values.
- `answers.json` — answer key (file, line, severity) and decoys.

One issue is cross-file (the same JWT secret in `.env`, `config/settings.js` and `deploy.yml`) to test whether the model connects reuse across files.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/secrets-audit" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/akita --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = K01–K04 found / 4
- **Cross-file** = K03 found with `.env`, `settings.js` and `deploy.yml` traced
- **False positives** = decoys reported + findings not real
- **Secret values never printed** = no fake value (e.g. `FAKE-...`) appears in the output; file:line and secret type only
- **Format** = severity groups, file:line, fix, "Not checked"
