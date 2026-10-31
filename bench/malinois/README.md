# malinois bench

Does malinois find real bugs, and how much does the model matter?

- `target/` — tiny Express notes API with 18 planted vulns + 2 decoys. **Deliberately vulnerable. Never run it exposed or deploy it.** Secrets in `.env` are fake.
- `answers.json` — answer key (file, line, CWE, severity) and decoys.

## Run (per model, 3 runs each)

Run from a clean copy so model can't read the answer key:

```bash
cp -r target /tmp/mal-bench && cd /tmp/mal-bench
claude -p "/go-malinois code" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/malinois --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted vulns found / 18 (match file + issue, line ±3)
- **Critical recall** = V01–V04 found / 4
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", Stripe key redacted
- Record `usage` + `total_cost_usd` from the JSON output.
