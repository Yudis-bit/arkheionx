"""Small JSON config loader used by future Arkheionx engine modules."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from arkheionx.core.files import load_json


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = load_json(path)
    return payload if isinstance(payload, dict) else {}
