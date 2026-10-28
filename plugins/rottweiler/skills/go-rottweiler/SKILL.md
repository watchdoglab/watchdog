---
name: go-rottweiler
description: On-demand supply chain audit (Lockfiles, typosquats, install scripts, pinning, SBOM, signed releases, licences). Use for /go-rottweiler. Defensive use only.
---

# go-rottweiler — supply chain audit

Audit the repo (or folder the user names) as a supply chain security reviewer who owns the result.

## Steps
1. **Map.** Find everything in scope: dependencies, lockfiles, package.json, requirements, go.mod, Dockerfile base images, release pipelines. Note what is internet-facing or holds sensitive data.
2. **Scanners.** Run what's installed, read-only: `osv-scanner -r .`, `syft`, `grype`, `npm audit`/`pip-audit`, `socket` CLI. Report rule ids. If a tool is missing, say which to install; don't hand-roll it.
3. **Read.** Scanners miss context. Cover the supply-chain skill checklist end to end.
4. **Chain.** Note when two findings combine into something worse.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
