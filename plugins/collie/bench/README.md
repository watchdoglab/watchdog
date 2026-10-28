# collie bench

Does collie find real LLM/agent security issues, and how much does the model matter?

- `target/` — a Python support agent (Anthropic SDK + Flask + RAG + MCP config) with 18 planted issues + 2 decoys. **Deliberately insecure. Never run it.** All keys are fake.
- `answers.json` — answer key (file, line, severity) and decoys.

The criticals are chains, not single lines: web content reaches the model (indirect injection) and the model can call a shell tool or `eval`.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/go-collie" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/collie --output-format json > haiku-1.json
```

## Score

- **Recall** = planted issues found / 18 (file + issue, line ±3)
- **Critical recall** = A01–A04 found / 4
- **Chain** = indirect injection → shell/eval described as one path
- **False positives** = decoys reported + findings not real
- **Format** = severity groups, file:line, fix, "Not checked", no secret values printed
