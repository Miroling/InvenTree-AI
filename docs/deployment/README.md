# Docker Compose and k3s deployment

**Status: deployment scaffolding.** Compose and Helm files are available and can be validated locally. The MCP application, its image, InvenTree-backed OAuth broker, encrypted credential storage, and client login tests are not implemented yet. Do not treat a successful render as a working or authenticated release.

The runtime must first implement [the proposed image contract](runtime-contract.md). This repository does not currently publish an image to pull. Deployment commands below document the eventual operator workflow; configuration checks are usable now with the synthetic validation script.

## Architecture

```text
ChatGPT / Codex / Claude ── service OAuth token ── MCP service ── user token ── InvenTree
             │                                      │
             └── Browser login with InvenTree token ─┘

Compose: Caddy → private container listener
k3s:     existing Traefik HTTPS ingress → ClusterIP Service → MCP Pod
```

Only the front door is public. OAuth discovery and login routes are public; MCP calls require runtime authorization. The user links a personal InvenTree token on the HTTPS login page. Tokens are stored encrypted and resolved per caller; no shared administrator token is deployed. InvenTree determines admission and operation permissions. See [the authentication design](authentication.md). No browser worker or public browser control port is included.

## Docker Compose

1. Copy `deploy/compose/.env.example` to an operator-owned file outside source control and fill in the verified MCP image, pinned official Caddy image, MCP domain, OAuth audience, upstream URL, and broker-configuration file path. Use an absolute secret-file path. The issuer is derived from the MCP HTTPS origin. Broker configuration must specify signing and encrypted durable-store access once the implementation is selected; it contains no deployment-wide InvenTree token.
2. Make the mounted broker-configuration file readable by the container's UID/GID `10001` without broadening access to unrelated users. Compose file-backed secrets use bind mounts; do not assume a `uid` or `mode` declaration will fix host permissions. Keep secret contents out of environment worksheets and command arguments. [Compose secret behavior](https://docs.docker.com/reference/compose-file/services/#secrets).
3. Validate without contacting Docker Engine:

   ```sh
   docker compose --env-file /absolute/path/to/inventree-ai.env -f compose.yaml config --quiet
   ```

4. After the actual image passes the authorization tests, configure the domain and a reachable TLS front door. The default `MCP_BIND_ADDRESS=127.0.0.1` avoids accidental public binding. Set it deliberately for the target host. Caddy's automatic certificates require appropriate public DNS and ACME reachability; loopback bindings by themselves do not provide that. An existing front proxy is another operator-specific setup. [Caddy HTTPS](https://caddyserver.com/docs/automatic-https).
5. On the intended deployment host, start the validated stack:

   ```sh
   docker compose --env-file /absolute/path/to/inventree-ai.env -f compose.yaml up -d
   ```

The MCP container publishes no host port. Caddy waits for the image's health check and forwards `/mcp`, `/auth` and OAuth discovery. It does not implement OAuth itself. Certificate data is kept in named volumes. Credential/grant/approval state has no persistent storage in this scaffold; its runtime requirements must be completed first.

## Helm on k3s

The chart uses standard Deployment, Service, Ingress, and NetworkPolicy resources. It assumes an existing ingress controller and TLS Secret. It does not install or reconfigure the cluster's Traefik, certificate manager, or InvenTree. k3s normally includes Traefik, but actual versions, labels and enabled components must be checked for the target cluster. [k3s networking](https://docs.k3s.io/networking/networking-services).

1. Prepare a namespace, a TLS certificate Secret, and an application Secret through the operator's normal secret-management process. The application Secret must have an `auth-broker.json` key for the future signing/storage configuration. Personal InvenTree credentials are linked at runtime. Reference its name in Helm values; never place these values themselves in a chart, Git commit, or `--set` argument. Kubernetes Secrets require appropriate cluster RBAC, storage encryption and backup policy; a Secret reference alone does not establish those controls.
2. Copy `deploy/k3s/values.example.yaml` to an operator-owned values file. Set the verified image, canonical resource URL, upstream URL, audience, and existing Secret names. Set the ingress host to match the public URL exactly; its HTTPS origin is the broker issuer. Adjust the ingress-controller namespace/pod selectors if needed.
3. Validate locally, without a kubeconfig or cluster connection:

   ```sh
   helm lint charts/inventree-ai -f /absolute/path/to/values.yaml --strict
   helm template inventory charts/inventree-ai -f /absolute/path/to/values.yaml
   ```

4. After runtime tests and authorization to deploy to the target cluster, install:

   ```sh
   helm upgrade --install inventory charts/inventree-ai \
     --namespace inventree-ai --create-namespace \
     -f /absolute/path/to/values.yaml --wait --timeout 5m
   ```

An empty configuration intentionally fails schema validation. Ingress is disabled in base values. The enabled k3s worksheet requires a host and TLS Secret; it uses Traefik's `websecure` entrypoint. The backend remains ClusterIP. NetworkPolicy restricts ingress to the configured controller when the cluster enforces it; outbound traffic is not restricted by this chart. Health routes are not included in the public ingress.

Until secret reload is implemented and tested, rotate mounted credentials with a coordinated workload restart. The one-replica Recreate strategy permits downtime; scale-out, durable storage, and zero-downtime upgrades remain runtime design work.

## Local verification available now

Prerequisites: Python 3.11+, Helm 3+, and Docker Compose v2-compatible CLI. Docker Engine and Kubernetes are not used by the checks.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/validate-deployments.py
```

The script renders synthetic configurations, validates the chart, verifies protected deployment inputs and internal service exposure, and checks that missing auth configuration or invalid public ingress is rejected. Its image references are intentionally non-deployable. These checks do not pull images, run containers, use a kubeconfig, or test an OAuth flow.
