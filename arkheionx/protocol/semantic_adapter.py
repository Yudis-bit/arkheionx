"""Semantic adapter: produce semantic-lite contract data for the workbench.

Two sources are supported:

* Re-parse Solidity sources locally (default). The output mirrors the legacy
  scanner ``semantic_lite`` shape so artifacts stay consistent.
* Load an existing Arkheionx scan report JSON (``--from-report``) and reuse its
  ``semantic_lite.contracts`` directly.

This module is intentionally self-contained (stdlib only) so the workbench
stays inside the installable package and does not import the monolithic
scanner.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

_IGNORED_DIRS = {"lib", "out", "cache", "node_modules", ".git", "broadcast", ".venv"}

_EXTERNAL_TERMS = (
    "transferFrom",
    "safeTransferFrom",
    "safeTransfer",
    "transfer",
    "send",
    ".call(",
    "call{",
    "delegatecall",
    "flashLoan",
    "executeOperation",
)
_ORACLE_TERMS = (
    "latestRoundData",
    "latestAnswer",
    "getPrice",
    "getReserves",
    "observe",
    "consult",
    "sqrtPriceX96",
)
_IGNORED_CALLS = {"if", "for", "while", "require", "assert", "revert", "emit", "return", "new", "delete"}


def _line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(text) - 1


def _extract_state_variables(contract_body: str) -> list[str]:
    without_functions = re.sub(r"\b(function|constructor)\b[\s\S]*?{[\s\S]*?}", "", contract_body)
    variables: set[str] = set()
    for match in re.finditer(
        r"^\s*(?:mapping\s*\([^;]+?\)|[A-Za-z_][A-Za-z0-9_<>,\[\].]*)\s+"
        r"(?:(?:public|private|internal|external|immutable|constant|override)\s+)*"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|;)",
        without_functions,
        flags=re.MULTILINE,
    ):
        name = match.group(1)
        if name not in {"function", "returns", "modifier", "event", "error", "struct"}:
            variables.add(name)
    return sorted(variables)


def _extract_calls(function_body: str) -> list[str]:
    calls = {
        m.group(1)
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", function_body)
        if m.group(1) not in _IGNORED_CALLS
    }
    dot_calls = {
        m.group(1)
        for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", function_body)
        if m.group(1) not in _IGNORED_CALLS
    }
    return sorted(calls | dot_calls)


def _signature(name: str, raw_params: str) -> str:
    params = []
    for part in raw_params.split(","):
        tokens = part.strip().split()
        if tokens:
            params.append(tokens[0])
    return f"{name}({','.join(params)})"


def _parse_functions(contract_body: str, file_text: str, body_offset: int, state_variables: list[str]) -> list[dict]:
    functions: list[dict] = []
    pattern = re.compile(r"\b(function|constructor)\s+([A-Za-z_][A-Za-z0-9_]*)?\s*\(([^;{}]*)\)\s*([^;{]*){", re.MULTILINE)
    for match in pattern.finditer(contract_body):
        open_index = body_offset + match.end() - 1
        close_index = _find_matching_brace(file_text, open_index)
        body = file_text[open_index + 1 : close_index]
        name = match.group(2) or "constructor"
        raw_params = match.group(3) or ""
        tail = match.group(4) or ""
        visibility = "unspecified"
        for candidate in ("external", "public", "internal", "private"):
            if re.search(rf"\b{candidate}\b", tail):
                visibility = candidate
                break
        modifiers = [
            token
            for token in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", tail)
            if token not in {"external", "public", "internal", "private", "view", "pure", "payable", "virtual", "override", "returns"}
        ]
        writes_state = [
            v for v in state_variables
            if re.search(rf"\b{re.escape(v)}\b\s*(?:=|\+=|-=|\*=|/=|\+\+|--|\[)", body)
        ]
        reads_state = [v for v in state_variables if re.search(rf"\b{re.escape(v)}\b", body)]
        external_calls = sorted({t for t in _EXTERNAL_TERMS if t in body})
        oracle_calls = sorted({t for t in _ORACLE_TERMS if t in body})
        functions.append(
            {
                "name": name,
                "signature": _signature(name, raw_params),
                "visibility": visibility,
                "modifiers": sorted(set(modifiers)),
                "payable": bool(re.search(r"\bpayable\b", tail)),
                "line_start": _line_for_offset(file_text, body_offset + match.start()),
                "line_end": _line_for_offset(file_text, close_index),
                "body_excerpt_hash": hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:16],
                "calls": _extract_calls(body)[:40],
                "external_calls": external_calls,
                "oracle_calls": oracle_calls,
                "writes_state": sorted(set(writes_state)),
                "reads_state": sorted(set(reads_state)),
            }
        )
    return functions


def parse_contracts(text: str, file_rel: str) -> list[dict]:
    """Parse Solidity ``text`` into a list of semantic-lite contract dicts."""

    contracts: list[dict] = []
    pattern = re.compile(r"\b(abstract\s+contract|contract|interface|library)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+is\s+([^{]+))?\s*{")
    for match in pattern.finditer(text):
        open_index = match.end() - 1
        close_index = _find_matching_brace(text, open_index)
        body = text[open_index + 1 : close_index]
        inherits = []
        if match.group(3):
            inherits = [item.strip().split()[0] for item in match.group(3).split(",") if item.strip()]
        state_variables = _extract_state_variables(body)
        contracts.append(
            {
                "name": match.group(2),
                "file": file_rel,
                "kind": match.group(1).replace("abstract ", ""),
                "inherits": inherits,
                "line_start": _line_for_offset(text, match.start()),
                "line_end": _line_for_offset(text, close_index),
                "state_variables": state_variables,
                "functions": _parse_functions(body, text, open_index + 1, state_variables),
            }
        )
    return contracts


def _is_test_path(rel_path: str) -> bool:
    parts = rel_path.split("/")
    return rel_path.endswith((".t.sol", ".test.sol")) or "test" in parts or "tests" in parts


def find_solidity_files(root: Path) -> tuple[list[Path], list[Path]]:
    """Return ``(sources, tests)`` Solidity files under ``root``."""

    sources: list[Path] = []
    tests: list[Path] = []
    for path in sorted(root.rglob("*.sol")):
        parts = set(path.relative_to(root).parts)
        if parts & _IGNORED_DIRS:
            continue
        rel = path.relative_to(root).as_posix()
        (tests if _is_test_path(rel) else sources).append(path)
    return sources, tests


def load_semantic(root: Path, from_report: Path | None = None) -> dict:
    """Build the semantic-lite structure for ``root``.

    Returns ``{"contracts": [...], "warnings": [...], "source": str}``.
    """

    if from_report is not None:
        try:
            payload = json.loads(from_report.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return {"contracts": [], "warnings": [f"could not read report {from_report}: {exc}"], "source": "report"}
        semantic = payload.get("semantic_lite") if isinstance(payload, dict) else None
        contracts = semantic.get("contracts", []) if isinstance(semantic, dict) else []
        if contracts:
            return {"contracts": contracts, "warnings": [], "source": "report"}
        return {"contracts": [], "warnings": ["report has no semantic_lite.contracts"], "source": "report"}

    sources, _tests = find_solidity_files(root)
    contracts: list[dict] = []
    warnings: list[str] = []
    for path in sources:
        rel = path.relative_to(root).as_posix()
        try:
            contracts.extend(parse_contracts(path.read_text(encoding="utf-8", errors="ignore"), rel))
        except Exception as exc:  # defensive: never fail the whole command
            warnings.append(f"parse warning for {rel}: {exc}")
    return {"contracts": contracts, "warnings": warnings, "source": "static"}
