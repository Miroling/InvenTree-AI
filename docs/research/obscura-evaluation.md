# Provisional Obscura assessment for component enrichment

Research date: 2026-09-05. Resolves the evidence-gathering question in [Evaluate Obscura for component enrichment](https://github.com/Miroling/InvenTree-AI/issues/12), not the browser selection.

**Identity remains unconfirmed:** this assessment concerns [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura), associated with [obscura.sh](https://obscura.sh/). The owner has not supplied the intended project's URL. Do not transfer these findings to another product named Obscura. Reviewed upstream snapshots: Obscura `a1e09de68c7617b8079fbb1661b0548c501971c1`; PinchTab `a59828d59df32381a027eb77b0dbc5f1b7dc8523`. No binaries were installed or executed, supplier sites scraped, private deployments accessed, or extraction accuracy measured.

## Findings

| Concern | Obscura candidate | PinchTab comparison |
|---|---|---|
| Runtime | Independent Rust browser with V8 and a CDP implementation. | Browser bridge/orchestrator; its Docker image includes Chromium. |
| Linux packaging | Release v0.2.2 lists x86_64 and aarch64 Linux archives, including rendering variants. Docker publishing workflow targets linux/amd64 and linux/arm64. | Release configuration builds Linux amd64/arm64 binaries. Container browser/package support must also be verified for the chosen image digest. |
| Client API | Playwright connects through `connectOverCDP`; its native `connect` protocol is different. | HTTP actions, snapshots, and screenshots; adopting Obscura requires an adapter, not merely changing a hostname. |
| License | Apache-2.0 project license. | MIT project license; preserve notices and audit packaged third-party dependencies separately. |

Sources: [Obscura runtime and license](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/README.md), [release assets](https://github.com/h4ckf0r0day/obscura/releases/tag/v0.2.2), [Docker workflow](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/.github/workflows/docker.yml), [PinchTab Dockerfile](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/Dockerfile), [release configuration](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/.goreleaser.yml), [MIT license](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/LICENSE).

**CDP is useful compatibility, not Chromium parity.** Obscura documents selectors, clicks, form filling, evaluation, waits, and request interception. However, pages share a V8 isolate, so CPU-heavy JavaScript can block other pages. Service workers, some Web APIs, long-tail CSS, media, and compositor behavior remain incomplete; storage-state persistence has limits. These differences can affect variant selectors or expandable specification tables. No evidence here establishes better supplier-page coverage. [Playwright support and limitations](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Use-with-Playwright.md).

**Visuals and text exist in both tools.** Obscura's render-enabled builds provide screenshots and raster-backed PDF export. Its MCP exposes snapshots, Markdown, structured extraction, attributes, links, clicks, scrolling, and waits. A fresh snapshot is needed after interaction because references can become stale. This provides mechanisms for opening product details and reading image URLs, but does not identify the correct component automatically. [Obscura MCP tools](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Use-the-MCP-server.md). PinchTab provides accessibility snapshots, text/selector/ref clicks, and element or full-page screenshots. [Snapshot](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/snapshot.md), [click](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/click.md), [screenshot](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/screenshot.md).

**Printing a PDF does not parse a datasheet.** Obscura's generated PDF has no selectable/searchable text; PinchTab also offers page-to-PDF export. Datasheet retrieval, bounded download, PDF text/table extraction, and scanned-document handling need a separate enrichment step. Neither export API proves datasheet understanding. [Obscura PDF limits](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Use-with-Playwright.md), [PinchTab PDF](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/pdf.md).

## Deployment and access boundary

Obscura's **CDP and HTTP MCP endpoints have no built-in authentication**. Its Origin allowlist permits clients without an Origin header; it is not user authentication. Keep the browser on an internal Compose network or a non-public Kubernetes Service. Publish only the InvenTree-AI MCP gateway, with independently validated user authorization. Neither browser establishes that a request belongs to an authorized ChatGPT, Codex, or Claude user. [Production authentication guidance](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Run-in-production-at-scale.md), [Origin rules](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Environment-variables.md).

PinchTab supports bearer tokens, feature gates, and restricted agent sessions, but explicitly does not present them as hostile multi-tenant isolation. Separate instances and network/credential boundaries remain necessary. [PinchTab security model](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/guides/security.md).

For either implementation, proposed Compose/Helm requirements are: pinned image digest; non-root worker where supported; no privileged mode; dropped capabilities; restricted writable storage; explicit CPU/memory limits; bounded job queue and concurrency; per-job deadlines; output/download size limits; separate user sessions; and egress restrictions excluding inventory services and cloud metadata. Never inject InvenTree credentials into the browser. These are design recommendations, not validated deployments.

Obscura documents navigation/script/CDP timeouts and worker counts, but its default V8 old-space ceiling is 4 GB; advertised small memory figures are not resource budgets. Its security policy says JavaScript executes in process and requires OS isolation. Architecture support makes k3s packaging plausible, not certified: verify the actual release image manifest and smoke-test rendering, shutdown, memory enforcement, and isolation on each intended architecture. [Limits](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Environment-variables.md), [isolation responsibilities](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/SECURITY.md).

## Proposed acceptance benchmark

Use the same approved public-source fixture set and extraction schema for both engines: 20–30 parts covering static pages, JavaScript tables, expandable details, variant selectors, image galleries, and PDF-only specifications. Establish human-reviewed manufacturer evidence first. Run each case three times with fixed engine, architecture, viewport, locale, deadlines, and concurrency.

| Gate | Proposed acceptance |
|---|---|
| Identity and variants | Zero accepted wrong manufacturer/MPN/package/variant; ambiguous cases explicitly unresolved. |
| Specifications | Every accepted value includes units and source evidence; zero unsupported values; report completeness separately. |
| Product images | Image corresponds to the exact product or is explicitly marked representative; reject logos, category art, tracking pixels, and unrelated variants. |
| Evidence | Preserve source URL, retrieval time, selected variant, relevant text/location, and content hash where permitted. |
| Reproducibility | All accepted identity/specification results agree across repeats; record failures and changed upstream content. |
| Operations | No cross-user state leakage, private-network access, unbounded jobs, or memory-limit violations; measure peak RSS and p50/p95 latency. |

**Conditional recommendation:** keep the browser provider replaceable. If this is the intended Obscura and it meets the quality gates with materially better measured resource use, consider it as an isolated enrichment worker. Retain Chromium/PinchTab as the comparison and possible compatibility fallback. Do not choose from marketing benchmarks or treat successful rendering as verified component data. Final identity and provider selection remain open.
