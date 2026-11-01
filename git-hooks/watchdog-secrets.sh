#!/usr/bin/env bash
# Watchdog pre-commit: blocks commits that add secrets.
# Reports file:line and secret type only, never the value.
# Skip once with WATCHDOG_SKIP=1 git commit ..., or mark a line with "watchdog:allow".
set -uo pipefail

[ "${WATCHDOG_SKIP:-}" = "1" ] && exit 0

if command -v gitleaks >/dev/null 2>&1 && [ "${WATCHDOG_NO_GITLEAKS:-}" != "1" ]; then
  out=$(gitleaks git --pre-commit --staged --redact=100 --no-banner --log-level error -v 2>&1)
  status=$?
  if [ $status -eq 0 ]; then exit 0; fi
  if [ $status -eq 1 ]; then
    echo "🐕 Watchdog (akita): secrets found in staged changes. Commit blocked."
    # Fingerprint is file:rule:line; print it as file:line  rule
    printf '%s\n' "$out" | sed -n 's/^Fingerprint:[[:space:]]*//p' | awk -F: '{ print "  " $1 ":" $NF "  " $(NF-1) }'
    echo "Remove the secret, rotate it if it was ever pushed, and load it from env or a vault."
    echo "False positive? Add 'gitleaks:allow' to the line, or commit with WATCHDOG_SKIP=1."
    exit 1
  fi
  echo "🐕 Watchdog: gitleaks failed ($status); falling back to built-in patterns." >&2
fi

# Built-in patterns: name<TAB>extended regex
patterns='AWS access key	AKIA[0-9A-Z]{16}
GitHub token	(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,}
Anthropic API key	sk-ant-[A-Za-z0-9_-]{20,}
OpenAI API key	sk-(proj-)?[A-Za-z0-9_-]{32,}
Google API key	AIza[0-9A-Za-z_-]{35}
Slack token	xox[abposr]-[A-Za-z0-9-]{10,}
Stripe live key	(sk|rk)_live_[0-9A-Za-z]{20,}
Private key	-----BEGIN ([A-Z]+ )?PRIVATE KEY-----
JWT	eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}
Password in URL	[a-z]+://[^/:@ ]+:[^/@ ]{3,}@'

pats_file=$(mktemp "${TMPDIR:-/tmp}/watchdog.XXXXXX")
trap 'rm -f "$pats_file"' EXIT
printf '%s\n' "$patterns" > "$pats_file"

found=$(git diff --cached -U0 --no-color --diff-filter=ACMR | awk -F'\n' -v pats_file="$pats_file" '
  BEGIN { while ((getline row < pats_file) > 0) { split(row, p, "\t"); n++; name[n] = p[1]; re[n] = p[2] } }
  /^\+\+\+ / { file = substr($0, 7); next }
  /^@@/ { match($0, /\+[0-9]+/); line = substr($0, RSTART + 1, RLENGTH - 1) + 0; next }
  /^\+/ {
    text = substr($0, 2)
    if (text !~ /watchdog:allow/) for (i = 1; i <= n; i++) if (text ~ re[i]) { print "  " file ":" line "  " name[i]; break }
    line++
  }') || { echo "🐕 Watchdog: secrets check failed to run. Commit blocked; use WATCHDOG_SKIP=1 to bypass." >&2; exit 1; }

if [ -n "$found" ]; then
  echo "🐕 Watchdog (akita): secrets found in staged changes. Commit blocked."
  printf '%s\n' "$found"
  echo "Remove the secret, rotate it if it was ever pushed, and load it from env or a vault."
  echo "False positive? Add 'watchdog:allow' to the line, or commit with WATCHDOG_SKIP=1."
  exit 1
fi
exit 0
