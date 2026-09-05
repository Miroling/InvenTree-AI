# InvenTree-AI

An open-source project for connecting InvenTree to ChatGPT in a browser, Codex, and Claude through an authenticated hosted Model Context Protocol (MCP) service.

**Status: planning, research, and deployment scaffolding.** Docker Compose and a Helm chart for k3s are available. The repository does not yet contain a working MCP service, runtime image, implemented OAuth integration, or installable plugin. Template validation does not establish runtime readiness.

See [Docker Compose](compose.yaml), [the Helm chart](charts/inventree-ai), and [deployment instructions](docs/deployment/README.md). Deployment artifacts require an image implementing the [proposed runtime contract](docs/deployment/runtime-contract.md); no runnable image is implied by these examples.

## Follow the plan

The canonical plan is [Find the path to cloud InvenTree access from ChatGPT, Codex, and Claude](https://github.com/Miroling/InvenTree-AI/issues/1). Its child issues hold investigations and decisions; native GitHub dependencies show what can be worked on next.

Research notes are linked from their research tickets. Decisions are recorded in issue resolution comments, with a short index in the map.

Completed research:

- [ChatGPT and Codex connection requirements](https://github.com/Miroling/InvenTree-AI/blob/a8e093cc508c6871a922df3a7bfda7af46ada9e4/docs/research/client-compatibility.md)
- [PoC capabilities and cloud migration gaps](https://github.com/Miroling/InvenTree-AI/blob/acd07adfcdda89f18bd40917d417840480bb0b7d/docs/research/poc-assessment.md)
- [Hosting options and credential boundaries](https://github.com/Miroling/InvenTree-AI/blob/d89363a6c82ef67b3ae145ccbbc7260211fff81d/docs/research/hosting-options.md)
- [Authenticated access across ChatGPT, Codex, and Claude](https://github.com/Miroling/InvenTree-AI/blob/60c7a2d309f325c6392718fbcef8e7e3ffc6007e/docs/research/authenticated-clients.md)
- [Provisional Obscura evaluation](https://github.com/Miroling/InvenTree-AI/blob/f7b27dfbba2d8dc5234b4361409094745404b387/docs/research/obscura-evaluation.md)
- [Measured Obscura–PinchTab comparison: tokens, site protection, component data and PDF downloads](https://github.com/Miroling/InvenTree-AI/blob/f6009c87dc4cdf0fca2279fc45f7ae1a2b9fc457/docs/research/browser-comparison.md)

## Intended connection

```text
ChatGPT in a browser ─┐
Codex ────────────────┼── MCP OAuth token ── MCP service ── user's InvenTree token ── InvenTree
Claude ───────────────┘                          │
                                  InvenTree-backed browser login
```

GitHub distributes the source, documentation, and eventual Codex package. The MCP service needs a separate runtime that can reach the selected InvenTree instance.

Docker Compose and Helm for k3s are required deployment targets. InvenTree determines access by validating each user's personal API token; a separate manual allowlist is not required. All inventory requests retain that user's upstream permissions. ChatGPT, Codex, and Claude use separate MCP OAuth credentials, not the raw InvenTree token. See [the authentication design](docs/deployment/authentication.md).

The OAuth broker, credential storage, first release's workflows, and runtime implementation are still being decided in the map. Current research starts from an existing local InvenTree proof of concept, including its intake workflows, API compatibility fixes, and review-before-write behavior. Obscura is being evaluated for component enrichment; it is not selected or bundled.

## Contributing to the decisions

Read the map, then choose an open child issue with no open blockers and no assignee. Claim it before work, cite primary sources, and keep recommendations distinct from decisions made with the owner. See [the tracker guide](docs/agents/issue-tracker.md).

Do not submit credentials, private inventory exports, local configuration files, or private service addresses. Use synthetic examples in public discussions.

## License

This repository uses the [MIT License](LICENSE). Any third-party code added later must retain its own applicable license and attribution; dependency reuse is being investigated before code is imported.
