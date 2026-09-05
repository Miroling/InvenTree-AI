#!/usr/bin/env python3
"""Validate deployment scaffolds locally; never contact a daemon or cluster."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "inventree-ai"


class DeploymentTemplates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="inventree-ai-validation-")
        cls.path = Path(cls.temp.name)
        cls.addClassCleanup(cls.temp.cleanup)
        cls.values = {
            "image": {"reference": "example.invalid/inventree-ai:validation-only"},
            "publicUrl": "https://mcp.example.invalid/mcp",
            "inventreeUrl": "https://inventory.example.invalid",
            "auth": {"issuerUrl": "https://identity.example.invalid", "audience": "inventory-mcp"},
            "existingSecret": "synthetic-existing-secret",
        }
        cls.values_file = cls.path / "values.json"
        cls.values_file.write_text(json.dumps(cls.values))
        cls.base_env = {"PATH": os.environ["PATH"]}
        # Avoid inherited provider, kubeconfig, Helm and Compose configuration.
        cls.cli_env = {
            **cls.base_env,
            "HELM_CONFIG_HOME": str(cls.path / "helm-config"),
            "HELM_CACHE_HOME": str(cls.path / "helm-cache"),
            "HELM_DATA_HOME": str(cls.path / "helm-data"),
        }
        cls.token_file = cls.path / "token"
        cls.policy_file = cls.path / "policy.json"
        cls.token_file.write_text("SYNTHETIC_SECRET_NOT_FOR_USE")
        cls.policy_file.write_text('{"validation_fixture_only":true}')
        cls.compose_env = {
            **cls.base_env,
            "MCP_IMAGE": "example.invalid/inventree-ai:validation-only",
            "CADDY_IMAGE": "example.invalid/caddy:validation-only",
            "MCP_DOMAIN": "mcp.example.invalid",
            "MCP_AUTH_ISSUER_URL": "https://identity.example.invalid",
            "MCP_AUTH_AUDIENCE": "inventory-mcp",
            "INVENTREE_URL": "https://inventory.example.invalid",
            "INVENTREE_TOKEN_FILE": str(cls.token_file),
            "MCP_AUTH_POLICY_FILE": str(cls.policy_file),
        }

    def command(self, args, *, env=None, success=True):
        result = subprocess.run(args, cwd=ROOT, env=env or self.cli_env,
                                text=True, capture_output=True, timeout=45)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, "Invalid configuration was accepted")
        return result

    def render(self, *overrides):
        result = self.command(["helm", "template", "validation", str(CHART),
                               "-f", str(self.values_file), *overrides])
        return {item["kind"]: item for item in yaml.safe_load_all(result.stdout) if item}

    def compose(self, env=None, success=True):
        return self.command(["docker", "compose", "--env-file", "/dev/null",
                             "-f", str(ROOT / "compose.yaml"), "config", "--format", "json"],
                            env=self.compose_env if env is None else env, success=success)

    def test_helm_lint(self):
        self.command(["helm", "lint", str(CHART), "-f", str(self.values_file), "--strict"])

    def test_private_service_and_required_auth(self):
        objects = self.render()
        self.assertNotIn("Ingress", objects)
        self.assertNotIn("Secret", objects)
        self.assertEqual(objects["Service"]["spec"]["type"], "ClusterIP")
        pod = objects["Deployment"]["spec"]["template"]["spec"]
        self.assertFalse(pod["automountServiceAccountToken"])
        container = pod["containers"][0]
        env = {item["name"]: item["value"] for item in container["env"]}
        self.assertEqual(env["MCP_AUTH_REQUIRED"], "true")
        self.assertNotIn("INVENTREE_TOKEN", env)
        self.assertTrue(container["securityContext"]["readOnlyRootFilesystem"])
        self.assertEqual(pod["volumes"][0]["secret"]["secretName"], "synthetic-existing-secret")
        source = objects["NetworkPolicy"]["spec"]["ingress"][0]["from"]
        self.assertEqual(len(source), 1)
        self.assertIn("podSelector", source[0])
        self.assertIn("namespaceSelector", source[0])

    def test_https_ingress_excludes_health_routes(self):
        objects = self.render("--set", "ingress.enabled=true", "--set", "ingress.host=mcp.example.invalid",
                              "--set", "ingress.tlsSecretName=synthetic-tls")
        ingress = objects["Ingress"]["spec"]
        self.assertEqual(ingress["tls"][0]["secretName"], "synthetic-tls")
        paths = [x["path"] for x in ingress["rules"][0]["http"]["paths"]]
        self.assertEqual(paths, ["/mcp", "/.well-known/oauth-protected-resource"])

    def test_invalid_or_missing_auth_configuration_is_rejected(self):
        for override in ["auth.issuerUrl=", "auth.audience=", "auth.issuerUrl=http://identity.example.invalid",
                         "existingSecret=", "image.reference=", "publicUrl=http://mcp.example.invalid/mcp",
                         "auth.required=false"]:
            with self.subTest(override=override):
                self.command(["helm", "template", "validation", str(CHART), "-f", str(self.values_file),
                              "--set", override], success=False)

    def test_public_ingress_requires_tls_and_matching_resource(self):
        for override in ["ingress.tlsSecretName=", "ingress.host=other.example.invalid"]:
            with self.subTest(override=override):
                self.command(["helm", "template", "validation", str(CHART), "-f", str(self.values_file),
                              "--set", "ingress.enabled=true", "--set", "ingress.host=mcp.example.invalid",
                              "--set", "ingress.tlsSecretName=synthetic-tls", "--set", override], success=False)

    def test_empty_chart_values_do_not_deploy(self):
        self.command(["helm", "template", "validation", str(CHART)], success=False)

    def test_compose_does_not_publish_backend_or_inline_credentials(self):
        result = self.compose()
        config = json.loads(result.stdout)
        mcp = config["services"]["mcp"]
        self.assertFalse(mcp.get("ports"))
        self.assertEqual(mcp["environment"]["MCP_AUTH_REQUIRED"], "true")
        self.assertNotIn("SYNTHETIC_SECRET_NOT_FOR_USE", result.stdout)
        gateway = config["services"]["gateway"]
        self.assertEqual({p["host_ip"] for p in gateway["ports"]}, {"127.0.0.1"})
        self.assertEqual(gateway["depends_on"]["mcp"]["condition"], "service_healthy")

    def test_compose_requires_image_auth_and_secret_inputs(self):
        for key in ["MCP_IMAGE", "CADDY_IMAGE", "MCP_AUTH_ISSUER_URL", "MCP_AUTH_AUDIENCE",
                    "INVENTREE_TOKEN_FILE", "MCP_AUTH_POLICY_FILE"]:
            with self.subTest(key=key):
                self.compose({k: v for k, v in self.compose_env.items() if k != key}, success=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
