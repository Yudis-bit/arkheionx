"""Generate conservative Foundry proof scaffolds.

The scaffold compiles intent into test stubs that are explicitly skipped
(`vm.skip(true)`) with TODOs. It never asserts true just to pass and never
claims EXECUTION_CONFIRMED until a real run is parsed.
"""
from __future__ import annotations

import re

_HEADER = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Arkheionx generated proof scaffold (HEURISTIC).
// This is a starting point, not a proof. Replace TODOs, bind the real
// contract/mocks, then run: forge test --match-contract {harness}
import "forge-std/Test.sol";

contract {harness} is Test {{
    // TODO: deploy the target contract and any required mocks here.
    function setUp() public {{
        // TODO: instantiate {contract} and fund test actors.
    }}
"""

_FOOTER = "}\n"


def _camel(text: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", text)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Target"


def _test_name(title: str, index: int) -> str:
    slug = _camel(title)[:40]
    return f"test_{index:02d}_{slug}"


def harness_name(contract: str, function: str) -> str:
    return f"Arkheionx{_camel(contract)}{_camel(function)}ProofTest"


def generate_scaffold(contract: str, function: str, suggested_tests: list[str], invariants: list[str]) -> str:
    harness = harness_name(contract, function)
    body = [_HEADER.format(harness=harness, contract=contract or "Target")]
    tests = suggested_tests or [f"Exercise {function}() and assert state deltas"]
    for index, title in enumerate(tests, start=1):
        safe_title = title.replace("\\", " ").replace('"', "'")
        body.append(f"\n    // {safe_title}")
        body.append(f"    function {_test_name(title, index)}() public {{")
        body.append('        vm.skip(true); // TODO: implement; remove skip when ready.')
        body.append(f"        // Arrange / Act / Assert for {function}().")
        body.append("    }")
    for index, inv in enumerate(invariants, start=1):
        safe_inv = inv.replace("\\", " ").replace('"', "'")
        body.append(f"\n    // invariant candidate: {safe_inv}")
        body.append(f"    function invariant_{index:02d}_property() public {{")
        body.append('        vm.skip(true); // TODO: wire StdInvariant targets and assert property.')
        body.append("    }")
    body.append(_FOOTER)
    return "\n".join(body)
