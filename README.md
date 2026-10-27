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

More dogs later (privacy, supply chain).

## Install

```
/plugin marketplace add salahu01/watchdog
/plugin install malinois@watchdog
/plugin install husky@watchdog
/plugin install collie@watchdog
/plugin install bloodhound@watchdog
```

## ⚖️ Authorized use only

Every dog is for **defensive security and authorized testing**. Static analysis of code and apps you own or are authorized to assess is always fine. **Active testing of a live system** (requests, scanning, fuzzing) (malinois `/vapt-web`) requires written authorization and an in-scope target — the dog refuses otherwise. husky, collie and bloodhound are static only. Findings and fixes first; exploit/PoC code only on request and in scope. You are responsible for having permission to test any target.
