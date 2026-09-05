# Proposed MCP runtime contract

Status: an interface for the deployment scaffold, not an implemented server. Docker Compose and Helm cannot enforce application authentication merely by setting environment variables. No current image has been verified against this contract. The authentication provider, authorized-user model, and inventory operation set remain open decisions.

The owner requested Docker Compose, Helm deployment on k3s, and authenticated access from ChatGPT, Codex, and Claude. Preparing these deployment artifacts is explicitly in scope before the rest of the implementation is selected.

## Container interface

The eventual image must support Linux architectures published in its manifest, run as UID/GID `10001`, listen on port `8000`, and tolerate a read-only root filesystem. `/tmp` is bounded ephemeral scratch space. There is no application persistent volume or database in the scaffold: durable identity, approval, and session state must be designed before claiming restart safety. One replica with replacement updates is intentional; availability during updates is not guaranteed.

| Input | Meaning |
| --- | --- |
| `MCP_HOST`, `MCP_PORT` | Internal listener, `0.0.0.0:8000`. |
| `MCP_PUBLIC_URL` | Exact canonical HTTPS resource URL, ending in `/mcp`. Used for resource metadata and OAuth resource binding. |
| `MCP_AUTH_REQUIRED` | Always `true` in these deployment artifacts. The application must reject missing, invalid, or disabled auth configuration at startup. |
| `MCP_AUTH_ISSUER_URL` | Trusted HTTPS authorization-server issuer; never obtained from an untrusted token. |
| `MCP_AUTH_AUDIENCE` | Expected audience/resource for this MCP service. Validation must follow the actual provider's token format. |
| `MCP_AUTH_POLICY_FILE` | Read-only file containing service authorization rules. Its format will be chosen with the identity model; missing, invalid, or unmatched policy must deny access. |
| `INVENTREE_URL` | Operator-configured upstream instance URL. HTTP is only for a deliberately trusted private network; use HTTPS across untrusted networks. Never accept a caller-supplied arbitrary instance URL in a single-instance deployment. |
| `INVENTREE_TOKEN_FILE` | Separate read-only upstream credential file. Never forward the MCP bearer token to InvenTree. |

These names are a proposed project interface, not the existing third-party `inventree-mcp` package's settings. Pointing the chart at that package's image does not make it compatible or authenticated. No image tag is invented by the examples.

## Endpoints

- `/mcp`: Streamable HTTP. Every MCP request, including initialization and tool listing, requires valid service authorization. Return `401` and a standards-compliant `WWW-Authenticate` challenge for missing/invalid credentials. Valid authentication without permission must not allow inventory access.
- `/.well-known/oauth-protected-resource` and, where required, its `/mcp` resource-specific form: public, non-sensitive discovery with exact resource and issuer metadata. Public OAuth discovery is compatible with protecting inventory tools.
- `/health/live`: internal process-health response containing no credentials or inventory. It must not depend on InvenTree availability, to avoid restart loops during an upstream outage.
- `/health/ready`: internal readiness response. It must remain unsuccessful until auth configuration and authorization policy are loaded and the service is able to enforce them.
- `/usr/local/bin/inventree-ai-healthcheck`: an image-provided executable that checks local readiness and exits nonzero when unready, without emitting secrets. Compose uses it; Kubernetes uses the HTTP probes.

The OAuth provider serves its own discovery, login, authorization, token, and registration endpoints. These artifacts neither deploy a provider nor implement a redirecting cookie-login proxy. A provider requiring an application callback/broker will need additional routes after that choice is made.

## Authentication and authorization requirements

Signing in to ChatGPT, Codex, or Claude does not confer access to someone's inventory. A client must obtain an OAuth access token for this MCP service after the authorized person signs in and consents. The server must validate signature or authenticated introspection, issuer, audience/resource, validity times, required scopes, and the selected allowed-user/organization/instance policy. Client names, `User-Agent`, CORS, and IP lists do not replace these checks.

The identity decision will choose allowlisted people, organizational SSO, or another explicitly agreed mapping. Until then, the authorization policy has no permissive example. Client registration through CIMD/DCR does not authorize a user; accepting a registration must not grant inventory access. Read and write permissions must be distinguishable, approved changes must remain tied to their specific plan, and automated deletion remains prohibited.

See [authenticated client research](https://github.com/Miroling/InvenTree-AI/blob/60c7a2d309f325c6392718fbcef8e7e3ffc6007e/docs/research/authenticated-clients.md), [OpenAI authentication](https://developers.openai.com/plugins/build/auth), and [Claude connector authentication](https://claude.com/docs/connectors/building/authentication). Exact client callbacks and provider registration support must be verified when configuring the chosen provider.

## Browser worker boundary

Obscura is under evaluation, not selected or bundled. A future browser worker must have no public CDP/control port, no mounted InvenTree token, and no direct inventory-write authority. It receives only the specific research input and returns attributable extraction evidence. Bound browser memory/time/concurrency and protect private-network and metadata destinations before adding URL-fetching tools. Add the chosen worker and its deployment resources only after its API and sandbox requirements are established.

## Required release evidence

Before public deployment, test the actual built image with synthetic inventory using all three clients. Include discovery and OAuth login; invalid/expired/wrong-audience tokens; valid-but-unapproved users; missing read/write scopes; cross-user sessions and plans; token revocation; explicit approval; deletion rejection; connection restart; and secret-safe errors. Confirm that unauthenticated `initialize`, `tools/list`, and `tools/call` cannot access service functionality and that public discovery contains no inventory.

Test image startup with missing/malformed policy and secrets, Linux architecture support, non-root file access, read-only root behavior, both health probe forms, and streaming through Caddy and the actual k3s ingress. Chart linting and configuration rendering do not establish any of these runtime properties.
