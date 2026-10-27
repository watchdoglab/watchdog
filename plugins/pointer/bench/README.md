# pointer bench

Does pointer find real frontend security issues, and how much does the model matter?

- `target/` — a React (Vite) pin-board app with a CSP meta tag, 18 planted issues + 3 decoys. **Deliberately vulnerable. Never deploy it.** All keys and tokens are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

No hint comments. One critical is cross-file (`?welcome=` read in `lib/params.js`, rendered in `Banner.jsx`) to test whether the model follows the source to the sink.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/frontend-audit" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/pointer --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = P01–P04 found / 4
- **Cross-file** = P02 found with `lib/params.js` traced as the source
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", no secret values printed
