"""Generic bounty-policy carve-outs consumed by the reality gate."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field


@dataclass
class ProgramPolicy:
    excludes_key_reuse: bool = False
    excludes_offchain_validation: bool = False
    excludes_trusted_role: bool = False
    excludes_forced_value_transfer: bool = False
    excludes_gas_only: bool = False
    excludes_precision_only: bool = False
    excluded_tags: list = field(default_factory=list)
    in_scope: bool | None = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_object(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            fields = {f.name for f in dataclasses.fields(cls)}
            return cls(**{k: v for k, v in value.items() if k in fields})
        return cls()
