---
name: go-collie
description: Static audit of an LLM app or agent (prompts, tools, RAG, MCP config, output handling). Use for /go-collie, "audit our agent", "check for prompt injection". Static, defensive only.
---

# go-collie — LLM app audit

Audit the repo (or folder the user names) as an AI-security reviewer who owns the result.

## Steps
1. **Map.** Find every model call, prompt template, agent tool, retriever/vector store, MCP or plugin config, and every place model output is used. Note which inputs are untrusted (users, web, email, files, other tenants).
2. **Scanners.** Run what's installed, read-only: `semgrep --config p/ai-best-practices` (or `p/python`/`p/javascript`), `gitleaks detect`, `bandit -r .` for Python. Report rule ids.
3. **Trace.** For each untrusted source, follow it into prompts. For each model output, follow it to its sink. Cover the ai skill checklist: injection, agency, output handling, data exposure, MCP, cost/loops.
4. **Chain.** Note combinations (indirect injection + shell tool = remote code execution; injection + Markdown images = data exfiltration).
5. Wrap the scanners — don't reinvent them. If a tool is missing, say which to install.

## Output
Start with stack + models/providers + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults; give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
