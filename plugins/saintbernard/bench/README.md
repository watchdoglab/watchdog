# saintbernard bench

Does saintbernard reconstruct a real breach from logs, and how much does the model matter?

- `target/` — an incident evidence folder (nginx, app, sshd auth, CloudTrail-style JSON, git log excerpt, `INCIDENT.md` ticket) with one attack story: leaked key in a public commit, then login, privilege escalation, data export and persistence. 17 planted facts + 3 decoys. All keys are fake, IPs are documentation ranges. No hint comments.
- `answers.json` — answer key (file, line, severity) and decoys.

Harder than earlier benches: the compromised account (`m.okafor`) appears only in `app.log` and the attacker IP only in `nginx-access.log`, linked by `rid=`. The bastion login only makes sense next to the CloudTrail `SendSSHPublicKey`.

## Run (per model)

Copy `target/` outside the repo so the model can't read the answer key, then:

```bash
claude -p "/incident-triage" --model claude-haiku-5-5 --plugin-dir <path-to>/plugins/saintbernard --output-format json > haiku-1.json
```

Repeat for `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`.

## Score

- **Facts found** = planted facts found / 17 (file + event, line ±3)
- **Critical recall** = I01, I03, I08, I12, I14 found / 5
- **First compromise** = correct first malicious event and time (02:14:09Z, I03), not the git commit or the later web access
- **Timeline order** = events in the report appear in the correct sequence (leak, recon, ssh, priv-esc, export, persistence, StopLogging)
- **Blast radius** = names customer PII (48,210 rows), `svc-deploy` as admin, the bastion, and the session signing key
- **Decoys flagged** = pentest scanner, backup-cron and ssh brute-force correctly called benign, not reported as attacker activity
- **False positives** = findings not real
- **Format** = severity groups, file:line, containment steps ordered by urgency, "Not checked", no secret values printed
