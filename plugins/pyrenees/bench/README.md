# pyrenees bench

Does pyrenees map findings to the right controls, spot missing evidence, and how much does the model matter?

- `target/` — a small invoicing SaaS (config, CI, logging, backup script, access-review CSV, SECURITY.md) plus `findings.md` from other dogs. 18 planted gaps/mappings + 3 decoys. **Deliberately non-compliant. Never deploy it.** All keys are fake.
- `answers.json` — answer key (file, line, severity, expected control IDs) and decoys.

Two criticals are cross-file: C02 (terminated admin in the access-review CSV vs the 24h removal promise in `SECURITY.md`) and C03 (auth log retention in `logging.yaml` vs the 1-year claim in `SECURITY.md`). Several gaps are missing evidence, not bad config (no quarterly review, no restore test, no incident plan).

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-pyrenees" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/pyrenees --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Gaps found** = planted gaps found / 18 (file + issue, line ±3)
- **Critical recall** = C01–C04 found / 4
- **Control IDs correct** = items where the SOC 2 / ISO 27001 / PCI DSS / ASVS IDs match the key / 18
- **Evidence list** = auditor evidence items named with a file path (access review, restore test, log retention, change approval)
- **Decoys flagged** = decoys reported as gaps (lower is better, 0 is the goal)
- **Cross-file** = C02 and C03 found with both files cited
- **Format** = severity groups, file:line, fix, "Not checked", no claim of compliance, no secret values printed
