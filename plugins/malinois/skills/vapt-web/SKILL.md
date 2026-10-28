---
name: vapt-web
description: Security assessment of a running web app. Use for /go-malinois web, "test this website for vulnerabilities", "web pentest". Active testing needs in-scope written authorization.
---

# vapt-web — web app assessment

## Gate first (hard stop)
Active testing hits a live system. Before any request to the target:
- Confirm the target URL/host is in the user's **written** authorized scope (plugin `authScope` or stated by the user now).
- Out of scope or unclear -> **stop**, ask the user to confirm authorization. Do not probe.

## Steps (once in scope)
1. **Passive first.** TLS/cert, security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options), cookie flags (HttpOnly/Secure/SameSite), CORS policy, exposed server/version, error verbosity.
2. **Auth & session.** Login flow, session fixation, token handling, password reset, MFA gaps, logout.
3. **OWASP Top 10 / ASVS walk.** Access control (IDOR), injection, SSRF, misconfig, known-vuln components, insecure design.
4. **Tooling** (only in scope, wrap existing tools): `nuclei -u <target>`, `nikto -host`, OWASP ZAP baseline. Non-destructive by default; no DoS, no mass requests, no data destruction.
5. Rate-limit yourself; don't degrade the service.

## Output
Findings most severe first, grouped Critical/High/Medium/Low: title, evidence (request/response, redacted), impact, fix, CWE/OWASP ref. End with scope tested, **Not checked:**, top fix.
