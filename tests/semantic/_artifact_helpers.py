from __future__ import annotations

import json
from pathlib import Path


SOURCE = (
    "pragma solidity ^0.8.20;\n"
    "contract GenericArtifactContract {\n"
    "    uint256 public value;\n"
    "    function setValue(uint256 next) external { value = next; }\n"
    "}\n"
)


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
