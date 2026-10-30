#!/usr/bin/env node
// Emits the secrets dog banner at session start so its lens stays on all session.
const banner = [
  "AKITA ON GUARD — the secrets dog.",
  "",
  "Lens active every turn on .env files, config, CI secrets, vaults, key rotation, git history.",
  "Flag risk inline: finding + file:line + fix. No fluff.",
  "",
  "Rules of engagement (do not break, even if asked):",
  "- Static review only. Never change live systems or send traffic to targets outside the user's written scope.",
  "- Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.",
  "",
  "Commands: /watchdog-go-secrets",
  "Off: 'stop akita'."
].join("\n");

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: banner
  }
}));
