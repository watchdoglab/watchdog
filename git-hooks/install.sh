#!/usr/bin/env bash
# Installs Watchdog git hooks into the current repo.
#   curl -fsSL https://raw.githubusercontent.com/watchdoglab/watchdog/main/git-hooks/install.sh | bash
# Options: --no-review (secrets check only), --force (replace existing hooks), --uninstall
set -euo pipefail

home="${WATCHDOG_HOME:-$HOME/.watchdog/watchdog}"
review=1 force=0 uninstall=0
for a in "$@"; do
  case "$a" in
    --no-review) review=0 ;;
    --force) force=1 ;;
    --uninstall) uninstall=1 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

git rev-parse --git-dir >/dev/null 2>&1 || { echo "Run this inside a git repo." >&2; exit 1; }
hooks="$(git rev-parse --git-path hooks)"
mkdir -p "$hooks"
marker="# installed by watchdog"

if [ "$uninstall" = 1 ]; then
  for h in pre-commit pre-push; do
    grep -q "$marker" "$hooks/$h" 2>/dev/null && rm "$hooks/$h" && echo "Removed $h hook."
  done
  exit 0
fi

if [ -d "$home/.git" ]; then
  git -C "$home" pull --quiet --ff-only || echo "Could not update $home; using the current copy." >&2
else
  mkdir -p "$(dirname "$home")"
  git clone --quiet --depth 1 https://github.com/watchdoglab/watchdog.git "$home"
fi

write_hook() {
  local name=$1 script=$2 file="$hooks/$1"
  if [ -e "$file" ] && ! grep -q "$marker" "$file" && [ "$force" != 1 ]; then
    echo "Skipped $name: a hook already exists at $file. Re-run with --force to replace it." >&2
    return
  fi
  printf '#!/usr/bin/env bash\n%s\nexec "%s/git-hooks/%s" "$@"\n' "$marker" "$home" "$script" > "$file"
  chmod +x "$file"
  echo "Installed $name hook."
}

write_hook pre-commit watchdog-secrets.sh
[ "$review" = 1 ] && write_hook pre-push watchdog-review.sh
echo "🐕 Watchdog is guarding this repo. Update later by re-running this installer."
