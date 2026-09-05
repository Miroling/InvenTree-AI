# PoC reuse and cloud migration assessment

Research date: 2026-09-05. Resolves [Assess reusable PoC capabilities and cloud migration gaps](https://github.com/Miroling/InvenTree-AI/issues/3). This is evidence and recommendations, not an approved architecture or release scope.

## Finding

The PoC offers useful workflow requirements, a small compatibility adapter, and an upstream MCP implementation to evaluate. It is not ready to expose directly as the public cloud service. Its current integration depends on a local process and local files; mutation approval and the no-delete rule exist in agent instructions, while executable tools still perform unrestricted dispatch to writes and deletes. Image uploads, remote file intake, authentication, operation-level authorization, and compatibility verification need explicit design before implementation. Sources: PoC `scripts/inventree-mcp-stdio.py:13–19`, `scripts/inventree_mcp_overlay.py:209–315`, `.codex/skills/inventree-change-safety/SKILL.md:18–39`; installed `inventree_mcp/tools/attachment.py:28–46`.

## Evidence boundaries and source notation

- **PoC paths** are relative to the owner's local reference repository. They are citations for maintainers with access, not public links or copied source. Inspection used the working tree based on commit `13e056626b4bfc3b67bd8f9f71fc14acf9ed4c67`.
- **Installed paths** are relative to the reference environment's Python `site-packages` directory. Package source, dependency metadata, and public upstream files were inspected without importing the actual server or settings.
- The observed overlay is locally modified and the observed test file is untracked. Findings about their latest behavior must not be attributed to the PoC commit alone. SHA-256 fingerprints: `scripts/inventree_mcp_overlay.py` = `2216efc5dd521dd76071328424c5f65e9da83909b7d223bf10a6f83928d36cee`; `tests/test_inventree_mcp_overlay.py` = `02c08b5d81fd253c1d3c4df189f4b0477807b5efbb68174936d93430af277faa`.
- No private InvenTree instance, deployment server, or inventory MCP tool was accessed. No credentials, environment values, private inventory exports, receipts, browser profiles, or generated evidence files were read. No reference files were changed. Public GitHub and upstream documentation were the only remote research sources.
- The two local tests were run in an isolated offline harness with `inventree_mcp.server` replaced before importing the overlay, so the real settings, client, and transport were never loaded. Python bytecode writes were disabled. Both tests passed; this is unit-level evidence only.

## What is implemented

### Runtime and transport

The Node launcher finds a project Python environment, combines process environment with locally loaded environment settings, and starts the Python wrapper with inherited standard input/output. That wrapper imports upstream tools, applies the overlay, and runs MCP over **stdio**. Sources: PoC `scripts/mcp/inventree.mjs:8–24`, `scripts/mcp/common.mjs:14–42`, `scripts/inventree-mcp-stdio.py:13–19`.

The installed upstream server already has an **HTTP** entry point. It constructs a FastMCP server and obtains one configured InvenTree URL/token pair through settings. The PoC's overlay is applied by its separate wrapper, not by that upstream HTTP entry point. Therefore, switching to the upstream executable would lose the local fixes unless the cloud entry point deliberately applies or incorporates them. Source: installed `inventree_mcp/server.py:5–27`; [pinned upstream server](https://github.com/munin92/inventree-mcp/blob/886e90fec7b24c78283fee7a7c7d02ddca432799/inventree_mcp/server.py).

The upstream README advertises an optional MCP bearer token. The inspected server construction and run path do not configure an authentication provider or check that token. There is no evidence here that setting the advertised variable protects this endpoint. This finding does not evaluate an external gateway; none was inspected. Sources: installed `inventree_mcp/server.py:5–27`; [upstream configuration description](https://github.com/munin92/inventree-mcp/tree/886e90fec7b24c78283fee7a7c7d02ddca432799#configuration).

The REST client sends an InvenTree token upstream, opens a new HTTP client for each request, and collects paginated responses into a complete list. Its pagination loop has no result cap and assumes the response contains `results` and `next`. There is no retry or idempotency mechanism in these methods. These are observable implementation choices, not a load or resilience test. Source: installed `inventree_mcp/client.py:6–62`.

### Operation inventory

Each tool accepts a free-form `operation` string, typically with optional identifiers and a generic `data` dictionary. The following operations are present in inspected dispatch branches. Presence means a wrapper exists; it does **not** prove compatibility with any current InvenTree instance. Source for the extended part tool: PoC `scripts/inventree_mcp_overlay.py:209–315`. Other sources are the named installed modules below.

| Tool or area | Read-oriented operations | Write, destructive, or side-effect operations | Source |
| --- | --- | --- | --- |
| `part`: parts | `list`, `get`, `search`, `suppliers`, `stock_summary`, `attachments` | `create`, `update`, `delete` | Overlay `:220–244` |
| `part`: categories | `category_list`, `category_get`, `category_parameters` | `category_create`, `category_update`, `category_delete`, `category_parameter_add`, `category_parameter_update` | Overlay `:246–270` |
| `part`: BOM | `bom_list` | `bom_add`, `bom_remove`, `bom_validate` | Overlay `:272–281` |
| `part`: parameters | `parameters`, `parameter_get`, `parameter_templates`, `parameter_template_get` | `parameter_set`, `parameter_update`, `parameter_delete`, `parameter_template_create`, `parameter_template_update` | Overlay `:283–315` |
| `stock` | `list`, `get`, `location_list`, `location_get`, `history` | `create`, `update`, `delete`, `transfer`, `count`, `add`, `remove`, `merge`, `location_create`, `location_update`, `location_delete` | `inventree_mcp/tools/stock.py:36–75` |
| `build_order` | `list`, `get` | `create`, `update`, `delete`, `issue`, `complete`, `cancel`, `allocate` | `inventree_mcp/tools/build_order.py:28–48` |
| `purchase_order` | `list`, `get`, `line_list` | `create`, `update`, `delete`, `issue`, `receive`, `complete`, `cancel`, `line_add`, `line_update` | `inventree_mcp/tools/purchase_order.py:31–57` |
| `sales_order` | `list`, `get`, `line_list`, `shipment_list` | `create`, `update`, `delete`, `issue`, `ship`, `complete`, `cancel`, `line_add`, `line_update`, `shipment_create` | `inventree_mcp/tools/sales_order.py:33–63` |
| `return_order` | `list`, `get` | `create`, `update`, `delete`, `issue`, `complete`, `cancel` | `inventree_mcp/tools/return_order.py:27–45` |
| `company` | `list`, `get`, `contacts`, `addresses`, `supplier_parts`, `manufacturer_parts` | `create`, `update`, `delete`, `contact_create`, `contact_delete`, `address_create` | `inventree_mcp/tools/company.py:34–69` |
| `attachment` | `list`, `get`, `download_url` | `upload`, `delete` | `inventree_mcp/tools/attachment.py:28–46` |
| `barcode` | `scan`, `lookup` are lookup-labelled POST requests; classify against the supported API | `assign`, `unassign` | `inventree_mcp/tools/barcode.py:24–32` |
| `label` | `list_part`, `list_stock`, `list_templates`, `get_template` | `print` | `inventree_mcp/tools/label.py:26–36` |
| `report` | `list_templates`, `get_template` | `generate` | `inventree_mcp/tools/report.py:24–30` |
| `system` | `version`, `health`, `me`, `users`, `groups`, `currencies`, `settings_global`, `settings_user` | None in inspected dispatch | `inventree_mcp/tools/system.py:24–41` |

The installed sources are available in the [pinned public tool directory](https://github.com/munin92/inventree-mcp/tree/886e90fec7b24c78283fee7a7c7d02ddca432799/inventree_mcp/tools). Some read operations expose users or settings; read access still needs a deliberate release allowlist.

Important contract differences:

- The local cheat sheet says parameter-template and category-template operations are absent, but the observed overlay adds them. It also advertises `system info`, `build_order outputs`, barcode `link`/`unlink`, and generic label/report operations that differ from actual dispatch names. Build the release inventory from source and transport discovery, not this cheat sheet. Sources: PoC `docs/mcp-inventree-tool-cheat-sheet.md:11–53`; operation table above.
- The stock-receive skill generally proposes `stock add` from a part, quantity, and location. The installed `add` wrapper instead builds an adjustment for an existing **stock item** identifier; `create` creates a new stock row. Receiving a purchase-order line is another distinct operation. The cloud contract must preserve this distinction and verify payloads. Sources: PoC `.codex/skills/inventree-stock-receive/SKILL.md:43–54`; installed `inventree_mcp/tools/stock.py:46–60`, `inventree_mcp/tools/purchase_order.py:46–47`.

### Schema adaptation worth preserving

The overlay caches the OpenAPI document and path set once per process. It chooses from known candidate collection paths, falling back to its newest known candidate when schema loading fails or no candidate is present. It is a targeted adapter, not a general API repair engine. Sources: PoC `scripts/inventree_mcp_overlay.py:39–81`.

For parameters, it supports the older part-specific paths and newer generic paths. It adapts `part` to `model_id` plus `model_type`, resolving the Part model identifier from a specific schema component/enum shape. For category-template links it maps `parameter_template` and `template` using the POST body's referenced schema. Sources: PoC `scripts/inventree_mcp_overlay.py:87–135`, `:171–206`.

The observed `parameter_set` reads existing parameters and updates an existing matching row instead of blindly creating a duplicate; it creates only when none match and rejects multiple matches. This addresses automatically created blank category parameters. It is a read-then-write sequence, so it is not atomic protection against concurrent requests. Sources: PoC `scripts/inventree_mcp_overlay.py:138–168`; `tests/test_inventree_mcp_overlay.py:71–127`.

Limitations to carry into design:

- Schema errors become an empty cached schema for the process lifetime; no refresh, TTL, instance key, or explicit unsupported-version result is present. A service serving multiple instances cannot safely share that cache unchanged.
- Only selected parameter and category-link fields are adapted. The model lookup assumes the `Parameter` component and a limited enum reference structure; other schema layouts are not comprehensively resolved.
- The overlay explicitly leaves label/report, stock-history/count, and sales-shipping drift outside its scope. Attachment model identifiers and most other endpoints remain hardcoded. Broad version support is unproven.

Sources: PoC `scripts/inventree_mcp_overlay.py:17–33`, `:39–112`, `:171–206`, `:243–244`; installed operation modules listed above. InvenTree's own [API documentation](https://docs.inventree.org/en/stable/api/) confirms that the instance supplies API documentation and that user permissions govern REST access; it does not establish compatibility of these wrappers.

### Images and attachments

The primary Part image is a real gap: `part update` calls the JSON-only `patch` method, which has no multipart argument. The enrichment skill documents downloading an image and using a direct multipart Part image update, but no dedicated image operation is implemented in the inspected overlay. A generic attachment upload does not set the Part image. Sources: PoC `scripts/inventree_mcp_overlay.py:230–233`, `.codex/skills/inventree-part-enrichment/SKILL.md:62–64`, `:84–92`; installed `inventree_mcp/client.py:53–57`.

Attachment upload does support multipart POST, but accepts a `file_path` and opens it in the **server's filesystem**, without an allowed directory check in this handler. It cannot directly consume a file on a browser user's machine or a separate chat execution environment. Its `data` parameter is unused for upload, so this handler does not implement a general external-link creation contract. Download returns the upstream attachment URL without making it independently accessible. Sources: installed `inventree_mcp/tools/attachment.py:6–46`, `inventree_mcp/client.py:43–51`.

Design implication: define an authenticated artifact intake mechanism, ownership, size/type checks, retention, and user-visible references before porting images/PDFs. Replace arbitrary host file paths with controlled artifact identifiers. If server-side URL retrieval is offered, its destination and redirect policy must be designed explicitly. These are recommendations arising from the file boundary, not capabilities already implemented.

## Documented workflows versus executable service features

The six focused skills form a useful behavior specification. They are Markdown instructions composed by an agent, not an implemented transaction engine, parser API, image-identification service, PDF renderer, or browser service.

| Skill | Reusable intent | Source |
| --- | --- | --- |
| Order intake | Normalize receipts, URLs, tables, names, or photos; match existing parts; collect ambiguities; produce one consolidated plan with optional taxonomy improvements | `.codex/skills/inventree-order-intake/SKILL.md:21–72`, `:93–103` |
| Photo intake | Extract visible identifiers and confidence; resolve identity; obtain quantity, exact variant and location; hand off to the normal intake pipeline | `.codex/skills/inventree-photo-intake/SKILL.md:20–68` |
| Part enrichment | Prefer manufacturer evidence; preserve populated fields; plan descriptions, parameters, primary images, links and detailed-page PDFs | `.codex/skills/inventree-part-enrichment/SKILL.md:19–81`, `:94–107` |
| Stock receive | Reuse or propose categories, locations and location types; preserve actual line quantities; plan receipt rows | `.codex/skills/inventree-stock-receive/SKILL.md:17–60` |
| Taxonomy | Reuse templates; order template creation before category links and values; separate optional backfill from receipt | `.codex/skills/inventree-taxonomy/SKILL.md:17–47`, `:57–75` |
| Change safety | Show current/proposed values and planned operations; require explicit approval; stop on changed facts; prohibit automated deletes | `.codex/skills/inventree-change-safety/SKILL.md:18–52` |

These skills depend on headed PinchTab browsing, local intermediate files, and durable evidence beneath the workspace. PDF creation is described as local work; no dedicated renderer appears among the inspected tracked integration scripts. The PinchTab launcher manages a loopback browser bridge, browser profiles/state/logs, native binary discovery, and a second stdio MCP process. It is infrastructure separate from InvenTree MCP. Sources: PoC `.codex/skills/inventree-order-intake/SKILL.md:74–91`, `.codex/skills/inventree-part-enrichment/SKILL.md:66–73`, `scripts/mcp/pinchtab.mjs:34–40`, `:81–135`, `:149–168`, `:183–223`.

Thus publishing the repository or moving its Python wrapper to a host does not carry over the user's browser, uploaded files, evidence directory, or automatic skill discovery. Cloud browsing and file handling must be supplied by the client or a separately designed service. This assessment does not assume either client's current packaging or file protocol; those requirements belong to the client-compatibility research.

One local browser patch adds a bearer header to any intercepted fetch whose pathname ends in `/health`, without checking the origin. If retained, narrow this behavior to the intended bridge origin; do not copy it into a general cloud fetch environment. Source: PoC `scripts/pinchtab-mcp-preload.mjs:16–43`.

## Approval and deletion behavior

The reference requirement is explicit: a consolidated Change Plan, a user reply of `APPROVE PLAN`, only the approved changes, and no automated deletion even after approval. The template includes entity identifiers and before/after fields. Sources: PoC `.codex/skills/inventree-change-safety/SKILL.md:18–39`, `docs/inventree-change-plan.md:19–45`.

The executable implementation does not validate such approval. There is no plan identifier, approved-operation ledger, caller-bound grant, expiry, replay protection, or current-state check in the inspected dispatch/client path. A tool invocation directly calls the REST client. `delete`, `category_delete`, `bom_remove`, and `parameter_delete` remain in the overlay; other upstream tools also retain deletes. Sources: PoC `scripts/inventree_mcp_overlay.py:209–315`; installed `inventree_mcp/client.py:43–62` and operation table.

This makes the current gate dependent on the agent following instructions. Exposing the same grouped `part` or `stock` tool cannot truthfully classify the entire tool as read-only. For cloud use, determine policy per operation or expose separate read/write tools, enforce the no-delete boundary in code, and choose a verifiable approval mechanism. A model-provided `approved: true` alone would merely restate the same trust problem. These are design recommendations; the human approval experience remains an open decision.

## Dependencies and provenance

| Component | Observed version or source | Evidence and reuse implication |
| --- | --- | --- |
| `inventree-mcp` | Installed `1.0.0`, Git commit `886e90fec7b24c78283fee7a7c7d02ddca432799`; requested branch `develop` | Installed `inventree_mcp-1.0.0.dist-info/direct_url.json:1`, `METADATA:2–21`. PoC `requirements.txt:1–3` tracks a moving branch, not this immutable commit. |
| Python and direct runtime dependencies | Upstream requires Python `>=3.11`, FastMCP `>=2.0.0`, httpx `>=0.27.0`, pydantic-settings `>=2.0.0` | [Pinned package metadata](https://github.com/munin92/inventree-mcp/blob/886e90fec7b24c78283fee7a7c7d02ddca432799/pyproject.toml). These broad ranges are not a reproducible dependency lock. |
| Installed Python dependency versions | FastMCP `3.4.2`, httpx `0.28.1`, pydantic-settings `2.14.1` | Respective installed distribution `METADATA:2–3`. FastMCP metadata lists Apache-2.0, httpx BSD-3-Clause, and pydantic-settings MIT. This is a focused inventory, not a full transitive license audit. |
| Browser helpers | `pinchtab 0.10.0`, `pinchtab-mcp 1.4.1` | PoC `package.json:9–12`, `package-lock.json:892–921`; lock records MIT for both and Node `>=20` for `pinchtab-mcp`. Browser binaries/dependencies were not installed or run during research. |
| Local integration scripts and six InvenTree skills | Tracked reference material, except test/improvement state noted above | No tracked LICENSE/COPYING/NOTICE file was found in the reference repository. The six inspected skill files contain no explicit license/author header. Confirm ownership and copying permission before importing their text or implementation. |

The pinned upstream `inventree-mcp` metadata and README declare MIT, but its repository tree has no LICENSE/COPYING/NOTICE file, the installed distribution does not include a license file, and GitHub's repository-license endpoint returned 404 during this inspection. This is an unresolved notice/provenance issue, not a conclusion that all reuse is forbidden. Before copying, establish the applicable full license text and attribution or choose an independently implemented adapter. Sources: [pinned upstream tree](https://github.com/munin92/inventree-mcp/tree/886e90fec7b24c78283fee7a7c7d02ddca432799), [pinned package declaration](https://github.com/munin92/inventree-mcp/blob/886e90fec7b24c78283fee7a7c7d02ddca432799/pyproject.toml).

FastMCP provides a public [Apache-2.0 license at the inspected version](https://github.com/PrefectHQ/fastmcp/blob/v3.4.2/LICENSE), and PinchTab provides a public [MIT license at the declared version](https://github.com/pinchtab/pinchtab/blob/v0.10.0/LICENSE). The browser MCP package's complete notice provenance still needs checking if it is distributed. Preserve InvenTree-AI's existing [MIT license](../../LICENSE); it does not replace third-party notices. This report copies no third-party implementation or skill text.

## Verification and remaining decisions

The two observed tests verify (1) updating an existing blank category-created parameter without a POST and (2) creating a parameter using the schema's generic Part model identifier. They exercise the fake client's recorded calls and the modified overlay, including generic filtering. Sources: PoC `tests/test_inventree_mcp_overlay.py:36–63`, `:66–127`. Both passed offline. The manual dry-run checklist is a procedure, not evidence of a completed integration run. Source: PoC `docs/dry-run-checklist.md:1–12`.

No observed local test covers old-schema routing, unavailable schema, category-link adaptation, duplicate-match rejection, concurrent upserts, transport discovery, authentication, approval bypass, deletion blocking, multipart images, artifact boundaries, or the broader operation inventory. These are useful acceptance-test areas once the corresponding scope and architecture are chosen. No test or research result here establishes live compatibility or production readiness.

The evidence is sufficient to make these human decisions without inspecting private inventory:

1. **Implementation base:** depend on a pinned upstream package, maintain a reviewed fork with notices resolved, or build a focused adapter from the documented behavior requirements.
2. **First-release operations:** choose the useful subset, including whether complete receipt/enrichment and media are required immediately. Broad purchasing, sales, manufacturing, reporting and administrative reads should not enter accidentally through upstream imports.
3. **Approval experience:** decide how an exact reviewable plan becomes an authenticated, limited authorization, how changed facts/retries are handled, and how the no-delete rule is enforced.
4. **Artifacts and browsing:** choose where product research, photo intake and PDF generation run; how browser uploads cross into the service; and how evidence remains viewable before approval.
5. **Instance and compatibility policy:** decide single-instance versus multiple-instance identity, supported InvenTree versions, schema refresh/failure behavior, and the required contract tests.
6. **Public provenance:** confirm rights to reuse local scripts/skills and resolve missing upstream notices before copying. Runtime dependency pins and a release notice inventory remain implementation prerequisites.

Hosting selection, client configuration, and authorization protocol details are deliberately left to the related research and human decision tickets.
