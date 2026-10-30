---
name: watchdog-go-cloud
description: Static audit of infrastructure-as-code and pipelines (Terraform, CloudFormation, Kubernetes, Helm, Dockerfile, GitHub Actions/GitLab CI). Use for /watchdog-go-cloud, "audit our infra", "check terraform/k8s for misconfig". Static, defensive only.
---

# watchdog-go-cloud — infrastructure audit

Audit the repo (or folder the user names) as a cloud-security reviewer who owns the result.

## Steps
1. **Map.** List IaC and pipeline files: `*.tf`, `*.tfvars`, CloudFormation/CDK output, `*.yaml` manifests, Helm charts, `Dockerfile*`, `.github/workflows/`, `.gitlab-ci.yml`. Note which cloud and what is internet-facing.
2. **Scanners.** Run what's installed, read-only: `checkov -d .`, `trivy config .`, `tfsec .`, `kube-score score`, `hadolint Dockerfile`, `actionlint`, `gitleaks detect`. Report each with the rule id.
3. **Read.** Scanners miss context. Follow variables, module defaults and overlays to the real value. Cover the cloud skill checklist: exposure, IAM, secrets, workload hardening, encryption/logging, CI supply chain.
4. **Chain.** Note when two findings combine (public port + no auth, CI write token + unpinned action).
5. Wrap the scanners — don't reinvent them. If a tool is missing, say which to install, don't hand-roll it.

## Output
Start with cloud/stack + what you assumed in scope. Then findings, most severe first, grouped **Critical / High / Medium / Low**. Each: bold title with `file:line`, then — What it is / Why exploitable (concrete case) / Fix (smallest) / If ignored. Redact secrets: Never print a secret's value — not keys, tokens, passwords (even weak or default ones), or connection strings. Name the file:line and the kind of secret only, e.g. `password default (redacted)`. Writing a value and labelling it redacted is a leak. End with **Not checked:** and the one thing to fix first. Change no code unless the user asks. Never apply or deploy.
