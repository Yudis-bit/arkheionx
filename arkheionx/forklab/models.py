"""Fork-lab models (Layer 8).

A :class:`ForkRequirement` says when local-only proof is insufficient and what a
fork test must verify. It never carries an RPC URL or a private key — only env
var *names* — and always sets ``do_not_broadcast``.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field


@dataclass
class ForkRequirement:
    candidate_id: str = ""
    chain: str = "unknown"
    required_env: list = field(default_factory=list)   # env var NAMES only
    reason: str = ""
    contracts_to_verify: list = field(default_factory=list)
    static_calls_needed: list = field(default_factory=list)
    candidate_tests: list = field(default_factory=list)
    do_not_broadcast: bool = True
    secret_redaction_required: bool = True

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
