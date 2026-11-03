---
name: watchdog-go-supply-chain
description: On-demand supply chain audit (Lockfiles, typosquats, install scripts, pinning, SBOM, signed releases, licences). Use for /watchdog-go-supply-chain. Defensive use only.
---

# watchdog-go-supply-chain — supply chain audit

Audit the repo (or folder the user names) as a supply chain security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: dependencies, lockfiles, package.json, requirements, go.mod, Dockerfile base images, release pipelines. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `osv-scanner -r .`, `syft`, `grype`, `npm audit`/`pip-audit`, `socket` CLI. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the supply-chain skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.

## Usage count (opt-in)
Only if the environment variable `WATCHDOG_TELEMETRY` is `1`: after the report, run `node "${CLAUDE_PLUGIN_ROOT}/hooks/telemetry.js" watchdog-go-supply-chain critical=N high=N medium=N low=N` with your finding counts. It sends only those numbers. Otherwise skip this step.
