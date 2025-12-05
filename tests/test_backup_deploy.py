import tarfile
from datetime import datetime, timedelta

import pytest
import yaml

from automation.backup import create_backup, rotate_backups
from automation.config import DeployConfig, load_config
from automation.deploy import deploy, render_manifests


def test_backup_and_rotation(tmp_path):
    src = tmp_path / "data"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    dest = tmp_path / "out"
    base = datetime(2026, 1, 1)
    for i in range(4):
        create_backup([str(src)], dest, now=base + timedelta(minutes=i))
    removed = rotate_backups(dest, keep=2)
    assert len(removed) == 2
    left = sorted(p.name for p in dest.glob("*.tar.gz"))
    assert left == ["backup-20260101-000200.tar.gz", "backup-20260101-000300.tar.gz"]
    with tarfile.open(dest / left[0]) as tar:
        assert "data/a.txt" in tar.getnames()


def test_backup_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup([str(tmp_path / "nope")], tmp_path / "out")


def test_render_manifests_substitutes_values():
    docs = render_manifests(DeployConfig(image="img", namespace="prod", replicas=4, port=9000), "v1")
    deployment = next(d for d in docs if d["kind"] == "Deployment")
    assert deployment["spec"]["replicas"] == 4
    assert deployment["spec"]["template"]["spec"]["containers"][0]["image"] == "img:v1"
    assert all(d["kind"] == "Namespace" or d["metadata"]["namespace"] == "prod" for d in docs)


def test_deploy_dry_run_does_not_call_kubectl():
    calls = []
    out = deploy(DeployConfig(), "abc", dry_run=True, runner=lambda *a, **k: calls.append(a))
    assert calls == [] and list(yaml.safe_load_all(out))


def test_deploy_apply_runs_kubectl():
    calls = []
    deploy(DeployConfig(), "abc", dry_run=False, runner=lambda *a, **k: calls.append(a[0]))
    assert calls[0][:2] == ["kubectl", "apply"] and calls[1][:3] == ["kubectl", "rollout", "status"]


def test_load_config_rejects_bad_url(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text("services:\n  - name: x\n    url: ftp://nope\n")
    with pytest.raises(ValueError):
        load_config(f)
