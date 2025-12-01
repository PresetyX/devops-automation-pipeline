"""Create timestamped tar.gz backups and rotate old ones."""
from __future__ import annotations

import tarfile
from datetime import datetime
from pathlib import Path


def create_backup(sources: list[str], destination: str | Path, now: datetime | None = None) -> Path:
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    archive = dest / f"backup-{stamp}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for src in sources:
            path = Path(src)
            if not path.exists():
                raise FileNotFoundError(f"backup source not found: {src}")
            tar.add(path, arcname=path.name)
    return archive


def rotate_backups(destination: str | Path, keep: int) -> list[Path]:
    """Delete the oldest archives, keeping the newest N. Returns removed files."""
    if keep < 1:
        raise ValueError("keep must be >= 1")
    archives = sorted(Path(destination).glob("backup-*.tar.gz"))
    removed = archives[:-keep] if len(archives) > keep else []
    for old in removed:
        old.unlink()
    return removed
