# Issue tracker: GitHub

The tracker is `Miroling/InvenTree-AI`. Use `gh` with an explicit `--repo Miroling/InvenTree-AI` when working from another checkout. Use body files for multiline issue descriptions and comments.

## Wayfinding operations

- Map: one issue labelled `wayfinder:map`, containing Destination, Notes, Decisions so far, Not yet specified, and Out of scope. It is the canonical index, not a duplicate store for decision details.
- Child ticket: create an issue labelled `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, or `wayfinder:task`, then attach it through `POST repos/Miroling/InvenTree-AI/issues/{map_number}/sub_issues` with the child's numeric database ID as `sub_issue_id`.
- Dependencies: after all relevant issues exist, add each blocker with `POST repos/Miroling/InvenTree-AI/issues/{child_number}/dependencies/blocked_by`, passing the blocker's numeric database ID as `issue_id`. Issue numbers and GraphQL node IDs are not database IDs.
- Frontier: fetch the map's sub-issues in their native order; take open children with no assignee and `issue_dependencies_summary.blocked_by` equal to zero. The dependency count is the number of open blockers. Inspect dependencies when resolving ambiguous data.
- Claim before work: `gh issue edit <number> --repo Miroling/InvenTree-AI --add-assignee @me`.
- Resolve: publish the answer as a resolution comment, link any assets, close the issue, and append a linked one-line gist to the map's Decisions so far. Keep the full answer in the ticket only.
- Research: use a `research/<topic>` branch with a Markdown evidence note; link an immutable commit URL from the resolution comment. Never publish secrets or raw private reference data.
- Human decisions: do not close grilling or prototype tickets using an agent's assumed answers. Charting may resolve research tickets, but does not resolve human decision tickets.
- Concurrent sessions: re-fetch the map immediately before updating its index and preserve other sessions' changes. Prefer one coordinating writer for the index.

GitHub's native sub-issues and dependencies are enabled for this repository. Body-only dependency conventions are unnecessary.

See GitHub's official [sub-issue API](https://docs.github.com/en/rest/issues/sub-issues) and [issue dependency API](https://docs.github.com/en/rest/issues/issue-dependencies).
