"""Scope loading for war-run (Layer 10).

Parses a small YAML subset (the documented scope.yaml shape) without PyYAML,
since the package ships with no third-party dependencies. Also accepts JSON.
If no scope is provided, the run is unscoped and a warning is recorded.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


def _scalar(v: str):
    v = v.strip()
    if v == "":
        return None
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v.strip("\"'")


class _Lines:
    def __init__(self, raw: str):
        self.items = []
        for ln in raw.splitlines():
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            indent = len(ln) - len(ln.lstrip(" "))
            self.items.append((indent, ln.strip()))
        self.i = 0

    def peek(self):
        return self.items[self.i] if self.i < len(self.items) else (None, None)

    def next(self):
        it = self.items[self.i]
        self.i += 1
        return it


def _parse(lines: _Lines):
    indent, content = lines.peek()
    if indent is None:
        return None
    if content.startswith("- "):
        return _parse_list(lines, indent)
    return _parse_map(lines, indent)


def _parse_map(lines: _Lines, indent: int):
    d = {}
    while True:
        ind, content = lines.peek()
        if ind is None or ind < indent or ind > indent or content.startswith("- "):
            break
        lines.next()
        key, _, val = content.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            child_ind, _ = lines.peek()
            d[key] = _parse(lines) if (child_ind is not None and child_ind > indent) else None
        else:
            d[key] = _scalar(val)
    return d


def _parse_list(lines: _Lines, indent: int):
    out = []
    while True:
        ind, content = lines.peek()
        if ind is None or ind != indent or not content.startswith("- "):
            break
        lines.next()
        item = content[2:].strip()
        if ":" in item and not item.startswith(("\"", "'")):
            key, _, val = item.partition(":")
            m = {}
            key, val = key.strip(), val.strip()
            if val == "":
                child_ind, _ = lines.peek()
                m[key] = _parse(lines) if (child_ind is not None and child_ind > indent) else None
            else:
                m[key] = _scalar(val)
            while True:
                ind2, content2 = lines.peek()
                if ind2 is None or ind2 <= indent or content2.startswith("- "):
                    break
                lines.next()
                k2, _, v2 = content2.partition(":")
                k2, v2 = k2.strip(), v2.strip()
                if v2 == "":
                    child_ind, _ = lines.peek()
                    m[k2] = _parse(lines) if (child_ind is not None and child_ind > ind2) else None
                else:
                    m[k2] = _scalar(v2)
            out.append(m)
        else:
            out.append(_scalar(item))
    return out


def parse_yaml_subset(text: str) -> dict:
    lines = _Lines(text)
    result = _parse(lines)
    return result if isinstance(result, dict) else {}


@dataclass
class ScopeModel:
    present: bool = False
    name: str = ""
    platform: str = ""
    chain: str = ""
    in_scope_paths: list = field(default_factory=list)
    in_scope_contracts: list = field(default_factory=list)
    out_of_scope_text: list = field(default_factory=list)
    out_of_scope_contracts: list = field(default_factory=list)
    known_reports: list = field(default_factory=list)
    rules: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)

    def as_context(self) -> dict:
        return {
            "chain": self.chain,
            "out_of_scope_contracts": self.out_of_scope_contracts,
            "contracts": [{"name": c} for c in self.in_scope_contracts],
        }

    def to_dict(self) -> dict:
        return {
            "present": self.present, "name": self.name, "platform": self.platform,
            "chain": self.chain, "in_scope_paths": self.in_scope_paths,
            "in_scope_contracts": self.in_scope_contracts,
            "out_of_scope_text": self.out_of_scope_text,
            "out_of_scope_contracts": self.out_of_scope_contracts,
            "known_reports": self.known_reports, "rules": self.rules,
            "warnings": self.warnings,
        }


def load_scope(scope_file: str | None) -> ScopeModel:
    sm = ScopeModel()
    if not scope_file:
        sm.warnings.append("No scope file provided; running unscoped (all .sol under target).")
        return sm
    p = Path(scope_file).expanduser()
    if not p.is_file():
        sm.warnings.append(f"Scope file not found: {scope_file}; running unscoped.")
        return sm
    text = p.read_text(encoding="utf-8", errors="ignore")
    try:
        data = json.loads(text) if p.suffix == ".json" else parse_yaml_subset(text)
    except (ValueError, IndexError):
        sm.warnings.append("Scope file could not be parsed; running unscoped.")
        return sm
    if not isinstance(data, dict):
        sm.warnings.append("Scope file is not a mapping; running unscoped.")
        return sm

    sm.present = True
    sm.raw = data
    program = data.get("program") or {}
    if isinstance(program, dict):
        sm.name = str(program.get("name", "") or "")
        sm.platform = str(program.get("platform", "") or "")
    sm.chain = str(data.get("chain") or data.get("network") or (program.get("chain", "") if isinstance(program, dict) else "") or "")
    for entry in (data.get("in_scope") or []):
        if isinstance(entry, dict):
            if entry.get("path"):
                sm.in_scope_paths.append(str(entry["path"]))
            for c in (entry.get("contracts") or []):
                sm.in_scope_contracts.append(str(c))
        elif isinstance(entry, str):
            sm.in_scope_paths.append(entry)
    for entry in (data.get("out_of_scope") or []):
        if isinstance(entry, str):
            sm.out_of_scope_text.append(entry)
            # contract-like token (CamelCase or ALLCAPS) -> out-of-scope contract
            for tok in re.findall(r"\b(?:[A-Z][a-z0-9_]*[A-Z][A-Za-z0-9_]*|[A-Z]{3,})\b", entry):
                sm.out_of_scope_contracts.append(tok)
        elif isinstance(entry, dict) and entry.get("contract"):
            sm.out_of_scope_contracts.append(str(entry["contract"]))
    for entry in (data.get("known_reports") or []):
        if isinstance(entry, dict) and entry.get("path"):
            sm.known_reports.append(str(entry["path"]))
        elif isinstance(entry, str):
            sm.known_reports.append(entry)
    rules = data.get("rules") or {}
    if isinstance(rules, dict):
        sm.rules = rules
    return sm
