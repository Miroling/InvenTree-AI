# AliExpress intake logic prototype

Throwaway prototype for [Prototype AliExpress component evidence and Change Plan review](https://github.com/Miroling/InvenTree-AI/issues/16). Open `index.html` directly in a browser. It has no dependencies, external assets, storage or network calls. All inventory state is synthetic; it cannot write InvenTree or authenticate a cloud MCP client.

The example is https://www.aliexpress.com/item/1005009814305006.html and the owner-selected HUSB238_002DD. The original order-list tracking query is deliberately omitted.

Observed on 2026-09-05 using Obscura 0.2.2 render/stealth: original HTML exposed the seller's Open Graph title; rendered extraction returned partial page content, not a complete SKU/specification sheet. Therefore the prototype verifies the accessible title claims only and explicitly leaves other seller sections uninspected.

Manufacturer authority: https://www.hynetek.com/2421.html. Its ordering table identifies HUSB238_002DD as DFN-10L, conflicting with the seller's QFN-10 designation. This does not establish counterfeit or physically different goods. Manufacturer technical values take precedence in the proposed plan; the conflict remains visible.

Official full datasheet: https://www.hynetek.com/uploadfiles/site/219/news/c16af076-8c40-4e8d-b126-b4f9b83e86ea.pdf — Rev. 2.5, 17 pages, 1,436,387 bytes; SHA-256 `d4dabfe5e6055ec72f14dd2f4ae8f913be80822c14d2d24f910ea4bb777c002a`. Ordering guide: page 15; family/package summary: page 1. Downloaded through Obscura and parsed with pypdf. The product page's current English datasheet link returned an abbreviated one-page Rev. 2.5 PDF, so the full official-domain document was located separately. Its name/revision alone did not establish completeness.

The HTML uses a fixed, sanitized observation snapshot. Buttons simulate workflow transitions and do not rerun the browser. “Review” records an in-memory demo acknowledgement only, not authorization for a real write. Changing the variant, evidence or synthetic inventory invalidates the current draft and review. No seller stock quantity or authenticity claim is treated as a manufacturer-verified technical fact.

Re-collect public sources with an installed Obscura binary:

```sh
python3 prototypes/aliexpress-intake/collect.py --obscura /path/to/obscura
```

This optional helper writes raw artifacts and a metadata manifest into a git-ignored `.prototype-cache` beside itself. It does not automatically replace the reviewed evidence snapshot. Re-read changed source documents before changing verified claims. Supplier images, raw HTML, cookie jars and source PDFs are not committed.
