# InvenTree-backed MCP admission

Status: owner-selected admission rule with a proposed implementation design. No authentication runtime or live token validation exists in this repository yet. This updates [Choose who may access the InvenTree integration](https://github.com/Miroling/InvenTree-AI/issues/13): InvenTree is the authority for admission, superseding the earlier separate manual allowlist interpretation.

## Owner requirement

Validate a user's personal InvenTree API token against the configured InvenTree instance. If InvenTree accepts the identity, admit the user to the InvenTree-AI MCP services. This applies to the MCP endpoints owned by this project; it cannot grant access to unrelated third-party services. Each inventory operation still runs with that user's token and is limited by InvenTree's permissions. No shared administrator/service token can substitute when the user's request is denied.

InvenTree documents token-based API authentication, user-specific role enforcement, and permission-denied responses for disallowed actions. These establish the upstream authority; successful login does not imply full inventory permissions. [InvenTree API authentication and authorization](https://docs.inventree.org/en/stable/api/).

## Proposed browser connection

1. The AI client discovers the MCP resource and starts OAuth authorization-code login with PKCE.
2. The browser opens the integration's HTTPS authorization page. The user enters their InvenTree token there, directly to the service, and consents to linking it. The token must not be entered into chat, sent in a URL, retained in browser storage, or included in model-visible tool arguments.
3. The broker validates the credential using a protected authenticated identity endpoint on the operator-configured instance. The current official schema documents `GET /api/user/me/` for the current user. Establish that identity, not merely HTTP 200 on a public health/API-root page; confirm the endpoint/payload against the target version during authorized integration testing. Do not use `/api/user/me/token/` as a validation probe: current schema describes token issuance/rotation there. [User API schema](https://docs.inventree.org/en/stable/api/schema/user/).
4. After successful validation, the broker links the credential to the verified instance/user identity and issues a short-lived, client/redirect/PKCE-bound authorization code. The client exchanges that code for a separate MCP access token.
5. For an authorized tool request, the MCP service resolves the authenticated user's linked credential. It supplies `Authorization: Token <personal-token>` only to the configured InvenTree API, without following credential-bearing redirects to a different origin.
6. All project MCP entry points apply the same admission rule. Distinct MCP resources still require correctly scoped/audience-bound credentials; a shared login is not a universal bearer token for arbitrary resources.

The broker's token-signing, registration, credential storage and login implementation will use maintained OAuth components where possible. A separate Authentik/Keycloak/Auth0 user directory is not required by this admission model. The precise library and persistence mechanism remain open.

## Two different tokens

| Credential | Issuer / authority | Recipient |
| --- | --- | --- |
| Personal InvenTree API token | Configured InvenTree instance | InvenTree only; held by the service as a linked upstream credential |
| MCP OAuth access token | InvenTree-AI OAuth broker | The intended project MCP resource; validated before any tool action |

This is upstream credential use after explicit account linking, not accepting the InvenTree token as an MCP bearer token and forwarding that same inbound bearer. The distinction is needed for browser compatibility and resource binding: ChatGPT cannot present arbitrary custom API keys, and MCP requires access tokens intended for the MCP resource. [OpenAI authentication](https://developers.openai.com/plugins/build/auth), [MCP token requirements](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization#token-requirements).

## Ongoing access and failure behavior

- Validate the upstream credential at account linking and refresh. Before each protected MCP action, including browser-only enrichment actions, revalidate admission against InvenTree. Initial design uses no positive authorization cache; a later bounded cache requires an explicit revocation-latency decision.
- An invalidated token or disabled identity blocks subsequent actions and refresh. An already-running action cannot be retroactively undone. A request racing with revocation remains subject to the upstream API's check when it performs an inventory operation.
- Preserve operation-level `403` denials; they are not permission to retry with a more privileged identity. Distinguish them from a failure of the admission check.
- If identity validation cannot complete because InvenTree is unreachable, timeouts or server errors must not grant access. Return a temporary service failure without describing it as a permanently invalid credential.
- Bind sessions, refresh grants, linked credentials and Change Plans to the verified principal and configured instance. Never reuse one user's upstream credential for another.
- Browser workers receive neither token. They act only after the central service authorizes a job and receive the minimum research input.

## Secret storage and deployment changes

Personal tokens are collected at runtime and stored encrypted server-side, with access limited to credential resolution. Signing keys, storage access and encryption-key configuration belong in an operator-managed `auth-broker.json` secret. Its exact schema depends on the chosen implementation. Do not publish actual tokens, keys, or account lists.

Compose and Helm no longer mount a shared `inventree-token` or a manual `authorization-policy.json`. They select `MCP_AUTH_MODE=inventree-token`, mount broker configuration, and expose discovery plus `/auth` routes alongside `/mcp`. The proposed broker issuer is the HTTPS origin of the canonical MCP resource URL.

The scaffold does not yet deploy durable credential/grant storage. The runtime must not become ready until its persistent encrypted store and signing configuration are valid. Implement and test rotation, refresh-token replay detection, PKCE, exact redirect binding, anti-CSRF controls, login throttling, safe errors, and deletion of linked credentials before claiming a working release.

The existing Change Plan approval requirement and no-automated-deletion constraint remain in force. Upstream permission to change inventory is necessary but does not replace approval of the specific proposed change.
