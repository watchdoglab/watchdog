# rottweiler — the supply chain dog

The supply-chain dog. Guards what you pull in: lockfiles, package names, install scripts, pinning, SBOMs, release signing and licences. Part of [Watchdog](../../README.md).

> Status: **0.1.0, new.** No benchmark or logo yet.

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install rottweiler@watchdog
```

## Commands

| Command | Does |
|---|---|
| `/supply-audit` | Lockfiles, typosquats, install scripts, pinning, SBOM, signed releases, licences |

The always-on lens watches dependencies, lockfiles, package.json, requirements, go.mod, Dockerfile base images, release pipelines. Turn it off with `stop rottweiler`.

## What it checks

- **Known vulnerabilities** — dependencies with CVEs, reachable or not; fixed versions.
- **Lockfile integrity** — missing or out-of-sync lockfiles, registry URLs changed, integrity hashes absent.
- **Typosquats and confusion** — look-alike names, internal package names resolvable on public registries.
- **Install-time code** — `postinstall`/`setup.py` scripts, native builds, `curl | sh`.
- **Pinning** — ranges, `latest`, unpinned base images and CI actions.
- **Provenance** — no SBOM, unsigned releases, no build attestation.
- **Licences** — copyleft or unknown licences in a proprietary product.

## Tools it wraps

`osv-scanner -r .`, `syft`, `grype`, `npm audit`/`pip-audit`, `socket` CLI. Missing ones are named in the report's **Not checked** section.

## Rules

Static review only. Never change live systems or send traffic to targets outside the user's written scope. Never print a secret's value — not keys, tokens or passwords, even weak defaults. Give file:line and the secret type only.
