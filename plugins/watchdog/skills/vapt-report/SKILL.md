---
name: vapt-report
description: Merge findings from this session into one ranked VAPT report. Use for /go-malinois report, "write up the findings", "generate the pentest report".
---

# vapt-report — write the report

Collect every finding produced this session (code/web/apk/ipa) into one client-ready report. Write to the plugin `reportDir` (default `./malinois-reports`) as Markdown, filename `malinois-<target>-<date>.md`.

## Structure
1. **Executive summary** — 3-5 lines, plain English: what was assessed, overall risk, count by severity.
2. **Scope & method** — targets, what was tested, tools used, dates, what was out of scope / not tested.
3. **Findings** — most severe first, grouped Critical/High/Medium/Low. Each:
   - Title + severity + CWE/OWASP ref
   - Affected asset (`file:line`, URL, class, or bundle path)
   - Description + concrete impact
   - Evidence (redacted — never full secrets)
   - Remediation (smallest effective fix)
4. **Appendix** — tool versions, raw scanner notes.

Severity: use CVSS-style reasoning (impact x exploitability) and state the vector. If the user has no CVSS tooling, give a defensible High/Med/Low with one-line justification. Keep every secret redacted. State clearly it is an authorized assessment.
