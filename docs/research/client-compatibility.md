# ChatGPT and Codex remote MCP compatibility

Research date: 2026-09-05. Resolves [Verify ChatGPT and Codex remote MCP connection requirements](https://github.com/Miroling/InvenTree-AI/issues/2). This is documentation research, not a deployment, compatibility test, or owner-approved architecture decision. No private InvenTree instance or deployment server was accessed.

## Main finding

The integration needs a running MCP service plus client-specific connection and distribution instructions. Publishing its source to GitHub does not register a ChatGPT connection or deploy the service. Current documentation supports a shared ChatGPT/Codex plugin format, but direct MCP declarations in a GitHub-imported workspace plugin are **desktop-only, including HTTPS servers**. Browser use needs a registered app connection or a publicly published plugin. A generic self-hosted deployment cannot assume arbitrary endpoint entry during public-plugin installation. These distinctions follow the official [packaging guide](https://developers.openai.com/plugins/build/plugins), [workspace import rules](https://learn.chatgpt.com/docs/enterprise/plugin-management), and [submission rules](https://developers.openai.com/plugins/deploy/submission).

## Supported surfaces and minimum setup

| Surface | Established path | Setup and boundary |
| --- | --- | --- |
| ChatGPT web, developer mode | Remote MCP tools, reads and writes; SSE or streaming HTTP; OAuth, no authentication, or mixed authentication. | Enable Developer mode under Settings → Security and login; create a connection using the plus button in Plugins; supply the endpoint and OAuth configuration; select the connection in a conversation. Eligibility lists Plus, Pro, Business, Enterprise, and Education; workspace policy can restrict access. |
| Local Codex host: desktop, CLI, IDE | STDIO or Streamable HTTP; HTTP bearer tokens and OAuth are supported. | Configure the URL in the MCP settings or host `config.toml`, then authenticate. These local clients share host configuration. This does not configure ChatGPT web. |
| ChatGPT Chat and hosted Work | Installed plugins can provide remote MCP tools and skills. | Install an available plugin and authenticate its connection. Workspace permissions still apply. This documents hosted Work capability, not automatic import of local Codex settings. |
| Codex plugin use | Desktop and CLI can install plugins; the IDE extension does not currently support plugins. | Install from the supported directory/marketplace, then begin a new session. Direct MCP configuration remains available in the IDE independently of plugins. |
| Other “Codex cloud” execution | The retrieved documentation does not establish a universal route for arbitrary repository MCP configuration or local plugins to transfer into every cloud execution environment. | Name the exact target product/environment and test it separately. Neither local Codex remote-MCP support nor hosted Work support proves that transfer. |

Sources: [developer mode](https://developers.openai.com/api/docs/guides/developer-mode), [MCP by surface](https://learn.chatgpt.com/docs/extend/mcp), [plugins by surface](https://learn.chatgpt.com/docs/plugins), and [connection testing](https://developers.openai.com/plugins/deploy/connect-chatgpt). The last row is a research gap, not a claim that cloud MCP is unsupported.

Developer-mode tools do not need to be named `search` and `fetch`. Server-wide workflows can use initialization `instructions`; keep the first 512 characters independently useful. Tool descriptions, schemas, annotations, and instructions can be refreshed in connection settings. [Developer-mode guidance](https://developers.openai.com/api/docs/guides/developer-mode).

## Authentication contract

For inventory data, treat the MCP-facing identity and downstream InvenTree credential as different roles. ChatGPT's supported static credentials identify an **OAuth client**; they are not a documented arbitrary API-key field. ChatGPT cannot present custom API keys or use machine-to-machine OAuth grants. A raw InvenTree token therefore does not by itself implement browser authentication. [Authentication](https://developers.openai.com/plugins/build/auth).

The documented OAuth contract includes:

- HTTPS protected-resource metadata with the canonical resource and authorization-server issuer; a discoverable `WWW-Authenticate` challenge.
- Authorization-server OAuth/OIDC discovery, authorization-code flow with PKCE `S256`, and audience/resource binding.
- CIMD, DCR, or a pre-registered OAuth client. ChatGPT CIMD supports `none` or `private_key_jwt` token-endpoint authentication.
- Server-side token verification: issuer, audience, expiry, scopes, and application permissions.
- Exact registered redirects. Stable versus callback-specific redirects depend on issuer-identification metadata and responses; copy the client's displayed redirect rather than hard-coding a remembered one.
- For tool-level linking: `securitySchemes`, resource metadata, and runtime `_meta["mcp/www_authenticate"]` challenges.

These are summarized requirements, not a complete authentication implementation. The official guide recommends an established identity provider. [OAuth requirements and linking behavior](https://developers.openai.com/plugins/build/auth).

Codex HTTP configuration separately supports environment-sourced bearer tokens and headers. Its OAuth registration supports CIMD/DCR and configured clients; automatic CIMD selection requires advertised support, `none`, and a compatible loopback callback. Custom callback arrangements may require DCR or a pre-registered client. Configure and test the exact callbacks displayed by Codex. `auth = "chatgpt"` is for trusted first-party origins, not a generic InvenTree login mechanism. [Codex MCP authentication](https://learn.chatgpt.com/docs/extend/mcp).

## GitHub distribution and browser installation

The public repository can carry server source, deployment recipes, sanitized configuration templates, documentation, skills, a `.codex-plugin/plugin.json` manifest, and a `.agents/plugins/marketplace.json` catalog. The manifest can reference `skills/`, bundled servers through `.mcp.json`, or registered app mappings through `.app.json`. Local/repository marketplaces and the universal public directory are separate distribution paths. Codex can add a GitHub marketplace using `codex plugin marketplace add owner/repo`; that command does not publish it to the public directory. [Package your plugin](https://developers.openai.com/plugins/build/plugins).

Workspace admins have a browser path: Admin → Plugins → Add → Import marketplace, entering a GitHub repository URL and optional revision. The importer supports `.agents/plugins/marketplace.json`, native `.codex-plugin/plugin.json`, and repository-relative plugin paths. GitHub authentication and workspace administration are required. [Workspace marketplace import](https://learn.chatgpt.com/docs/enterprise/plugin-management).

For that import path:

- `.mcp.json`, `mcp.json`, or inline MCP declarations make the plugin desktop-only, even with a remote HTTPS URL.
- `.app.json` instead references an **existing** app. Supported ID prefixes are `asdk_app_`, `connector_`, and `templated_apps_`; a browser URL's `plugin_asdk_app_…` corresponds to the underlying `asdk_app_…` ID.
- The mapping neither creates a connection nor grants access. Admins enable the app; users authenticate it. Repository install/auth policies do not replace workspace policies.

Consequently, one generic public repository cannot presume every user's independently deployed instance already has the same registered app ID. [Imported plugin restrictions and app mappings](https://learn.chatgpt.com/docs/enterprise/plugin-management).

For public-directory distribution, submit the actual hosted MCP endpoint for review. A registered integration reference is insufficient. The usual endpoint type is **Universal**, one fixed URL. **Template** URLs are restricted to OpenAI-approved trusted developers and configured by workspace admins; they are not a generally available arbitrary self-hosted URL installer. Public review also requires a verified publisher, domain control, accurate annotations, test cases, and authentication/test materials. [Public submission](https://developers.openai.com/plugins/deploy/submission).

No shared production endpoint, approved template arrangement, or workspace app registration has been established by this research.

## Packaging compatibility and portable workflow instructions

The official universal manifest entry point is `.codex-plugin/plugin.json`. Public documentation permits optional component references and lifecycle hooks. The inspected local `plugin-creator` materials are narrower: `scripts/validate_plugin.py` requires richer publisher/interface metadata, rejects the top-level `hooks` field, accepts only the `mcpServers` wrapper in `.mcp.json`, and rejects `.app.json` entry fields other than `id` and `category`. Current workspace documentation demonstrates an additional `required` field, while public packaging documentation also shows other MCP wrapper forms. Local validation success therefore cannot certify every documented hosted import form; local validation failure may reflect a version mismatch. Evidence: the installed skill's `SKILL.md`, `references/plugin-json-spec.md`, and validator inspected on the research date; no local absolute paths or copied implementation are published here. Compare [universal packaging](https://developers.openai.com/plugins/build/plugins) and [workspace app format](https://learn.chatgpt.com/docs/enterprise/plugin-management).

Skills can package reusable workflows for ChatGPT and Codex. Use platform-neutral instructions and bundled relative references. A remote MCP connection alone does not imply that a client's repository files or installed local skills become available on another surface; test the installed bundle. Put essential cross-tool guidance in MCP instructions and enforce access rules in the server. [Skills and plugins](https://learn.chatgpt.com/docs/skills-and-plugins), [MCP instructions](https://learn.chatgpt.com/docs/extend/mcp), and [complete plugin testing](https://developers.openai.com/plugins/deploy/connect-chatgpt).

## Approvals and inventory behavior

ChatGPT uses `readOnlyHint`; an omitted hint is treated as a write. Writes require confirmation by default, but users can remember an approval for the conversation. Codex also exposes server/per-tool approval policies. Client prompts therefore do not establish an invariant that every inventory change received a fresh, specific approval. [ChatGPT confirmations](https://developers.openai.com/api/docs/guides/developer-mode) and [Codex tool policies](https://learn.chatgpt.com/docs/extend/mcp).

Annotations must reflect actual capability. A tool combining reads and writes cannot claim it is read-only merely because some operations read. Annotations do not replace server authorization, validation, or confirmation. [Tool annotations](https://developers.openai.com/plugins/build/mcp-server#tool-annotations-and-elicitation).

Project constraint: preserve a reviewable Change Plan and explicit approval before inventory writes; automated flows must not delete inventory. Recommendation: design the workflow and server checks around this constraint, rather than relying solely on prose or client confirmation defaults. The precise approval mechanism remains a decision ticket.

## Hosting alternative relevant to connection setup

Secure MCP Tunnel offers private developer-mode connectivity without public inbound access. An always-running `tunnel-client` may run on a VM, Kubernetes deployment, or another host that reaches the private MCP over STDIO/HTTP and makes outbound HTTPS requests to OpenAI. It requires a tunnel ID, runtime API key, appropriate Platform tunnel permissions, and the correct workspace/organization associations. Browser setup selects Tunnel and its ID. The authorization server is not automatically tunneled. This option does **not** satisfy public plugin submission/distribution, which still requires stable public HTTPS. Hosting location and operational costs remain separate decisions. [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

## Recommendations, remaining decisions, and acceptance checks

Recommended starting contract, pending owner decisions: Streamable HTTP plus OAuth for the shared service; manual ChatGPT developer-mode URL/OAuth setup for each generic self-hosted deployment; a separate local Codex connection/package path. Compare Secure MCP Tunnel for private personal use. Consider workspace `.app.json` distribution or public-directory publication only after the corresponding registration and endpoint model are chosen.

The owner still needs to decide the target surfaces/account/workspace, personal versus team/public distribution, self-hosted versus a shared service, identity provider and registration method, and how approved Change Plans are enforced. Hosting options should be compared before selection.

Before claiming compatibility, test against synthetic inventory and a disposable authenticated deployment:

1. ChatGPT browser discovery, OAuth login/refresh/revocation, correct tool listing, read calls, and write confirmation behavior; include denied/missing/expired scopes and remembered approval.
2. Local Codex desktop/CLI HTTP login and calls, then IDE direct MCP separately; verify actual versions and callback metadata.
3. Hosted Work after plugin installation, independently of local configuration. Test any additional named cloud environment separately.
4. Package/import the exact intended artifact: browser app mapping, local MCP declaration, or public submission. Confirm self-host endpoint and app-ID setup is explicit and contains no shared credentials.
5. Enforce rejection of unapproved, altered, stale, replayed, or cross-user Change Plans and all automated delete requests. Confirm malformed requests have no side effects.
6. Verify installed skill activation, tool sequencing, sanitized errors, metadata refresh, and service restart/reconnect behavior.

These checks are not completed. They are the evidence needed before the README can promise browser-ready operation.
