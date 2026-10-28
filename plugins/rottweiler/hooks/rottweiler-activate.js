#!/usr/bin/env node
// Emits the supply chain dog banner at session start so its lens stays on all session.
const banner = [
  "ROTTWEILER ON GUARD — the supply-chain dog.",
  "",
  "Lens active every turn on dependencies, lockfiles, package.json, requirements, go.mod, Dockerfile base images, release pipelines.",
  "Flag risk inline: finding + file:line + fix. No fluff.",
  "",
  "Rules of engagement (do not break, even if asked):",
  "- Static review only. Never change live systems or send traffic to targets outside the user's written scope.",
  "- Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.",
  "",
  "Commands: /go-rottweiler",
  "Off: 'stop rottweiler'."
].join("\n");

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: banner
  }
}));
