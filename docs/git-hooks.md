# Watchdog git hooks

Two hooks that guard your repo before code leaves your machine.

| Hook | When | What it does | Speed |
|---|---|---|---|
| `watchdog-secrets` | `git commit` | Blocks commits that add API keys, tokens or private keys. Uses gitleaks if installed, built-in patterns if not. Shows file:line and type, never the value. | Instant |
| `watchdog-review` | `git push` | AI security review of the commits you're pushing, using the Watchdog dogs. Blocks on high or critical findings. | ~15–60s |

The review uses whichever AI CLI you already have: Claude Code, Codex or Gemini CLI, so it runs on your own plan or key.

## Install

**With [pre-commit](https://pre-commit.com)** — add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/watchdoglab/watchdog
    rev: main   # pin to a tag or commit SHA in production
    hooks:
      - id: watchdog-secrets
      - id: watchdog-review
```

Then run:

```bash
pre-commit install --hook-type pre-commit --hook-type pre-push
```

**Without pre-commit** — run inside your repo:

```bash
curl -fsSL https://raw.githubusercontent.com/watchdoglab/watchdog/main/git-hooks/install.sh | bash
```

Add `-s -- --no-review` for the secrets check only. Remove with `-s -- --uninstall`. Existing hooks are never overwritten unless you pass `--force`.

## Settings

Set these as environment variables (for example in your shell profile):

| Variable | Default | What it does |
|---|---|---|
| `WATCHDOG_ENGINE` | first installed of `claude`, `codex`, `gemini` | Which AI CLI runs the review. |
| `WATCHDOG_DOGS` | `all` | Which review, as in `/watchdog-go-<dogs>`: `web`, `api`, `vapt`, `ai-app`, … |
| `WATCHDOG_BLOCK_ON` | `high` | Lowest severity that blocks a push. |
| `WATCHDOG_TIMEOUT` | `300` | Seconds before the review gives up. |
| `WATCHDOG_STRICT` | off | `1` blocks the push if the review fails or times out. Off by default so a broken CLI never stops your work. |
| `WATCHDOG_SKIP` | off | `1` skips both hooks once. `git commit/push --no-verify` also works. |

Mark a false-positive secret line with `watchdog:allow` (or `gitleaks:allow` when gitleaks is installed).

## Notes

- The review is read-only: the AI may read files but cannot run commands, edit files or reach the web.
- The pushed diff is treated as untrusted input. Code comments that try to talk the reviewer out of a finding are ignored, but treat the hook as a strong safety net, not a guarantee; keep the PR review ([watchdog-action](https://github.com/watchdoglab/watchdog-action)) on too.
- Make sure your AI CLI is signed in first (run it once interactively). An unsigned CLI waits for a login and the review times out.
