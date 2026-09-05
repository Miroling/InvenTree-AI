# InvenTree-AI contributor instructions

## Project stage

This project is in wayfinder planning with explicitly requested deployment scaffolding. The canonical artifact is [Find the path to cloud InvenTree access from ChatGPT, Codex, and Claude](https://github.com/Miroling/InvenTree-AI/issues/1). The owner has authorized Docker Compose and a Helm chart for k3s now; do not reinterpret planning as a reason to leave those artifacts unwritten. Runtime implementation, the OAuth broker library/storage, and workflow scope still require decisions.

Ask the owner questions in Ukrainian. Write all repository documentation, issue bodies, research, and code comments in English.

Required deployment targets are Docker Compose and Helm on k3s. Public inventory access must require authenticated and authorized users from ChatGPT, Codex, and Claude. Login to an AI client is not authorization to this service. Obscura is a candidate for component research, not an approved replacement for PinchTab.

The owner clarified that InvenTree determines admission: validate each user's personal InvenTree API token against the configured instance, then admit that identity to this project's MCP services. This supersedes the separate manual allowlist interpretation. Preserve that user's upstream permissions and never fall back to a shared administrative token. Use a distinct OAuth credential for AI-to-MCP access; only the separately linked InvenTree token is sent to InvenTree. A valid token grants service admission, not permission to every inventory operation. Do not require Authentik, Keycloak, or Auth0 merely to maintain another user directory; the OAuth broker mechanism still needs implementation.

Consult wayfinder, grilling, and domain-modeling for decision sessions. Consult research for evidence gathering, official OpenAI documentation for client requirements, and plugin-creator when implementing Codex packaging. Recommendations in research are not owner-approved decisions.

## Reference material and public content

Treat the owner's existing inventory PoC as read-only reference material. Inspect source and tests without launching its integrations. Never publish credentials, environment values, private inventory, receipts, private hostnames, or unrelated vendored code. Public research may cite sanitized relative paths and public upstream sources.

Do not copy third-party implementation or skills before checking provenance and applicable licenses. Preserve the existing repository license and required upstream notices.

## Remote server access

Never connect to, inspect, query, or modify any VPS, private InvenTree instance, or deployment server unless the user gives explicit permission for that specific task. Permission from earlier tasks does not carry forward. Public documentation and the GitHub repository are available for this planning effort.

## Inventory behavior

Preserve the reference workflow's requirement for a reviewable Change Plan and explicit approval before inventory writes. Automated flows must not delete inventory data. Planning and code changes do not authorize production inventory operations.

## Collaboration

Issues live on GitHub. Follow [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md) for map, sub-issue, dependency, claiming, and resolution operations. Refer to issues by linked titles in human-facing text.

Use independent research agents for wayfinder research tickets. Each should use its own `research/<topic>` branch and worktree. Keep findings in a single Markdown file per research ticket, and leave implementation unchanged.

Keep `CONTEXT.md` as a domain glossary. Decision detail belongs in its issue resolution, with an ADR only when a hard-to-reverse trade-off warrants one.
