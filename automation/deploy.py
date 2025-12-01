"""Render Kubernetes manifests and apply them with kubectl."""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from .config import DeployConfig


def render_manifests(cfg: DeployConfig, tag: str, template_dir: str | Path = "k8s") -> list[dict]:
    docs: list[dict] = []
    for path in sorted(Path(template_dir).glob("*.yaml")):
        text = (path.read_text(encoding="utf-8")
                .replace("__IMAGE__", f"{cfg.image}:{tag}")
                .replace("__NAMESPACE__", cfg.namespace)
                .replace("__REPLICAS__", str(cfg.replicas))
                .replace("__PORT__", str(cfg.port)))
        docs.extend(d for d in yaml.safe_load_all(text) if d)
    return docs


def deploy(cfg: DeployConfig, tag: str, dry_run: bool = True, runner=subprocess.run,
           template_dir: str | Path = "k8s") -> str:
    manifest = yaml.safe_dump_all(render_manifests(cfg, tag, template_dir), sort_keys=False)
    if dry_run:
        return manifest
    runner(["kubectl", "apply", "-n", cfg.namespace, "-f", "-"],
           input=manifest, text=True, check=True)
    runner(["kubectl", "rollout", "status", "deployment/app", "-n", cfg.namespace,
            "--timeout=120s"], check=True)
    return manifest
