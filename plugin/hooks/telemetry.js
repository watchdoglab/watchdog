#!/usr/bin/env node
// Opt-in, anonymous usage counts. Does nothing unless WATCHDOG_TELEMETRY=1.
// Sends only the command name and how many findings of each severity: no code, paths, repo names or ids.
// Usage: node telemetry.js session | node telemetry.js <command> critical=N high=N medium=N low=N
if (process.env.WATCHDOG_TELEMETRY !== "1") process.exit(0);

const COUNT = "https://watchdoglab.goatcounter.com/count";
const SEVERITIES = ["critical", "high", "medium", "low"];
const [kind, ...pairs] = process.argv.slice(2);
if (!/^[a-z0-9-]{1,40}$/.test(kind || "")) process.exit(0);

const paths = [kind === "session" ? "/plugin/session" : `/plugin/scan/${kind}`];
for (const p of pairs) {
  const [sev, n] = p.split("=");
  const count = Math.min(parseInt(n, 10) || 0, 999);
  if (SEVERITIES.includes(sev) && count > 0) paths.push(`/plugin/found/${sev}/${count}`);
}

const send = (p) =>
  fetch(`${COUNT}?e=true&p=${encodeURIComponent(p)}&rnd=${Math.random().toString(36).slice(2)}`, {
    headers: { "User-Agent": "watchdog-plugin" },
    signal: AbortSignal.timeout(3000),
  }).catch(() => {});

Promise.all(paths.map(send)).finally(() => process.exit(0));
