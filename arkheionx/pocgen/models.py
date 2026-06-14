"""PoC skeleton models (Layer 6)."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

# Honest compile-readiness ladder.
TEMPLATE_ONLY = "template_only"
NEAR_COMPILE = "near_compile"
COMPILE_LIKELY = "compile_likely"
REQUIRES_MANUAL_FILL = "requires_manual_fill"


@dataclass
class PoCSkeleton:
    candidate_id: str = ""
    family: str = ""
    test_name: str = ""
    file_name: str = ""
    actors: list = field(default_factory=list)
    setup_steps: list = field(default_factory=list)
    action_sequence: list = field(default_factory=list)
    assertions: list = field(default_factory=list)
    required_mocks: list = field(default_factory=list)
    required_fork_env: list = field(default_factory=list)
    comments: list = field(default_factory=list)
    source: str = ""           # the .t.sol text
    confidence: str = "MEDIUM"
    compile_ready_level: str = REQUIRES_MANUAL_FILL

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
