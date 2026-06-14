"""Root-cause memory file store (Layer 9).

Persists prior findings/kills/parks/out-of-scope under .arkheionx/memory/ as JSON
lists of :class:`MemoryEntry`. Local files only.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import root_cause_hash as rch
from .models import MemoryEntry

_FILES = {
    "findings": "findings.json",
    "killed": "killed-leads.json",
    "parked": "parked-candidates.json",
    "out_of_scope": "out-of-scope.json",
}


class MemoryStore:
    def __init__(self, base_dir):
        self.base = Path(base_dir)

    def _path(self, category):
        return self.base / _FILES.get(category, f"{category}.json")

    def load(self, category) -> list:
        p = self._path(category)
        if not p.is_file():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        return [MemoryEntry.from_dict(d) for d in data if isinstance(d, dict)]

    def all_entries(self) -> list:
        out = []
        for cat in _FILES:
            out.extend(self.load(cat))
        return out

    def add(self, category, entry: MemoryEntry, write: bool = True) -> MemoryEntry:
        if not entry.root_cause_hash and entry.invariant_family:
            entry.root_cause_hash = rch.root_cause_hash(
                entry.invariant_family, entry.function_role, entry.attacker_category)
        if write:
            self.base.mkdir(parents=True, exist_ok=True)
            existing = self.load(category)
            existing.append(entry)
            self._path(category).write_text(
                json.dumps([e.to_dict() for e in existing], indent=2) + "\n", encoding="utf-8")
        return entry

    def known_hashes(self) -> dict:
        """root_cause_hash -> MemoryEntry (first wins)."""
        out = {}
        for e in self.all_entries():
            if e.root_cause_hash and e.root_cause_hash not in out:
                out[e.root_cause_hash] = e
        return out

    def out_of_scope_contracts(self) -> set:
        names = set()
        for e in self.load("out_of_scope"):
            for c in e.affected_contracts:
                names.add(c)
        return names
