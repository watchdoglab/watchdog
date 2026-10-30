---
name: vapt-code
description: Static security audit (SAST) of a source repo. Use for /go-malinois code, "audit this code for security", "find vulnerabilities in the codebase". Authorized/defensive only.
---

# vapt-code — source audit

Audit the repo (or folder the user names) as a security reviewer who owns the result.

## Steps
1. **Confirm scope.** This is static analysis of code the user is responsible for — fine to proceed. Note the stack and entry points (README, build/deploy config, routes, handlers, jobs).
2. **Dependencies (SCA).** Run what's installed, read-only: `npm audit --json`, `pip-audit`, `osv-scanner -r .`, `govulncheck`, `bundler-audit`. Report known-CVE packages with the fixed version.
3. **Secrets.** Scan source and, if present, git history: `gitleaks detect`, `trufflehog filesystem .`. Redact hits.
4. **Code.** Trace untrusted input to sinks. Cover the vapt checklist: injection, authz (IDOR/BOLA), authn/session, SSRF, path traversal, deserialization, crypto, insecure defaults. Read auth, payment, file, and data-write paths fully.
5. Wrap the scanners — don't reinvent them. If a tool is missing, say which to install, don't hand-roll it.

## Output
Start with stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks.
