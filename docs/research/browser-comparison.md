# Obscura versus PinchTab for component research

Research date: 2026-09-05. This report separates upstream evidence from the project's practical measurements. It evaluates three outcomes: fewer model tokens, fewer blocked requests, and more correct, relevant component information.

## Source-based assessment

**Recommendation after the local pilot:** retain PinchTab as the primary interactive browser; use a separate original-file downloader, with Obscura as a tested candidate for that role. Do not replace PinchTab wholesale with Obscura. PinchTab has more explicit controls for reducing agent interaction output; Obscura has promising first-party scraping results, but those do not establish lower token cost or better electronics data. Neither is an electronics search index or a component identity validator. This is an engineering recommendation, not an owner-approved provider decision. The source claims below and the bounded local measurements below have different evidentiary limits.

| Criterion | PinchTab | Obscura | Evidence-based conclusion before the pilot |
|---|---|---|---|
| Model tokens | Compact, scoped and differential snapshots; action plus snapshot; focused text reads | Text, Markdown, selector extraction and JavaScript evaluation; bounded snapshot text | PinchTab offers clearer native interaction-budget controls. Actual tokens per correct component remain unmeasured. |
| Site blocking | Chromium with stealth overlays; optional separately installed CloakBrowser | Independent V8/DOM engine; optional stealth transport and fingerprint controls | No comparable electronics-domain block-rate study was found. A provider label cannot predict a cloud IP's result. |
| Relevant data | Chromium compatibility and structured browser reads | Structured DOM reads with evolving Web API compatibility | Source selection, exact MPN matching, package/variant checks and extraction design determine relevance. Missing fields must count against a smaller output. |
| Datasheet acquisition | Session-aware download endpoint; PDF generation is a different operation | Binary-safe original-response download; PDF generation is a different operation | Preserve the manufacturer's original datasheet; extract only relevant pages/tables outside the browser. |

### What the token evidence actually says

PinchTab's snapshot interface supports compact/text/JSON/YAML, element scoping, depth limits and diffs. Its `maxTokens` budget is based on **four bytes per estimated token**, not the tokenizer of ChatGPT or Claude. The project's 40-node example reports roughly five times more bytes for JSON than compact output. This supports choosing compact output within PinchTab; it does not compare engines. [Snapshot reference](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/snapshot.md).

PinchTab publishes actual agent-loop usage against **agent-browser**, reporting 17.9–26.2% fewer tokens across its measured suites. The benchmark covers local fixtures, uses small samples, and includes tailored partial skills. It explicitly acknowledges task-suite bias and substantial variance. These numbers must never be relabeled as savings against Obscura. [Benchmark methodology and caveats](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/benchmark.md).

Obscura's MCP supports a snapshot character limit, Markdown, links, structured extraction, search and JavaScript evaluation. Those enable a compact application-specific result, but its documented RAM/startup advantages are not model-token measurements. [MCP reading tools](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/docs/Use-the-MCP-server.md).

PinchTab defaults to Readability extraction and falls back to raw text when coverage is too low. Its own documentation recommends raw reads for grids and other UI-heavy pages. Component specifications should therefore use a known table selector or raw text with field validation; a short article heuristic output may omit useful values. [Text reference](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/text.md).

### What the blocking evidence actually says

Obscura's first-party benchmark reports 94/98 rendered pages versus 85/98 for headless Chrome. The recorded full pass is dated 2026-07-03 at engine commit `b5039a8`, and the report describes an older engine without rendering. It is not a comparison with PinchTab, does not measure component accuracy, and combines outcomes affected by website blocking and engine behavior. Its cold-process RAM/speed tests also explicitly disadvantage Chrome relative to persistent browser reuse. [Benchmark report](https://github.com/h4ckf0r0day/obscura-benchmark/blob/6ebac8293d7477f59e837768bfd4e74173f04f1c/README.md).

The benchmark's published URL corpus covers general news, retail, travel, developer and reference sites; it does not contain TI, ST, Microchip, DigiKey, Mouser or LCSC component pages. It warns that datacenter blocking may affect every engine. [Corpus and methodology notes](https://github.com/h4ckf0r0day/obscura-benchmark/blob/6ebac8293d7477f59e837768bfd4e74173f04f1c/realworld/sites.txt).

PinchTab's stealth history records Chrome/Cloak fingerprint divergences on detector sites, rather than successful electronics retrieval rates. Its Cloak integration is optional and is not bundled in normal release artifacts; its documentation also warns that detection results change with browser, detector and site updates. A comparison must identify the actual browser provider, rather than calling every configuration simply “PinchTab.” [Stealth history](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/tests/stealth-score/history.md), [Cloak integration](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/guides/cloakbrowser.md).

