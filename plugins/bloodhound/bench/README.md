# bloodhound bench

Does bloodhound find real API security issues, and how much does the model matter?

- `target/` — an Express + Apollo GraphQL ledger API with an OpenAPI spec, 18 planted issues + 2 decoys. **Deliberately insecure. Never run it.**
- `answers.json` — answer key (file, line, severity) and decoys.

Harder than earlier benches: no hint comments, and several criticals only show up by reading `app.js` mount order against the routers and the spec (unauthenticated admin router, zombie `/v0`).

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/api-audit" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/bloodhound --output-format json > haiku-1.json
```

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = A01–A04 found / 4
- **Mount order** = H02 and H04 found from `app.js`, not just the router files
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", no secret values printed
