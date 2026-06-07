from __future__ import annotations

import os
from pathlib import Path


def load_local_env(start: str | Path | None = None) -> None:
    """Load simple KEY=VALUE lines from a local .env file if present."""
    root = Path(start or Path.cwd()).resolve()
    candidates = [
        root / ".env",
        root.parent / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for path in candidates:
        if path.exists():
            _load_env_file(path)
            return


def _load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
