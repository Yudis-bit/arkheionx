"""Root-cause memory file store (Layer 9).

Persists prior findings/kills/parks/out-of-scope under .arkheionx/memory/ as JSON
lists of :class:`MemoryEntry`. Local files only.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import root_cause_fingerprint as rcf
from .models import MemoryEntry

_FILES = {
    "findings": "findings.json",
    "killed": "killed-leads.json",
    "parked": "parked-candidates.json",
    "out_of_scope": "out-of-scope.json",
}


def _ensure_fingerprint(entry: MemoryEntry) -> MemoryEntry:
    if entry.root_cause_hash and (entry.root_cause_family or entry.invariant_family):
        return entry
    fp = rcf.build_fingerprint(
        entry.root_cause,
        explicit_family=entry.root_cause_family or entry.invariant_family,
        affected_function=entry.affected_function or entry.function_role,
        affected_asset_type=entry.affected_asset_type,
        attacker_capability=entry.attacker_capability or entry.attacker_category,
        victim_type=entry.victim_type,
        impact_path=entry.impact_path,
        cap_type=entry.cap_type,
        proof_status=entry.proof_status,
        program_outcome=entry.program_outcome or entry.status,
    )
    entry.root_cause_hash = fp.fingerprint_hash
    entry.normalized_root_cause = entry.normalized_root_cause or fp.normalized_text
    entry.root_cause_family = entry.root_cause_family or fp.family
    entry.root_cause_subfamily = entry.root_cause_subfamily or fp.subfamily
    entry.lifecycle = entry.lifecycle or fp.lifecycle
    entry.affected_function = entry.affected_function or fp.affected_function
    entry.affected_asset_type = entry.affected_asset_type or fp.affected_asset_type
    entry.attacker_capability = entry.attacker_capability or fp.attacker_capability
    entry.victim_type = entry.victim_type or fp.victim_type
    entry.impact_path = entry.impact_path or fp.impact_path
    entry.cap_type = entry.cap_type or fp.cap_type
    entry.proof_status = entry.proof_status or fp.proof_status
    entry.program_outcome = entry.program_outcome or fp.program_outcome
    entry.fingerprint_confidence = entry.fingerprint_confidence or fp.confidence
    entry.fingerprint_warnings = entry.fingerprint_warnings or fp.warnings
    if not entry.invariant_family:
        entry.invariant_family = fp.family
    return entry


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
        return [
            _ensure_fingerprint(MemoryEntry.from_dict(d))
            for d in data if isinstance(d, dict)
        ]

    def all_entries(self) -> list:
        out = []
        for cat in _FILES:
            out.extend(self.load(cat))
        return out

    def add(self, category, entry: MemoryEntry, write: bool = True) -> MemoryEntry:
        entry = _ensure_fingerprint(entry)
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