### Downloads and relevance

Obscura supports binary-safe `fetch --dump original`, while its page-to-PDF feature produces a rendered document. Its current README documents evolving Web API/CSS coverage, so successful navigation alone is insufficient evidence of complete specifications. Stealth requires both a stealth-capable build and the runtime flag. The v0.2.2 release includes macOS ARM64 rendering-and-stealth and no-render-and-stealth archives. [Engine interface and limitations](https://github.com/h4ckf0r0day/obscura/blob/a1e09de68c7617b8079fbb1661b0548c501971c1/README.md), [Release assets](https://github.com/h4ckf0r0day/obscura/releases/tag/v0.2.2).

PinchTab's download handler retrieves a resource using the browser session and enforces download/domain policy. Its separate PDF endpoint prints the current page; this is not a substitute for downloading a datasheet. [Download handler](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/internal/handlers/download.go), [PDF reference](https://github.com/pinchtab/pinchtab/blob/a59828d59df32381a027eb77b0dbc5f1b7dc8523/docs/reference/pdf.md).

Recommended pipeline, based on the task requirements: exact MPN search → manufacturer's product page and original datasheet → authorized distributor evidence for packaging, availability and images → normalized fields with units and source references. Keep browser output outside model context until it has been filtered to the requested fields. Cache source artifacts and repeated lookups. Treat family-level values, alternative variants and representative images explicitly. These are proposed application behaviors, not capabilities automatically supplied by either engine.

## Practical measurement protocol

Use the same public URLs, network connection, clean profiles, locale, deadlines and low request rate. Record binary versions and actual browser provider. Separate explicit denial/challenge, transport failure, timeout, engine failure, empty extraction and correct retrieval. Do not count a short challenge page as a token-saving success.

Measure both raw text and a shared normalized component schema. Count returned text with a named tokenizer and label it **tool-output tokens**, not full agent expenditure. Compare only equally complete answers; score exact MPN, manufacturer, package, critical parameters and original datasheet URL against human-checked manufacturer evidence. Count wrong-variant values as errors, not partial credit. Repeated runs and a larger part sample are required before predicting cloud performance.

Comparable raw-text commands:

```text
Obscura: obscura fetch URL --eval 'document.body.innerText' --timeout 30 --quiet
PinchTab: navigate to URL, then GET /text?mode=raw&format=text
```

A paired raw-text read isolates retrieval completeness but does not exercise each tool's best agent workflow. A later end-to-end benchmark must use the same tasks and models, include all calls/retries and cached-input accounting, and score correctness before cost.

## Practical measurements

### Scope and reproducibility

A local pilot ran on 2026-09-05, using macOS ARM64 and the same outbound connection. Six public product URLs were visited twice by each engine (24 measured navigations). Engine order alternated between sites and rounds. These are **known-URL retrieval tests**, not search-engine ranking or complete autonomous research tasks. No private server, inventory, deployment or user browser profile was accessed.

- Obscura **0.2.2**, macOS ARM64 rendering-and-stealth release, with runtime `--stealth` enabled. Release archive SHA-256: `ae462d3518f5683464a53d00d1703effc57e128faba6706a82ec6033348eddd8`.
- PinchTab **0.15.2**, macOS ARM64 release, with **Chrome for Testing 151.0.7922.34**, `stealthLevel: full`, headless, no CloakBrowser and no automatic challenge solver. PinchTab binary SHA-256: `304201bae3528024e2dc32e59391fc7bebd38ad3f8206df91ef876299c7b989c`, matching the published release checksum.
- PinchTab used a dedicated temporary profile and state directory, authenticated control API on loopback, and a website allowlist. Its profile persisted across visits; Obscura started a fresh process without persisted storage for each visit. PinchTab had a TI preflight visit. There were no supplied site credentials, proxies or CAPTCHA-solving services. Cookies/profile persistence and engine viewport/locale defaults were **not fully matched**; this is an operational pilot, not a randomized controlled benchmark.
- Navigation deadline: 30 seconds; post-navigation wait: 5 seconds. Obscura had a 50-second outer process deadline; PinchTab HTTP calls had a 40-second outer deadline. Obscura's ST process returned after about 38 seconds with a navigation-deadline error. Fixed settling can miss later content.
- Both executed the same JavaScript expression: `({title:document.title,url:location.href,text:document.body?document.body.innerText:'',links:Array.from(document.querySelectorAll('a[href]')).map(a=>({text:a.innerText,url:a.href}))})`. PinchTab used `/navigate` and `/evaluate` with the returned tab ID; Obscura used `fetch URL --eval EXPRESSION --wait 5 --timeout 30 --quiet --stealth`.
- PinchTab also returned `/text?tabId=ID&format=text` and `/snapshot?tabId=ID&format=compact&filter=interactive`. A supplementary **single pass** measured Obscura `fetch URL --dump text --wait 5 --timeout 30 --quiet --stealth` on TI, Microchip and Adafruit. It was a separate navigation, not the identical DOM snapshot.
- Counts use **tiktoken 0.14.0, `o200k_base`**, with no special-token interpretation. They count the returned text strings only, excluding JSON envelopes, links, tool schemas, prompts, reasoning, retries and images. They are not billable ChatGPT/Codex/Claude totals; Claude and other models may tokenize differently.

### Retrieval and useful information

| Public target | PinchTab, both rounds | Obscura, both rounds | Relevance observation |
|---|---|---|---|
| [TI NE555](https://www.ti.com/product/NE555) | Useful family data and original datasheet links | Useful family data and original datasheet links | PinchTab visible text includes timer identity, typical 2 mA current, temperature range and package list; additional parameters require a tab or datasheet. Neither read alone validates every orderable suffix. |
| [ST STM32F103C8](https://www.st.com/en/microcontrollers-microprocessors/stm32f103c8.html) | Useful family data and original datasheet links | Navigation timeout with script/watchdog errors | PinchTab retrieves the C8 heading with 64 KB Flash and 72 MHz. The same page also has family text mentioning 64/128 KB: taking 128 KB as this C8 part's value would be an extraction error. |
| [DigiKey NE555P](https://www.digikey.com/en/products/detail/texas-instruments/NE555P/277057) | Part-specific attributes and original TI datasheet link in direct DOM text | Cloudflare challenge page | PinchTab provides exact NE555P, Texas Instruments, 8-PDIP, 4.5–16 V and 10 mA. Its Readability and compact interactive outputs show the cookie dialog instead of those attributes. |
| [Mouser NE555P](https://www.mouser.com/en/ProductDetail/Texas-Instruments/NE555P?qs=rkhjVJ6%2F3EIf4CWgjIKuKQ%3D%3D) | Challenge/denial; no useful part data | Explicit access denial; no useful part data | PinchTab's first empty-text result contains a DataDome Device Check iframe; its second explicitly says access denied. The first is not a successful zero-token read. |
| [Microchip ATmega328P](https://www.microchip.com/en-us/product/ATmega328P) | Parametrics, original PDF links and orderable variant/package rows | Basic parametrics; only a documentation anchor, no original PDF links found | Both expose 32 KB program memory, 2048 bytes RAM and 1024 bytes EEPROM. PinchTab also distinguishes the 28-pin SPDIP PU from 32-pin variants. Obscura's native text includes an unsupported-browser message. |
| [Adafruit BME280 board](https://www.adafruit.com/product/2652) | Useful board description and tutorial link | Useful board description and tutorial link | Both expose I2C/SPI and board-level regulator/logic information. This is an Adafruit breakout, not the bare Bosch IC; neither links the original sensor datasheet directly on this first product page. |

**Useful product content:** PinchTab 5/6 sites in each round (10/12 visits); Obscura 3/6 (6/12). This means useful content was present, not that every requested component field was complete or correct. **Explicit protection:** PinchTab 1/6 sites; Obscura 2/6. Obscura's additional ST timeout is a technical failure, not proven blocking. These correlated visits from one connection do not estimate a general cloud block rate.

### Tokens and completeness must be read together

| Successful site | PinchTab direct DOM text, two rounds | Obscura native `--dump text`, one supplementary pass | Interpretation |
|---|---:|---:|---|
| TI | 322 / 322 | 1,629 | PinchTab is smaller here, but Obscura includes additional features and operating-voltage/output-drive descriptions absent from that visible read. The outputs are not equally complete. |
| Microchip | 1,555 / 1,551 | 1,418 | Obscura is slightly smaller, but misses original PDF links and orderable variant data. |
| Adafruit | 1,258 / 1,275 | 1,963 | Both contain useful product descriptions; output includes different navigation/hidden content. |

These numbers **do not establish a universal token-cost winner**, because extraction formats and completeness differ. PinchTab's other successful direct reads were ST **1,088 / 1,088** and DigiKey **1,562 / 1,562** tokens; Obscura did not retrieve corresponding useful pages under the protocol.

Two important counterexamples prevent misleading optimization:

- PinchTab's default Readability returned **76 tokens** on TI, mostly a forum disclaimer, and **79 tokens** on DigiKey, mostly cookie consent. It omitted relevant specifications. On ST it instead returned **175,449 tokens**, versus 1,088 for direct visible text. Therefore default Readability is unsuitable as the only component extractor.
- Obscura's `document.body.innerText` returned **38,507 tokens** on TI and **95,950** on Microchip, including scripts/styles. Its dedicated text dump reduced those to 1,629 and 1,418. Therefore the huge direct-DOM counts must not be presented as Obscura's best native token efficiency.

Return a bounded, validated record of requested fields and evidence rather than full page output. A missing field should trigger a focused read or source fallback, not be silently rewarded as lower cost. No full agent-loop tokens or model-generated normalization accuracy were measured.

### Original datasheet downloads

A separate single-pass test requested the three links below. Obscura used `fetch URL --dump original --timeout 30 --quiet --stealth --output FILE`. PinchTab used its authenticated `/download?url=URL&raw=true` endpoint, without an explicit tab ID. Files stayed outside model context. A plain Python `urllib.request.urlopen(URL, timeout=35)` baseline was also tried, without added headers or cookies.

| Original source | Obscura | PinchTab with Chrome 151 | Plain HTTP baseline |
|---|---|---|---|
| [TI NE555](https://www.ti.com/lit/gpn/NE555) | Valid PDF, 2,259,343 bytes, 39 pages | 536-byte Chrome PDF-viewer HTML, despite `application/pdf` response type | Identical PDF to Obscura |
| [ST STM32F103C8](https://www.st.com/resource/en/datasheet/stm32f103c8.pdf) | Valid PDF, 1,965,230 bytes, 114 pages | 536-byte Chrome PDF-viewer HTML, despite `application/pdf` response type | Read timeout |
| [Microchip AVR family DS40002061B](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf) | Valid PDF, 33,319,446 bytes, 653 pages | Client timed out after 40 seconds | Identical PDF to Obscura |

The PDF results were checked using the `%PDF-` signature and **pypdf 6.17.0** parsing. Cover text identifies TI NE555, ST STM32F103 and Microchip's grouped `ATmega48A/PA/88A/PA/168A/PA/328/P` family. A naive search for the contiguous string `ATmega328` missed that last cover: family-aware identity checking is necessary. Some font-encoding warnings occurred while extracting PDF text; no full-document extraction-accuracy claim is made.

SHA-256 of the valid files:

- TI: `c6f5275b8c31eb1d65e30400e38357aefe95e2088286bbded5afc216f4259ee9`.
- ST: `1e54ce18e6c34c5b4a78986f26e245e143748c721009fc9af5953795c30686bc`.
- Microchip: `b9b9d83cda56a95d999ea8d54fe5a540748ae9020e5e7ae19b913d384ba9320e`.

The PinchTab result is specific to the tested release/browser/download route; it does not mean Chromium can never download PDFs. Its default 20 MiB download ceiling was unchanged, and the Microchip document exceeds it, so that timeout cannot be interpreted as an intrinsic engine size limit or website block. The raw Obscura and plain HTTP routes had no matching size cap. The smaller TI/ST HTML-wrapper failures are independent of that cap. No retry or alternative Chrome provider was benchmarked. Validate file signatures and parsing rather than trusting the extension or MIME header.

### Recommended project direction

1. Use **PinchTab for dynamic product pages and interaction**, with site-specific selectors or bounded direct reads plus required-field checks. In this pilot it recovered more useful pages and better linked/variant evidence.
2. Use a **separate original-file download path**. Plain HTTP can be attempted first where it works; Obscura's raw downloader is a promising fallback and successfully retrieved all three PDFs here. The tested PinchTab download endpoint needs correction or another verified route before use for datasheet ingestion.
3. Keep **Obscura as an optional adapter**, especially for raw resource fetching and later tests of static pages. Its current results do not justify replacing the interactive browser wholesale.
4. Normalize MPN, manufacturer, exact package, requested electrical parameters, source URL, document revision and page/table references before returning data to the model. Cache original files and parsed evidence. Preserve unknown/ambiguous fields instead of mixing family variants.
5. Before promising cloud reliability, repeat on the intended deployment egress with task-specific authorization and a larger representative component set. Test exact-part matching, images, search ranking, challenge handling and total agent-loop cost there. This research does not authorize server access or select a production provider.

Raw pages, browser profiles, local control credentials and copyrighted source PDFs are not published with this note. The methods, public URLs, versions, measurements and artifact hashes above are the public reproduction record.
