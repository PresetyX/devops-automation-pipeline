"""Typed configuration loaded from a YAML file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Service:
    name: str
    url: str
    expected_status: int = 200
    timeout: float = 5.0
    retries: int = 3


@dataclass(frozen=True)
class BackupConfig:
    sources: list[str] = field(default_factory=list)
    destination: str = "backups"
    keep: int = 5


@dataclass(frozen=True)
class DeployConfig:
    image: str = "ghcr.io/example/app"
    namespace: str = "default"
    replicas: int = 2
    port: int = 8080


@dataclass(frozen=True)
class Config:
    services: list[Service]
    backup: BackupConfig
    deploy: DeployConfig


def load_config(path: str | Path) -> Config:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    services = [Service(**s) for s in data.get("services", [])]
    for s in services:
        if not s.url.startswith(("http://", "https://")):
            raise ValueError(f"service '{s.name}' has an invalid url: {s.url}")
    return Config(
        services=services,
        backup=BackupConfig(**data.get("backup", {})),
        deploy=DeployConfig(**data.get("deploy", {})),
    )
