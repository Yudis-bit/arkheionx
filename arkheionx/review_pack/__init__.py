"""Arkheionx v8 — one-command review pack (`arkheionx review`).

`arkheionx review` is the primary entry point. It turns a local repository (plus an
optional scope note and an optional generic protocol-family lens) into a single,
numbered, human-readable review pack and machine-readable `review.json` and
`manifest.json`.

It orchestrates the existing layers rather than adding new analysis:

- the review map (contracts, value paths, assumptions, interactions),
- scope-aware orchestration (scope map, review lanes, evidence tasks, evidence
  rubric, report filter),
- and, when ``--lens`` is given, a protocol lens (protocol model, behavior
  promises, economic invariants, temporal windows, lens lanes, lens tasks).

Everything is local/static and heuristic. A review pack is a planning artifact, not
a finding. A review lane is not a vulnerability. Evidence quality is not
vulnerability validity. No RPC, no live-chain calls, no exploit automation, no
auto-submit. Human review is required.
"""
from __future__ import annotations

from .builder import (
    ARTIFACT_TYPE,
    CORE_ARTIFACTS,
    EXIT_CODE_SEMANTICS,
    LENS_ARTIFACTS,
    SCHEMA_VERSION,
    build_interaction_payload,
    build_review_pack,
    default_review_dir,
)

__all__ = [
    "build_review_pack",
    "build_interaction_payload",
    "default_review_dir",
    "CORE_ARTIFACTS",
    "LENS_ARTIFACTS",
    "SCHEMA_VERSION",
    "ARTIFACT_TYPE",
    "EXIT_CODE_SEMANTICS",
]
