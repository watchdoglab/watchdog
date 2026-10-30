# dachshund bench

Does dachshund find real database security issues, and how much does the model matter?

- `target/` — Supabase migrations (RLS, storage), Firestore/Storage rules, a roles script, a docker-compose Postgres and app query code, with 18 planted issues + 4 decoys. **Deliberately insecure. Never apply or deploy it.** All credentials are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

No hint comments. One issue is cross-file (the RLS policy in `001_init.sql` trusts `user_metadata`, which `src/client.js` lets the user set at signup). The Firestore catch-all rule only shows up by reading the whole rules file.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-dachshund" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/dachshund --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = Q01–Q05 found / 5
- **Cross-file** = Q05 found with the `user_metadata` signup path in `src/client.js` traced
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", no secret values printed
