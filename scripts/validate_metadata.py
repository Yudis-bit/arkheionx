#!/usr/bin/env python3
"""Validate metadata/registry.json against metadata/schema.json and repository state.

Pure-stdlib JSON Schema subset checker. Intentionally narrow: it understands
the constructs we actually use (`type`, `enum`, `required`, `properties`,
`items`, `pattern`, `minLength`, `minimum`, `maximum`, `additionalProperties`,
`format: uri`, `$ref` to `#/definitions/...`, `oneOf`, and `anyOf`).

Repository-level checks also compare EVM registry metadata against the fork
block and RPC alias declared in each Solidity PoC.

We do not pull in `jsonschema` so the script runs on a fresh checkout.

Exits 0 on success, 1 on any error. Prints one error per line.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "metadata" / "schema.json"
REGISTRY_PATH = REPO_ROOT / "metadata" / "registry.json"
FOUNDRY_TOML = REPO_ROOT / "EVM" / "foundry.toml"

RPC_ENDPOINT_RE = re.compile(
    r'^\s*([A-Za-z0-9_-]+)\s*=\s*"\$\{([A-Z0-9_]+)\}"\s*$', re.MULTILINE
)
UINT_DECL_RE = re.compile(r"\buint256\s+(?:\w+\s+)*([A-Za-z_]\w*)\s*=\s*([^;]+);")
STRING_DECL_RE = re.compile(r'\bstring\s+(?:\w+\s+)*([A-Za-z_]\w*)\s*=\s*"([^"]+)"\s*;')
FORK_CALL_RE = re.compile(
    r"createSelectFork\s*\(\s*(.+?)\s*,\s*([^)]+?)\s*\)", re.DOTALL
)
STRING_LITERAL_RE = re.compile(r'^"([^"]+)"$')
ENV_STRING_RE = re.compile(r'envString\s*\(\s*"([A-Z0-9_]+)"\s*\)')


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def resolve(schema: dict, ref: str) -> dict:
    assert ref.startswith("#/")
    node: Any = schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _is_uri(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return bool(parsed.netloc)
    return bool(parsed.scheme)


def validate(node: Any, sub: dict, root: dict, path: str, errs: list[str]) -> None:
    if "$ref" in sub:
        validate(node, resolve(root, sub["$ref"]), root, path, errs)
        return

    if "oneOf" in sub:
        matches = 0
        for option in sub["oneOf"]:
            option_errs: list[str] = []
            validate(node, option, root, path, option_errs)
            if not option_errs:
                matches += 1
        if matches != 1:
            errs.append(
                f"{path}: expected exactly one matching schema in oneOf, got {matches}"
            )
        return

    if "anyOf" in sub:
        matches = 0
        for option in sub["anyOf"]:
            anyof_errs: list[str] = []
            validate(node, option, root, path, anyof_errs)
            if not anyof_errs:
                matches += 1
        if matches == 0:
            errs.append(f"{path}: expected at least one matching schema in anyOf")
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
        if sub.get("format") == "uri" and not _is_uri(node):
            errs.append(f"{path}: expected uri format")
    elif t == "integer":
        if not isinstance(node, int) or isinstance(node, bool):
            errs.append(f"{path}: expected integer")
            return
        if "minimum" in sub and node < sub["minimum"]:
            errs.append(f"{path}: below minimum {sub['minimum']}")
    elif t == "null":
        if node is not None:
            errs.append(f"{path}: expected null")
            return
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


def load_rpc_aliases() -> dict[str, str]:
    if not FOUNDRY_TOML.exists():
        return {}
    text = FOUNDRY_TOML.read_text()
    return {alias: env for alias, env in RPC_ENDPOINT_RE.findall(text)}


def _eval_int_expr(expr: str, symbols: dict[str, int]) -> int | None:
    expr = expr.strip()
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None

    def walk(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, int)
            and not isinstance(node.value, bool)
        ):
            return node.value
        if isinstance(node, ast.Name) and node.id in symbols:
            return symbols[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return walk(node.operand)
        if isinstance(node, ast.BinOp):
            left = walk(node.left)
            right = walk(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, (ast.Div, ast.FloorDiv)) and right != 0:
                return left // right
        raise ValueError

    try:
        return walk(tree)
    except ValueError:
        return None


def extract_evm_fork_metadata(
    path: Path, env_to_alias: dict[str, str]
) -> tuple[str | None, int | None]:
    text = path.read_text()

    int_symbols: dict[str, int] = {}
    for _ in range(3):
        progressed = False
        for name, expr in UINT_DECL_RE.findall(text):
            if name in int_symbols:
                continue
            value = _eval_int_expr(expr, int_symbols)
            if value is not None:
                int_symbols[name] = value
                progressed = True
        if not progressed:
            break

    string_symbols = {name: value for name, value in STRING_DECL_RE.findall(text)}

    match = FORK_CALL_RE.search(text)
    if not match:
        return None, None

    alias_expr = match.group(1).strip()
    block_expr = match.group(2).strip()

    alias: str | None = None
    literal = STRING_LITERAL_RE.fullmatch(alias_expr)
    env = ENV_STRING_RE.search(alias_expr)
    if literal:
        alias = literal.group(1)
    elif env:
        alias = env_to_alias.get(env.group(1), env.group(1))
    elif alias_expr in string_symbols:
        alias = string_symbols[alias_expr]

    block = _eval_int_expr(block_expr, int_symbols)
    return alias, block


def repo_rules(reg: dict, errs: list[str]) -> None:
    seen_ids: set[str] = set()
    rpc_aliases = load_rpc_aliases()
    env_to_alias = {env: alias for alias, env in rpc_aliases.items()}
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

            declared_alias = e.get("rpc_alias")
            if declared_alias and rpc_aliases and declared_alias not in rpc_aliases:
                errs.append(
                    f"{ep}: rpc_alias {declared_alias!r} is not declared in EVM/foundry.toml"
                )

            poc = e.get("poc_path")
            full_poc = REPO_ROOT / poc if poc else None
            if full_poc and full_poc.exists():
                source_alias, source_block = extract_evm_fork_metadata(
                    full_poc, env_to_alias
                )
                if source_alias is None:
                    errs.append(
                        f"{ep}: could not detect createSelectFork RPC alias in {poc}"
                    )
                elif declared_alias and source_alias != declared_alias:
                    errs.append(
                        f"{ep}: rpc_alias mismatch: metadata={declared_alias!r}, "
                        f"source={source_alias!r} in {poc}"
                    )

                declared_block = e.get("block_number")
                if source_block is None:
                    errs.append(
                        f"{ep}: could not detect createSelectFork block in {poc}"
                    )
                elif declared_block != source_block:
                    errs.append(
                        f"{ep}: block_number mismatch: metadata={declared_block!r}, "
                        f"source={source_block!r} in {poc}"
                    )

        if status not in ("embargoed", "educational", "template"):
            if not e.get("references"):
                errs.append(
                    f"{ep}: at least one reference required for status={status!r}"
                )


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
