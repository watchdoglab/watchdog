<p align="center"><img src="assets/banner.gif" width="100%" alt="Watchdog — security dogs for your code"></p>

# Watchdog

A pack of security dogs for Claude Code. Each dog guards one surface. Install the marketplace, add the dogs you need.

## Dogs

| | Dog | Guards |
|---|-----|--------|
| <img src="plugins/malinois/assets/icon.gif" width="96" alt="Malinois"> | **malinois** | VAPT — vulnerability assessment & pen-test lens: source code, web apps, Android APKs, iOS IPAs, plus the report. Active tests are scope-gated. See [plugins/malinois](plugins/malinois/README.md). |
| <img src="plugins/husky/assets/icon.gif" width="96" alt="Husky"> | **husky** | Cloud — misconfiguration lens for Terraform, Kubernetes, Dockerfiles and CI pipelines. Static only. See [plugins/husky](plugins/husky/README.md). |
| <img src="plugins/collie/assets/icon.gif" width="96" alt="Collie"> | **collie** | AI — security lens for LLM apps and agents: prompt injection, agent tools, RAG, MCP, model-output handling. Static only. See [plugins/collie](plugins/collie/README.md). |
| <img src="plugins/bloodhound/assets/icon.gif" width="96" alt="Bloodhound"> | **bloodhound** | API — security lens for REST and GraphQL: reads the OpenAPI spec and handlers together for BOLA, mass assignment, broken auth, SSRF and shadow routes. Static only. See [plugins/bloodhound](plugins/bloodhound/README.md). |
| | **beagle** | Privacy — Personal data in code, logs, analytics and SDKs; retention; consent; GDPR/DPDP mapping. New, no benchmark yet. See [plugins/beagle](plugins/beagle/README.md). |
| | **rottweiler** | Supply chain — Lockfiles, typosquats, install scripts, pinning, SBOM, signed releases, licences. New, no benchmark yet. See [plugins/rottweiler](plugins/rottweiler/README.md). |
| | **doberman** | Auth & identity — Login, OAuth/OIDC, sessions, password reset, MFA, JWT, SSO. New, no benchmark yet. See [plugins/doberman](plugins/doberman/README.md). |
| | **shepherd** | Mobile deep dive — Android/iOS/Flutter/React Native: pinning, storage, deep links, WebViews, bridges. New, no benchmark yet. See [plugins/shepherd](plugins/shepherd/README.md). |
| | **dachshund** | Database — Migrations, row-level security, DB roles, Firebase/Supabase rules, encryption. New, no benchmark yet. See [plugins/dachshund](plugins/dachshund/README.md). |
| | **akita** | Secrets lifecycle — Find, rotate and properly store secrets; git history; pre-commit blocking. New, no benchmark yet. See [plugins/akita](plugins/akita/README.md). |
| | **pointer** | Frontend — XSS sinks, CSP, postMessage, token storage, third-party scripts. New, no benchmark yet. See [plugins/pointer](plugins/pointer/README.md). |
| | **saintbernard** | Incident response — Read logs after a breach: timeline, blast radius, containment steps. New, no benchmark yet. See [plugins/saintbernard](plugins/saintbernard/README.md). |
| | **shiba** | Web3 / smart contracts — Solidity/Rust contracts: reentrancy, access control, oracles, upgrades. New, no benchmark yet. See [plugins/shiba](plugins/shiba/README.md). |
| | **pyrenees** | Compliance — Map the pack's findings to SOC 2, ISO 27001, PCI DSS, OWASP ASVS. New, no benchmark yet. See [plugins/pyrenees](plugins/pyrenees/README.md). |

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install malinois@watchdog
/plugin install husky@watchdog
/plugin install collie@watchdog
/plugin install bloodhound@watchdog
# …or any other dog by name, e.g.
/plugin install beagle@watchdog
```

## ⚖️ Authorized use only

Every dog is for **defensive security and authorized testing**. Static analysis of code and apps you own or are authorized to assess is always fine. **Active testing of a live system** (requests, scanning, fuzzing) (malinois `/vapt-web`) requires written authorization and an in-scope target — the dog refuses otherwise. shepherd runs dynamic tools only on builds you own and put in scope; every other dog is static only. Findings and fixes first; exploit/PoC code only on request and in scope. You are responsible for having permission to test any target.
