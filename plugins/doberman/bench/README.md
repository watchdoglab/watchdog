# doberman bench

Does doberman find real auth and identity flaws, and how much does the model matter?

- `target/` — an Express service with login, OAuth, SAML SSO, password reset, MFA and JWT sessions, with 18 planted issues + 3 decoys. **Deliberately insecure. Never run or deploy it.** All secrets are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

No hint comments. One issue is cross-file: `login.js` issues a full session before MFA while `mfa.js` has a verify endpoint that gates nothing, so the model must connect the two.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-doberman" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/doberman --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = D01–D04 found / 4
- **MFA bypass** = D02 found with `mfa.js` traced (login issues full session before MFA)
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", no secret values printed
