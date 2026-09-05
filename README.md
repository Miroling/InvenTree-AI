# InvenTree-AI

An open-source project for connecting InvenTree to ChatGPT in a browser and to Codex through a hosted Model Context Protocol (MCP) service.

**Status: planning and research.** This repository does not yet contain a working MCP service or an installable Codex plugin. No deployment is available from this repository yet.

## Follow the plan

The canonical plan is [Find the path to cloud InvenTree access from ChatGPT and Codex](https://github.com/Miroling/InvenTree-AI/issues/1). Its child issues hold investigations and decisions; native GitHub dependencies show what can be worked on next.

Research notes are linked from their research tickets. Decisions are recorded in issue resolution comments, with a short index in the map.

## Intended connection

```text
ChatGPT in a browser ─┐
                     ├── HTTPS MCP service ── InvenTree API
Codex ───────────────┘
```

GitHub distributes the source, documentation, and eventual Codex package. The MCP service needs a separate runtime that can reach the selected InvenTree instance.

The first release's workflows, hosting, login, and packaging are being decided in the map. Current research starts from an existing local InvenTree proof of concept, including its intake workflows, API compatibility fixes, and review-before-write behavior.

## Contributing to the decisions

Read the map, then choose an open child issue with no open blockers and no assignee. Claim it before work, cite primary sources, and keep recommendations distinct from decisions made with the owner. See [the tracker guide](docs/agents/issue-tracker.md).

Do not submit credentials, private inventory exports, local configuration files, or private service addresses. Use synthetic examples in public discussions.

## License

This repository uses the [MIT License](LICENSE). Any third-party code added later must retain its own applicable license and attribution; dependency reuse is being investigated before code is imported.
