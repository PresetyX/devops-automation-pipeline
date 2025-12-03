"""Command line entry point: python -m automation <command>."""
from __future__ import annotations

import argparse
import json
import sys

from .backup import create_backup, rotate_backups
from .config import load_config
from .deploy import deploy
from .healthcheck import check_all


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="automation", description="DevOps automation toolkit")
    p.add_argument("-c", "--config", default="config/services.yaml")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("health", help="check all configured services")
    sub.add_parser("backup", help="create a backup and rotate old ones")
    d = sub.add_parser("deploy", help="render and apply Kubernetes manifests")
    d.add_argument("--tag", required=True)
    d.add_argument("--apply", action="store_true", help="really run kubectl (default is dry-run)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    if args.command == "health":
        results = check_all(cfg.services)
        print(json.dumps([r.__dict__ for r in results], indent=2))
        return 0 if all(r.healthy for r in results) else 1
    if args.command == "backup":
        archive = create_backup(cfg.backup.sources, cfg.backup.destination)
        removed = rotate_backups(cfg.backup.destination, cfg.backup.keep)
        print(f"created {archive}; removed {len(removed)} old archive(s)")
        return 0
    print(deploy(cfg.deploy, args.tag, dry_run=not args.apply))
    return 0


if __name__ == "__main__":
    sys.exit(main())
