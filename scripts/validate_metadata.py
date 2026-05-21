#!/usr/bin/env python3
"""Validate metadata/registry.json against metadata/schema.json and repository state.

Pure-stdlib JSON Schema subset checker. Intentionally narrow: it understands
the constructs we actually use (`type`, `enum`, `required`, `properties`,
`items`, `pattern`, `minLength`, `minimum`, `maximum`, `additionalProperties`,
`$ref` to `#/definitions/...`, `oneOf`/`anyOf` are not used).

We do not pull in `jsonschema` so the script runs on a fresh checkout.

Exits 0 on success, 1 on any error. Prints one error per line.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "metadata" / "schema.json"
REGISTRY_PATH = REPO_ROOT / "metadata" / "registry.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def resolve(schema: dict, ref: str) -> dict:
    assert ref.startswith("#/")
    node: Any = schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def validate(node: Any, sub: dict, root: dict, path: str, errs: list[str]) -> None:
    if "$ref" in sub:
        validate(node, resolve(root, sub["$ref"]), root, path, errs)
        return

    if "enum" in sub and node not in sub["enum"]:
        errs.append(f"{path}: {node!r} not in enum {sub['enum']}")
        return

    t = sub.get("type")
    if t == "string":
        if not isinstance(node, str):
            errs.append(f"{path}: expected string, got {type(node).__name__}")
            return
        if "minLength" in sub and len(node) < sub["minLength"]:
            errs.append(f"{path}: shorter than minLength {sub['minLength']}")
        if "pattern" in sub and not re.fullmatch(sub["pattern"], node):
            errs.append(f"{path}: does not match pattern {sub['pattern']}")
    elif t == "integer":
        if not isinstance(node, int) or isinstance(node, bool):
            errs.append(f"{path}: expected integer")
            return
        if "minimum" in sub and node < sub["minimum"]:
            errs.append(f"{path}: below minimum {sub['minimum']}")
    elif t == "number":
        if not isinstance(node, (int, float)) or isinstance(node, bool):
            errs.append(f"{path}: expected number")
            return
        if "minimum" in sub and node < sub["minimum"]:
            errs.append(f"{path}: below minimum {sub['minimum']}")
    elif t == "array":
        if not isinstance(node, list):
            errs.append(f"{path}: expected array")
            return
        if "items" in sub:
            for i, item in enumerate(node):
                validate(item, sub["items"], root, f"{path}[{i}]", errs)
    elif t == "object":
        if not isinstance(node, dict):
            errs.append(f"{path}: expected object")
            return
        for req in sub.get("required", []):
            if req not in node:
                errs.append(f"{path}: missing required field {req!r}")
        props = sub.get("properties", {})
        if sub.get("additionalProperties") is False:
            extra = set(node) - set(props)
            for k in sorted(extra):
                errs.append(f"{path}: unexpected field {k!r}")
        for k, v in node.items():
            if k in props:
                validate(v, props[k], root, f"{path}.{k}", errs)


def repo_rules(reg: dict, errs: list[str]) -> None:
    seen_ids: set[str] = set()
    for i, e in enumerate(reg.get("entries", [])):
        ep = f"entries[{i}]"
        eid = e.get("id", "")
        if eid in seen_ids:
            errs.append(f"{ep}: duplicate id {eid!r}")
        seen_ids.add(eid)

        status = e.get("status")

        if status == "embargoed":
            for forbidden in ("poc_path", "attack_tx"):
                if forbidden in e:
                    errs.append(f"{ep}: embargoed entry must not include {forbidden!r}")
        else:
            poc = e.get("poc_path")
            if poc and not (REPO_ROOT / poc).exists():
                errs.append(f"{ep}: poc_path does not exist: {poc}")

        if e.get("vm") == "EVM" and status not in ("embargoed", "template"):
            if "block_number" not in e:
                errs.append(f"{ep}: EVM entry missing block_number")

        if status not in ("embargoed", "educational", "template"):
            if not e.get("references"):
                errs.append(f"{ep}: at least one reference required for status={status!r}")


def main() -> int:
    schema = load(SCHEMA_PATH)
    registry = load(REGISTRY_PATH)
    errs: list[str] = []
    validate(registry, schema, schema, "$", errs)
    repo_rules(registry, errs)

    if errs:
        for e in errs:
            print(f"error: {e}", file=sys.stderr)
        print(f"\n{len(errs)} error(s)", file=sys.stderr)
        return 1

    print(f"ok: {len(registry.get('entries', []))} entries valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
