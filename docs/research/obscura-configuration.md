# Configure Obscura for reliable component content extraction

Research date: 2026-09-05. Owner decision: use Obscura as the browser engine; PinchTab is excluded. Earlier comparative recommendations are historical, not the selected architecture. This report describes verified upstream behavior and proposed integration settings, not an implemented production extraction service.

## Evidence and recommendation

Both upstream `main` and release tag `v0.2.2` resolved to commit `a1e09de68c7617b8079fbb1661b0548c501971c1` when inspected. There was no newer source-only configuration to recommend over that release. Links below pin that revision. The repository URL is [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura), without the trailing punctuation in the user's message.

Use a verified **render + stealth build**, a persistent **single-worker CDP process**, bounded navigation/script budgets, and component-specific structured extraction. Make success mean exact component identity plus usable evidence, rather than HTTP 200 or a large text dump. Classify challenges separately from timeouts and engine errors. Configuration can improve compatibility; it cannot guarantee access to every distributor.

The most consequential findings are documentation/source discrepancies: the upstream Dockerfile does not enable TLS stealth; raw downloads do not reuse stored cookies; CLI selectors do not scope output; and the HTTP MCP server shares one browser state across callers. These need explicit handling in our integration.

## Challenge handling: actual capability

`--stealth` with the build feature enables the wreq browser-like transport and tracker blocking. The implementation fixes the TLS/HTTP profile to **Chrome 145 on Windows**; the page runtime sets matching navigator identity. Avoid custom User-Agent overrides and profile rotation. Setting `OBSCURA_PROFILE=2` documents the matching ordinary browser profile, but does not select a different stealth TLS identity. Timezone and optional geolocation should describe the actual configured egress region; no assumed region belongs in a universal deployment default. [Stealth implementation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-net/src/wreq_client.rs#L60), [page identity](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-browser/src/page.rs#L1811), [profiles](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-browser/src/profiles.rs).

There is **no documented or source-discovered `--solve-challenge`, CAPTCHA solver, or challenge-provider configuration**. Upstream explicitly excludes Cloudflare interactive challenges, active DataDome/Akamai challenges, CAPTCHAs, and IP rate limiting from stealth's guarantees. Source includes useful compatibility fixes for challenge scripts: typed-array/CryptoKey structured cloning, frame lifecycle and message-origin handling, form submission, and string timers. Regression tests for these primitives are not evidence that complete vendor challenges pass. [Declared limits](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Configure-stealth-and-proxies.md), [Cloudflare-related primitive regression tests](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cdp/tests/structured_clone_crypto_parity.rs), [frame implementation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-js/src/frame.rs).

Use one request at a time per supplier origin, a stable session, caching, and delayed bounded retries. Honor `Retry-After`. If the page requires an interactive challenge, record that condition and try another public source for the same exact component, such as the manufacturer's product page or original datasheet. Those policies belong to our application; they are not existing Obscura flags. Do not repeatedly reload a challenge or treat challenge text as product data. This recommendation requires no additional browser engine or paid proxy service.

HTTP/SOCKS5 proxies are supported. A stable operator-provided proxy can be tested if evidence indicates an IP problem, but it does not fix unsupported Web APIs. `serve` reads `OBSCURA_PROXY` as a fallback; do not assume the same fallback is wired to every subcommand. Standard `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` are not the documented interface. Proxy URLs can appear in informational logs, so credential-bearing proxy configuration must not enter published diagnostics. [Proxy documentation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Configure-stealth-and-proxies.md), [serve wiring](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L372).

## Build and persistence corrections

| Item | Verified behavior and integration consequence |
| --- | --- |
| TLS stealth build | Upstream Dockerfile builds with `--features render`; CLI default features are empty. `--stealth` alone cannot add the missing transport feature. Build with `cargo build --release -p obscura-cli --bins --features render,stealth`, or use a verified `-stealth` release artifact. Pin the resulting image digest. |
| Flag placement | `storage_dir` is declared separately at top level and on `fetch`/`serve`; the subcommand values are the ones passed onward. Use `obscura fetch URL --storage-dir DIR`, or `obscura serve --storage-dir DIR`. The documentation's blanket statement that top-level flags apply everywhere is too broad. |
| Cookie persistence | BrowserContext loads and saves `cookies.json`. Save happens on successful CLI output and CDP persistence paths. A terminated or failed fetch is not a guaranteed persistence checkpoint. |
| localStorage persistence | Docs claim automatic localStorage persistence, but no disk load/save implementation was found in this source revision. Only cookies are confirmed. Explicitly export/import storage if needed and test that path. |
| Multiple workers | `serve --workers N` with N greater than one does not forward `storage_dir`, `max_connections`, or `allow_file_access` into child invocation. Use `--workers 1` for the persistent profile; scale separate explicitly isolated processes instead. |
| Raw original download | `--dump original` exits into a separate HTTP path before BrowserContext construction, with a fresh CookieJar. It ignores `--storage-dir`, executes no challenge JavaScript, and its stealth branch ignores custom User-Agent. It is suitable for public direct PDF/image URLs, not an implicit continuation of a browser session. |

Sources: [Docker build command](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/Dockerfile#L39), [CLI feature definitions](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/Cargo.toml), [CLI argument/worker/raw-fetch wiring](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs), [cookie save implementation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-browser/src/context.rs#L196), [worker dispatch](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L399), [documentation claim about storage](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Architecture-overview.md#storage).

## Proposed baseline and heavy-page profile

These are starting configurations, not measured optimal values for every supplier. Use the baseline first; the heavy profile is one bounded escalation for pages with incomplete rendering or execution deadlines. Raising budgets does not resolve confirmed access-denied pages.

| Setting | Baseline | Heavy page | Purpose |
| --- | --- | --- | --- |
| `OBSCURA_NAV_TIMEOUT_MS` | `30000` | `60000` | End-to-end navigation ceiling |
| `OBSCURA_SCRIPT_DEADLINE_MS` | `30000` | `45000` | Full page script phase |
| `OBSCURA_MODULE_BUDGET_MS` | `3000` | `10000` | Enhancement-module graph/evaluation |
| `OBSCURA_FETCH_TIMEOUT_MS` | `20000` | `20000` | Bound script fetch/XHR/module requests |
| `OBSCURA_CDP_COMMAND_TIMEOUT_MS` | `45000` | `75000` | Outer command budget, above navigation budget |
| `OBSCURA_NAV_CHAIN_LIMIT` | `10` | `10` | Leave redirect-chain limit bounded |
| `OBSCURA_ROTATE_PROFILE` | `0` | `0` | Stable identity |
| `OBSCURA_PROFILE` | `2` | `2` | Matches fixed stealth Windows/Chrome 145 identity |

For CDP, use `obscura serve --host 127.0.0.1 --port 9222 --workers 1 --max-connections 1 --stealth --storage-dir /data/session`. For a container sidecar, bind `0.0.0.0` only on its private network and publish no browser port. `/data/session` is a deployment placeholder for one isolated storage directory, not a shared directory for all users. Keep the client-side command timeout above the server budget and bound each whole job separately. [Supported budgets](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Environment-variables.md), [connection limit and flags](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L57).

For one-shot heavy-page diagnosis, use `fetch URL --stealth --storage-dir DIR --timeout 60 --wait-until load --wait 10 --dump markdown`. CLI `--timeout` explicitly sets the page navigation ceiling, so it must be raised as well as the environment profile. `--wait-until` is actually passed into navigation. Omitted `--wait` uses adaptive settling up to five seconds; `--wait 10` requests a fixed post-load settle. Prefer a component-specific readiness check in the CDP integration over always spending ten seconds. A separate hard process watchdog may include navigation, settle passes and grace, so a CLI timeout is not an exact total wall-clock bound. [Fetch implementation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L675).

Do not disable watchdogs or enlarge redirect limits without a diagnosed reason. The stealth transport itself has a fixed 30-second client timeout in this source; raising the outer raw-download CLI timeout does not promise a single transport request lasting longer. No supported independent transport-timeout flag was found. [Transport builder](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-net/src/wreq_client.rs#L191).

## Extract more useful evidence with fewer model tokens

1. Start with an exact manufacturer part number and manufacturer. For public unauthenticated pages, first try original bytes through Obscura and parse HTML/structured metadata locally; render only when required fields or links are absent. This avoids making successful server-rendered content depend on unrelated page scripts. Original fetch does not reuse browser cookies, so do not apply this shortcut to a session-dependent resource. Read known product URLs or public search results through Obscura; validate identity before accepting any specifications. A product family page may be useful discovery evidence but cannot silently substitute for a package-specific ordering code.
2. Prefer structured page data, specification rows and original datasheet links. In MCP, `browser_extract` supports a field-to-CSS-selector map, `selector@attribute`, and array fields ending in `[]`. Through CDP, evaluate an equivalent bounded object. Explicitly selected JSON-LD product metadata may help discovery, but must be checked against visible identity and datasheet details.
3. Preserve parameter names, raw values, units, MPN/package evidence, final source URL and retrieval time. Return only relevant fields and a compact evidence excerpt to the model; keep full raw artifacts out of routine tool responses.
4. Use readable Markdown/text for unknown layouts and diagnostics, not a full `document.body.innerText` dump by default. Markdown can still be very large; measure and limit it before returning it to a model, and retain untruncated evidence outside the model response. The CLI text renderer strips scripts/styles and several boilerplate elements. Crucially, CLI `--selector` only waits for an element and then still dumps the full document in this revision; use explicit evaluation or `browser_extract` for actual output scoping. The README correctly calls the selector a wait condition, unlike the CLI reference. `browser_extract` really uses querySelector/querySelectorAll, but reads innerText/textContent without a separate sanitizing pass: select specific leaf values or specification rows, not a root containing scripts. Attribute extraction uses getAttribute, so relative links need URL resolution by the integration.
5. Expand specification accordions or select the exact orderable variant through normal page controls when necessary, wait for the corresponding content and take fresh element references after a rerender. Do not assume scrolling alone loads all data.
6. Discover links and inspect requested asset URLs when the datasheet link is generated dynamically. `--dump assets` includes DOM resources and fetch/XHR requests, but an observed request URL is not necessarily a public reusable API contract.
7. Download original PDFs rather than printing product pages into PDFs. If a download depends on cookies, an application-controlled same-session download implementation or a validated upstream change is required; no existing automatic handoff from CDP cookies to `--dump original` has been established. Check response/body signature, content type, size and parsed content; an HTML challenge saved as `.pdf` is a failed download. Extract the relevant electrical characteristics and package tables locally, preserving page references. OCR is an additional document-processing step if a PDF has no usable text layer.

Sources: [MCP extraction implementation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-mcp/src/lib.rs#L1727), [CLI selector handling](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L904), [readable text renderer](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L1426), [extraction formats](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Extract-data.md), [Playwright-over-CDP controls](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Use-with-Playwright.md).

A minimal structured-evaluation shape is below. Selectors are illustrative and must be discovered and verified for each supplier; null fields remain missing evidence, not invented specifications. No DOM cloning or cleanup mutation is required.

```javascript
(() => {
  const text = selector => document.querySelector(selector)?.textContent?.trim() ?? null;
  const link = document.querySelector('a[data-role="datasheet"]')?.getAttribute('href');
  return {
    source_url: location.href,
    title: document.title,
    mpn: text('[data-role="manufacturer-part-number"]'),
    package: text('[data-role="package"]'),
    datasheet_url: link ? new URL(link, location.href).href : null
  };
})()
```

`browser_snapshot` and `browser_markdown` default to a 4,000-character body/text limit. This is a useful diagnostic budget, not a token count or completeness guarantee; target a section before truncating it. Model-token expenditure must be measured across the complete interaction including retries and images, rather than inferred from browser RAM or a single response length. [MCP output limits](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-mcp/src/lib.rs).

## Sessions and public MCP boundary

The upstream HTTP MCP loop creates one `BrowserState` and passes it to every connection. It provides no user authentication or tenant isolation; an Origin allowlist does not authenticate native clients. `mcp` does not wire `--storage-dir`. Do not expose this raw endpoint as the project's shared public MCP. Use the project's authenticated gateway with isolated internal Obscura processes/sessions. No InvenTree API token, OAuth credential or user inventory data belongs in browser cookies or supplier-page JavaScript. Keep private-network access and file access disabled. [HTTP shared state](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-mcp/src/http.rs#L178), [MCP command dispatch](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-cli/src/main.rs#L510), [production security](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Run-in-production-at-scale.md).

MCP storage export captures cookies and the current page origin's local/session storage. Import applies storage entries to the currently loaded page without enforcing that the saved origin matches it. Any wrapper using these methods must enforce exact origin matching, keep state private, and never return cookie exports as ordinary model-visible extraction output. Persistence across multiple origins is not automatically complete. [Storage implementation](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/crates/obscura-mcp/src/lib.rs#L1981).

## Integration work versus available configuration

Available now: render/stealth build options, CDP, cookies in a single-worker storage directory, bounded execution, structured selectors/evaluation, page controls and original-byte fetching.

Still application work: supplier queues/cache/retry policy; challenge classification; exact-MPN and package validation; evidence/schema normalization; original-file verification/PDF parsing; correct session-bound downloads when required; per-user session isolation; metrics; and the authenticated public gateway. There is no configuration-only route that implements these requirements.

## Validation observations

The coordinating task ran these bounded **local public-page** experiments on 2026-09-05 with the same Obscura 0.2.2 macOS ARM64 render/stealth binary used in the earlier pilot. No PinchTab, alternative browser engine, private service or paid proxy was used. The profiles below were diagnostic probes, not a statistically controlled optimization benchmark.

| Probe | Outcome | Consequence |
| --- | --- | --- |
| ST STM32F103C8 rendered with navigation 60 s, script 45 s, module 10 s, fetch 20 s, CLI timeout 60 s and fixed wait 10 s | Failed after 70.61 s with a navigation deadline/V8 watchdog; no rendered output | Increasing timeouts did not solve this page. A timeout setting is not a total wall-clock guarantee. |
| The same ST page through Obscura `--dump original`, then local standard-library HTML parsing | Retrieved 380,803 bytes; recovered STM32F103C8 identity, the heading's 64 KB Flash/72 MHz description, and the exact original `stm32f103c8.pdf` link | An Obscura-only non-JavaScript route rescued useful evidence from a page whose scripts failed. Raw HTML remained outside model context. |
| Microchip ATmega328P with the same heavy profile and full Markdown | Exited successfully after 28.76 s, but produced 263,254 characters / 39,012 output tokens and no original PDF URL | Longer waiting and Markdown alone did not restore the missing document links or produce compact output. |
| TI NE555 with baseline 30 s timeout, fixed 5 s wait and explicit structured JavaScript | Returned after 10.05 s: 673 output tokens, two tables (document metadata and packages/pins), and 18 document-link entries, including duplicates | Explicit selection can return compact attributable evidence. Deduplicate links and request missing electrical fields separately. This is not complete orderable-part validation. |

Token counts use tiktoken 0.14.0, `o200k_base`, on the actual returned strings. They exclude tool schemas, prompts, retries, reasoning and images. The 673-token TI response includes headings and document/package evidence, not the same fields as an entire page; do not describe the ratio to a full dump as equal-completeness savings.

Public inputs: [ST product](https://www.st.com/en/microcontrollers-microprocessors/stm32f103c8.html), [recovered ST datasheet](https://www.st.com/resource/en/datasheet/stm32f103c8.pdf), [Microchip product](https://www.microchip.com/en-us/product/ATmega328P), [TI product](https://www.ti.com/product/NE555).

The ST recovery used `obscura fetch URL --stealth --dump original --timeout 30 --output FILE --quiet`. An offline HTMLParser inspected headings, description metadata and anchor hrefs ending in PDF resources. Among four unique PDF links, only the exact product datasheet was the intended evidence; material declarations and sales terms were excluded. This was source identification, not a second PDF-content validation test.

The TI probe used an explicit evaluated object containing the source URL/title, up to 16 h1/h2 texts, up to 12 tables with 30 rows each, and up to 30 anchors whose URLs matched PDF or TI document routes. Table cells used whitespace-normalized textContent. The bounds limited this diagnostic output; production extraction must indicate truncation and paginate or narrow when a bound is reached. User-supplied JavaScript must not be interpolated into these templates.

Earlier [persistent-session distributor tests](https://github.com/Miroling/InvenTree-AI/blob/436ce913173f6399dc116f225e3266c77983fbda/docs/research/browser-comparison.md#follow-up-persistent-obscura-sessions-on-digikey-and-mouser) remain relevant measurements: DigiKey was challenge/product/challenge and Mouser denied all three visits. No new distributor challenge-success claim is made in this configuration study. The earlier recommendation to use PinchTab is superseded by the owner's Obscura-only decision, not by rewriting the measurements.

## Proposed recovery and output contract

The following are **application policies to implement**, not existing Obscura environment variables:

- For a public source, attempt original bytes once and parse locally. Render only if identity, requested fields or document links are missing. For session-dependent resources, enter the isolated session path directly instead of assuming raw fetch shares cookies.
- Allow one heavy rendering escalation for incomplete JavaScript readiness or a diagnosed execution deadline. Do not spend that escalation on a confirmed access-denied page.
- Classify `success`, `partial`, `challenge`, `rate_limited`, `authentication_required`, `timeout`, `engine_error` and `invalid_artifact` separately. HTTP 200 is insufficient. A page may contain hidden “verification successful” markup and still be a challenge; require labeled component fields or a valid source artifact.
- For transient protection, permit at most one delayed same-session retry within the job's budget. Honor Retry-After when present; if it exceeds the job budget, defer instead of retrying immediately. Persistent protection leads to another public source for the same component through Obscura, or an explicit incomplete result. Do not rotate identities on every retry.
- Start with one active navigation per supplier origin and a proposed 180-second whole-job budget. Cap each child process/command and total attempts independently. These are conservative starting limits, not measured optimal throughput.
- Return a normalized object containing the requested MPN, matched MPN/manufacturer/package, field-level value/unit/source/page evidence, missing fields, source status and truncation indicators. Set a proposed 2,000-output-token budget per ordinary result after normalization; paginate evidence or request a focused continuation rather than silently dropping required fields. Log actual output tokens and verified-field coverage separately.
- Cache original HTML/PDF/image artifacts by canonical public URL, retrieval metadata and content hash. Keep cookie jars and session-dependent responses private to their authorized session. Log neither cookies nor credential-bearing URLs.

For images, prefer original manufacturer or distributor image URLs collected from verified product-page image attributes or structured metadata. Resolve relative and lazy-loaded URLs explicitly, check MIME signature/dimensions, and distinguish an exact-part image from a representative family/package image. Save files outside routine model responses; send only identifiers and provenance unless visual inspection is needed. Screenshots help diagnose rendering but must not become a fabricated catalog photo. Image-selection accuracy was not benchmarked in this study.

For Docker Compose and k3s, the next worker artifact must use a verified render/stealth build, an internal CDP listener, an isolated writable cookie directory, and a process/session allocation policy implementing the boundaries above. Existing deployment scaffolds still contain no browser worker image or runtime adapter. This report records the configuration contract; it does not claim that a cluster deployment, localStorage persistence workaround, same-session downloader or authenticated public gateway has been implemented.
