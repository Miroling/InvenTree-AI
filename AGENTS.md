# InvenTree-AI contributor instructions

## Project stage

This project is in wayfinder planning. The canonical artifact is [Find the path to cloud InvenTree access from ChatGPT and Codex](https://github.com/Miroling/InvenTree-AI/issues/1). Resolve decisions before implementing the integration unless the owner explicitly asks to proceed with execution.

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
