# beagle bench

Does beagle find real privacy leaks, and how much does the model matter?

- `target/` — Node/Express API plus web page for a fitness app, with 18 planted privacy issues + 3 decoys (GDPR + India DPDP). **Deliberately non-compliant. Never deploy it.** All keys and tokens are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

One issue is cross-file (`users.js` passes the full `RETURNING *` row, `analytics.js` forwards it to a third party) to test whether the model follows data across modules.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-beagle" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/beagle --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = B01–B04 found / 4
- **Cross-file** = B03 found with the `users.js` caller traced
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", secrets redacted
