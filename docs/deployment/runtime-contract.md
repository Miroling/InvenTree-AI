# Proposed MCP runtime contract

Status: an interface for deployment scaffolding, not an implemented server. Compose/Helm environment variables do not implement authentication. No image has been verified against this contract. The owner selected InvenTree-backed admission using personal API tokens; the OAuth broker library, encrypted persistent storage and inventory operation set remain to be implemented or specified.

See [the authentication design](authentication.md) for the selected authority and proposed linking flow. This supersedes the earlier shared-token/manual-allowlist scaffold interface.

## Container interface

The eventual image must support its declared Linux architectures, run as UID/GID `10001`, listen on `8000`, and tolerate a read-only root filesystem. `/tmp` is bounded ephemeral scratch space. One replica with replacement updates is intentional; availability during updates is not guaranteed.

The scaffold has no application database or persistent volume. Required durable credential, OAuth grant, signing-key and approval state must be configured through the broker integration before readiness succeeds. Scratch files and process memory are not durable credential storage.

| Input | Meaning |
| --- | --- |
| `MCP_HOST`, `MCP_PORT` | Internal listener, `0.0.0.0:8000`. |
| `MCP_PUBLIC_URL` | Canonical HTTPS MCP resource, ending in `/mcp`; must match resource metadata and ingress. |
| `MCP_AUTH_REQUIRED` | Always `true`. The runtime must reject absent, invalid or disabled authentication configuration. |
| `MCP_AUTH_MODE` | Fixed to `inventree-token`: InvenTree validates admission; the AI client receives a separate MCP OAuth token. |
| `MCP_AUTH_ISSUER_URL` | Derived HTTPS origin of `MCP_PUBLIC_URL`; the proposed broker shares the service origin. |
| `MCP_AUTH_AUDIENCE` | Expected audience/resource identifier for this MCP deployment. Validate it against the broker's actual issuance rules. |
| `MCP_AUTH_BROKER_CONFIG_FILE` | Read-only secret file containing signing and encrypted durable-store configuration. Its exact format depends on the maintained OAuth/storage components selected. |
| `INVENTREE_URL` | Operator-configured upstream base URL. Use HTTPS across untrusted networks; deliberately private HTTP requires a trusted network. Users cannot replace it with an arbitrary credential destination. |

These are proposed InvenTree-AI settings, not settings understood by the unmodified third-party `inventree-mcp` package. The image must implement them. There is no deployment-wide InvenTree token or separate allowed-user policy file. Personal credentials arrive through secure account linking and are resolved per authenticated caller.

## Proposed endpoints

- `/mcp`: Streamable HTTP. Protect initialization, listing and all actions with MCP token validation and InvenTree-backed admission. Use `401` plus `WWW-Authenticate` for absent/invalid MCP credentials. No inventory is returned before authorization.
- `/.well-known/oauth-protected-resource` and the resource-specific `/mcp` form when required: public, non-sensitive MCP resource discovery.
- `/.well-known/oauth-authorization-server`: public discovery for the broker issuer, advertising supported endpoints, PKCE and registration methods accurately.
- `/auth/*`: browser token-linking/consent and OAuth authorization, token and other supported protocol endpoints. They need endpoint-specific controls, not a pre-existing MCP bearer token; only the broker can issue a grant after the required checks. Exact subpaths are implementation choices advertised through discovery.
- `/health/live`: internal process health without inventory or secrets, independent of upstream availability to avoid restart loops.
- `/health/ready`: internal readiness; fail until auth configuration, signing keys and encrypted durable credential/grant storage are usable. Never silently fall back to anonymous mode or a shared token.
- `/usr/local/bin/inventree-ai-healthcheck`: image-provided executable checking local readiness, with nonzero exit when unready and no secret output. Compose uses it; Kubernetes uses HTTP probes.

Caddy/Traefik forward the MCP, broker and discovery routes. They do not themselves validate the user's InvenTree identity or implement OAuth. Health routes and any future browser control ports stay internal. Auth routes must be tested through ingress with the exact scheme/host and client callbacks.

## Runtime authorization

The selected model grants admission to this project's MCP services when InvenTree accepts the user's personal token. Every inventory operation uses that token and retains upstream permissions. Per-call admission checks also apply to enrichment tools that otherwise make no inventory API request. A revoked token, disabled identity or unavailable admission check cannot produce new allowed actions. No user may borrow another user's credentials or a global administrator token.

Maintain separate credentials for AI-to-MCP and service-to-InvenTree. Apply resource/audience binding, issuer verification, PKCE, exact redirects, protected refresh, caller-bound sessions, current upstream admission and operation permissions. Preserve the Change Plan approval requirement and prohibit automated deletion. Details and sources are in [the authentication design](authentication.md).

## Browser worker boundary

Obscura remains a candidate, not a bundled provider. A worker has no public control port, neither user's credential, and no direct inventory-write authority. It receives only authorized research jobs and produces attributable evidence. Specify URL/redirect/egress restrictions, resource limits and per-user job isolation before adding it.

## Required release evidence

With synthetic inventory, test all three clients' discovery, login, refresh and revocation; wrong-resource/issuer/expired MCP tokens; invalid/revoked upstream tokens; disabled users; restricted roles; upstream outages; cross-user sessions; retries; and rejected unapproved writes/deletes. Test that a valid MCP token cannot bypass lost InvenTree access and that a permission denial never triggers a privileged fallback.

Verify startup with missing/malformed broker config, unavailable encrypted storage, signing-key rotation, both health probes, non-root secret access, read-only filesystems, image architectures and streaming through both front doors. No such runtime/client/cluster tests have been performed yet; local template checks do not establish these properties.
