# INC-2291 - Unusual customer export reported

Reported: 2026-03-12 09:05 UTC by support (customer asked why their data appeared in a breach-notification search).
Owner: platform on-call. Status: open, evidence collected below.

## Environment
- Public edge: nginx in front of `acme-api` (app log carries request ids in `rid=`).
- Bastion host `bastion-1` (sshd). AWS account 111122223333, region eu-west-1.
- Deploy automation uses IAM user `svc-deploy`.

## Known and approved
- Pentest window 2026-03-12 01:00-01:30 UTC from 198.51.100.10 (ticket SEC-118). Scanner traffic from that IP is expected.
- Nightly backup: role `backup-cron` runs at 03:00 UTC from 10.0.4.5.

## Evidence in this folder
- `logs/nginx-access.log`, `logs/app.log`, `logs/auth.log`
- `cloudtrail/events.json`
- `git/git-log.txt` (public repo `acme/acme-api`)

## Ask
Build a timeline, identify the first compromise, the blast radius, and containment steps.
