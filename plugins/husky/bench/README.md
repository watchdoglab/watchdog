# husky bench

Does husky find real cloud misconfigs, and how much does the model matter?

- `target/` — Terraform (AWS), Kubernetes, Dockerfile and GitHub Actions for a notes API, with 17 planted misconfigs + 3 decoys. **Deliberately insecure. Never apply or deploy it.** All credentials are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

One misconfig is cross-file (SSH rule in `main.tf`, world-open default in `variables.tf`) to test whether the model follows variables.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/cloud-audit" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/husky --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted misconfigs found / 17 (file + issue, line ±3)
- **Critical recall** = C01–C04 found / 4
- **Cross-file** = C07 found with `variables.tf` traced
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", secrets redacted
