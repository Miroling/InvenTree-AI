# InvenTree-AI Helm chart

Deployment scaffold for k3s using a ClusterIP service and optional Traefik HTTPS ingress. The repository does not yet contain or publish the MCP application image. This chart cannot provide working inventory tools or OAuth by itself.

See [deployment instructions](../../docs/deployment/README.md), the [proposed runtime contract](../../docs/deployment/runtime-contract.md), and the [k3s values worksheet](../../deploy/k3s/values.example.yaml).

Required values: `image.reference`, `publicUrl`, `inventreeUrl`, `auth.issuerUrl`, `auth.audience`, and `existingSecret`. Public ingress additionally requires `ingress.host` and `ingress.tlsSecretName`. The public URL must exactly match `https://<ingress.host>/mcp`.

The referenced Secret must already contain `inventree-token` and `authorization-policy.json`. The TLS Secret and ingress controller must already exist. The chart does not provision an identity provider, issue certificates, build the image, install InvenTree, or create production credentials.

The chart uses one replica, a non-root process, a read-only root filesystem, internal health probes, and ingress NetworkPolicy. The default policy expects Traefik pods labelled `app.kubernetes.io/name=traefik` in `kube-system`; configure selectors for the actual installation. Policy enforcement depends on the cluster network-policy controller. Outbound connections remain allowed for the configured InvenTree and identity services.

Run local validation with `python scripts/validate-deployments.py` after installing `requirements-dev.txt`. Validation uses synthetic values and does not contact Kubernetes or Docker Engine.
