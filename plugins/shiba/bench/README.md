# shiba bench

Does shiba find real smart contract bugs, and how much does the model matter?

- `target/` — a Foundry-style DeFi project (vault, oracle, UUPS-less proxy, token, deploy script), with 18 planted vulnerabilities + 3 decoys. **Deliberately insecure. Never deploy it.** All keys are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

Two issues are cross-contract (W03: `Oracle.getPrice` spot price consumed by `Vault.borrow`; W05: proxy slot 0 collides with `Vault.owner`) to test whether the model follows calls and storage layout across files.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-shiba" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/shiba --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted vulns found / 18 (file + issue, line ±3)
- **Critical recall** = W01–W05 found / 5
- **Cross-contract** = W03 and W05 found with both contracts traced
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, exploit case, fix, "Not checked", secrets redacted
