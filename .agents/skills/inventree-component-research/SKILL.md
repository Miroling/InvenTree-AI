---
name: inventree-component-research
description: Research electronic components for InvenTree, find original manufacturer documentation, and verify seller specifications before preparing an evidence-backed Change Plan.
---

# Manufacturer-verified component research

Use this workflow for component identification, seller-listing intake, and specification enrichment. Obscura is the selected retrieval engine; do not use PinchTab. These instructions prepare evidence and a reviewable plan, not authorization to write inventory.

## Mandatory source of truth

Always search for the exact part on the original manufacturer's official website, even when the seller provides a datasheet or a plausible specification table. Here “vendor” means the original manufacturer/OEM, not the marketplace seller. Establish the manufacturer's domain from primary evidence. Preserve suffixes, package codes, and selected variants; an item URL, family name, or seller SKU is not automatically an exact manufacturer part number.

Locate and collect the official datasheet and relevant ordering/package documents. Download original files through Obscura, check the PDF signature and parseability, and record source URL, retrieval date, revision, page count and SHA-256. A one-page brief must not be mistaken for a complete datasheet. If the current product-page link is abbreviated, search the official domain for the complete document, compare revisions and expose remaining gaps. Keep downloaded documents and private sessions outside public git unless redistribution is authorized.

Use the manufacturer's applicable datasheet, ordering guide, errata and official product information as the technical authority. Record conflicts between official revisions instead of silently combining values. Seller text, marketplace photos, search snippets and third-party databases may guide discovery; they do not override manufacturer evidence. Manufacturer identity does not authenticate the physical item being sold.

For a board or module, identify its original board vendor and revision. An IC datasheet does not verify the module's regulator, connectors, wiring, supported power or thermal performance. Keep bare-IC and board-level evidence separate.

## Verify every seller claim

Inventory every accessible seller characteristic: title, selected variant, specification fields, description, and image text when available. Maintain one row per claim with:

- Seller field, exact value, source and location.
- Manufacturer value, units, conditions, applicability, document URL/revision and page/table.
- Status: `verified`, `conflicting`, `unverified`, or `seller_only`.
- Proposed catalog value and the reason for keeping, correcting or omitting it.

Verify technical claims individually, including identity, package/pins, dimensions, interfaces, voltage/current/power, temperature and features. Distinguish recommended conditions, absolute limits and typ/min/max values. Do not substitute family-wide capabilities for suffix-specific features.

A conflict remains visible; the proposed technical value follows applicable manufacturer evidence. Missing evidence stays unverified. `seller_only` covers commercial claims such as price, offered quantity, condition, authenticity and shipping: datasheets cannot establish those. Never infer stock quantity from a listing pack size or claim “new/genuine” from a manufacturer datasheet.

Report extraction coverage. If a page is blocked or only metadata is available, say which seller sections were not inspected; never claim all seller characteristics were verified. Do not turn an empty or inaccessible seller field into a verified absence.

## Obscura retrieval and plan handoff

Start with public original HTML and local metadata parsing. Render JavaScript only for missing evidence. Use explicit structured selectors/evaluation; do not assume CLI --selector limits output. Keep sessions isolated and attempts bounded. Raw original downloads do not automatically share browser cookies. Preserve an explicit partial/challenge/error result and use another manufacturer source through Obscura when appropriate.

The Change Plan contains manufacturer-backed technical values, source references, the claim ledger, missing evidence, and unresolved review items. Seller-only claims remain separate from verified catalog parameters. Changed identity, variant or evidence invalidates an earlier plan review. Do not execute writes or represent an agent flag as human approval; preserve the project's explicit Change Plan approval requirement and prohibition on automated deletions.
