"""Execute a target's tests via Foundry and assign honest status + evidence.

EXECUTION_CONFIRMED is assigned only when at least one relevant test actually
executed (passed or failed). Skipped or unmatched tests are never proof.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from arkheionx.protocol import foundry as foundry_mod
from arkheionx.protocol.model import COMPILER_CONFIRMED, EXECUTION_CONFIRMED, HEURISTIC

from .trace import parse_forge_output


@dataclass
class ExecResult:
    status: str = "no_foundry"
    evidence_level: str = HEURISTIC
    build_status: str = "not_attempted"
    ran: bool = False
    test_command: str = ""
    build_output: str = ""
    test_output: str = ""
    trace: dict = field(default_factory=dict)
    foundry: foundry_mod.FoundryStatus = field(default_factory=foundry_mod.FoundryStatus)


def execute_target(root: Path, function_name: str, timeout: int = 300) -> ExecResult:
    fs = foundry_mod.detect_foundry(root, with_version=True)
    result = ExecResult(foundry=fs)
    if fs.status not in {foundry_mod.AVAILABLE_NOT_BUILT, foundry_mod.BUILD_PASSED}:
        result.status = "no_foundry"
        return result

    passed_build, build_out = foundry_mod.run_build(root, timeout=timeout)
    result.build_output = build_out
    if not passed_build:
        result.status = "build_failed"
        result.build_status = "build_failed"
        return result
    result.build_status = "build_passed"
    result.evidence_level = COMPILER_CONFIRMED

    match = f"(?i){re.escape(function_name)}"
    rc, output, command = foundry_mod.run_test(root, match_test=match, timeout=timeout)
    result.test_command = command
    result.test_output = output
    trace = parse_forge_output(output)
    result.trace = trace

    executed = trace["passed"] + trace["failed"]
    total = trace["tests_run"]
    if total == 0:
        result.status = "no_tests_matched"
    elif executed == 0:
        result.status = "skipped_not_proof"
    else:
        result.ran = True
        result.evidence_level = EXECUTION_CONFIRMED
        if trace["failed"] == 0:
            result.status = "tested_passed"
        elif trace["passed"] == 0:
            result.status = "tested_failed"
        else:
            result.status = "tested_mixed"
    return result
