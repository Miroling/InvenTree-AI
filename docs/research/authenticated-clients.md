# Authenticated public MCP: interoperability contract

Research date: 2026-09-05. Resolves [Verify authenticated MCP access for ChatGPT, Codex, and Claude](https://github.com/Miroling/InvenTree-AI/issues/11). Public documentation only; no private server, identity tenant, cluster, or inventory was accessed. This is a proposed contract, not implemented authentication or a provider selection.

## Boundary and outstanding decision

The owner requires Docker Compose, a Helm chart for k3s, and authenticated public MCP access. Signing into an AI product does not authorize that person to InvenTree-AI. The service needs its own trusted authorization server and an explicit user-to-inventory permission policy. An OAuth client identifies an application; it is not a user permission. ChatGPT's custom MCP OAuth separates client, authorization server, and resource server, and does not support arbitrary API keys or machine-to-machine grants. [OpenAI authentication](https://developers.openai.com/plugins/build/auth).

**Pending owner decision:** named-user allowlist, organization SSO, or user-owned InvenTree instance mapping. None is selected here. Recommend fail-closed admission until that policy exists. Do not accept every user who can obtain a valid token from a broadly accessible identity provider. Client-name headers, user agents, and source IPs cannot substitute for user authorization.

## Documented client compatibility

| Client surface | Registration and callback facts |
| --- | --- |
| ChatGPT browser | OAuth with CIMD, DCR, or a predefined client; PKCE and discovery required. CIMD supports `none` or `private_key_jwt`. Exact callback behavior depends on issuer identification; register the redirect displayed by the actual connection setup. [OpenAI authentication](https://developers.openai.com/plugins/build/auth). |
| Codex host: desktop/CLI/IDE | Streamable HTTP supports bearer and OAuth. CIMD auto-selection requires advertised support, `none`, and compatible loopback callbacks; configured client IDs take precedence, otherwise DCR is available. Custom redirects can require DCR/pre-registration. The documented stable CIMD callback is still marked forthcoming: do not assume it has shipped. [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli). |
| Claude web connectors | DCR, CIMD, and static OAuth client credentials are documented. CIMD requires advertised support and `none`. S256 PKCE is always sent. Resource metadata must identify the exact MCP URL, including path; the first advertised issuer is used. [Claude authentication](https://claude.com/docs/connectors/building/authentication). |
| Claude Code | HTTP OAuth supports DCR, CIMD, and preconfigured clients. Fixed callback ports are configurable. Documented versions differ between `localhost` and `127.0.0.1`; inspect the actual installed version and redirect. [Claude Code MCP](https://code.claude.com/docs/en/mcp). |

These facts do not certify all hosted Codex execution environments or plugin distribution paths; retain the separate [client compatibility report](https://github.com/Miroling/InvenTree-AI/blob/a8e093c/docs/research/client-compatibility.md). No real client login was tested.

## Recommended protocol and enforcement

Use HTTPS Streamable HTTP with authorization-code OAuth and PKCE S256. Publish protected-resource metadata and authorization-server discovery without requiring an existing login. An unauthenticated MCP request should receive HTTP `401` with `WWW-Authenticate: Bearer resource_metadata="…"`, not an HTML login redirect or a successful tool-error response. Claude explicitly requires the `401` handshake. [Claude authentication](https://claude.com/docs/connectors/building/authentication).

Protect initialization, tool listing, resources, and tool calls under the proposed all-private service policy. Public discovery must contain no inventory. Bind access tokens to the canonical MCP resource, propagate OAuth `resource` requests correctly, and validate before processing. Do not forward client tokens to InvenTree; downstream credentials are separate. [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization).

Choose either supported verification mode explicitly:

- **JWT:** verify signature using trusted issuer keys and permitted algorithms, exact issuer, intended audience, expiry and applicable not-before time, and access-token type/profile. Reject ID tokens and unsigned tokens. Validate scopes and derive the subject from verified claims. [RFC 9068](https://www.rfc-editor.org/rfc/rfc9068.html).
- **Opaque token:** use an authenticated TLS introspection call to the configured issuer; require `active: true` and sufficient trusted metadata to establish audience, validity, subject, and scopes. Optional introspection fields must become provider integration requirements where policy needs them. Never infer permission merely from a nonempty token. Introspection caching delays awareness of revocation. [RFC 7662](https://www.rfc-editor.org/rfc/rfc7662.html).

After either verification mode, enforce the selected authorized-user policy, inventory ownership, and per-tool permissions on every request. Recommend `(issuer, subject)` as the principal key, read/write scopes such as `inventory:read` and `inventory:write`, and no deletion capability. A write scope alone cannot approve a change: project rules require a reviewable Change Plan and explicit approval. Reject altered, stale, replayed, or cross-user plans. These are proposed application requirements, not guarantees of OAuth.

Require refresh rotation for public clients, bounded token lifetimes, and a documented revocation latency. Logout/local credential removal must not be assumed to invalidate every issued access token. Recheck user permission changes; JWT verification alone does not detect a newly revoked grant. [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization), [RFC 7662](https://www.rfc-editor.org/rfc/rfc7662.html).

## Provider and deployment criteria

Prefer an established OAuth provider that passes discovery, S256, resource/audience issuance, the required registration modes, actual client redirects, refresh/revocation, and JWT/JWKS or introspection tests. Select it only after the user identity model is settled. Pre-registration can be a deliberate compatibility fallback; do not require a proprietary client credential flow as the shared baseline.

A browser-cookie reverse proxy alone is insufficient: MCP clients need bearer challenges, metadata, and token validation. An OAuth-aware gateway can enforce this contract if bypass is prevented and user/scope authorization still reaches the application. This is an architectural inference from the documented protocol, not a tested product comparison. Keep browser authorization redirects at the authorization endpoint; preserve MCP status codes, headers, and streaming through ingress.

Compose/Helm should require canonical public resource URL, trusted issuer, expected audience, verification mode, and an explicit mounted authorization policy. Keep InvenTree tokens, introspection credentials, and any client secrets in separate secret inputs. Expose only TLS ingress; browser workers, debug ports, health internals, and downstream services remain private. **Environment variables and chart validation do not implement authorization.**

## Release gate

**The release cannot expose an MCP runtime image publicly until this authentication contract is implemented and tested.** A deployment scaffold is not an authenticated service.

Using synthetic inventory, test each named client for discovery, exact redirects, login/refresh/revocation, and successful permitted calls. Verify rejection of anonymous requests, wrong issuer/audience, expired/invalid tokens, unauthorized users, missing scopes, cross-user access, and unapproved writes; verify deletions are unavailable. Test key rotation, issuer outages, ingress header/stream handling, and policy removal. Record versions and observed callbacks. These acceptance checks remain outstanding.
