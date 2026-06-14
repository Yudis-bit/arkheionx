"""Foundry PoC skeleton assembler (Layer 6).

Generates one ``.t.sol`` skeleton per top candidate. Skeletons are honest:
``compile_ready_level`` is ``requires_manual_fill`` — they encode the right
actors, setup, action sequence, and invariant assertions, but need the target
import, constructor args, and TODO values filled in. No broadcast, no keys.
"""
from __future__ import annotations

import re

from . import actors, assertions, setup_builder
from .models import PoCSkeleton, REQUIRES_MANUAL_FILL, TEMPLATE_ONLY, NEAR_COMPILE


def _contract_of(qn: str) -> str:
    return qn.split(".")[0] if qn else "Target"


def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", s)


def build_skeleton(candidate, smap=None) -> PoCSkeleton:
    family = candidate.invariant_family
    contract = _contract_of(candidate.entry_function)
    actor_names = actors.actors_for(family)
    setup_sol = setup_builder.setup_solidity(family, contract)
    action = assertions.action_sequence(family)
    assert_lines = assertions.assertion_lines(family)
    test_name = f"test_{_safe(family).lower()}"
    file_name = f"Candidate_{candidate.id}_{_safe(family)[:28]}.t.sol"
    test_contract = f"PoC_{candidate.id.replace('-', '')}_{_safe(family)[:24]}"

    # Honest compile-readiness: a structured family (dedicated actions+assertions and
    # named actors) is NEAR_COMPILE (needs only the target import / constructor / TODO
    # values); otherwise TEMPLATE_ONLY. Never COMPILE_LIKELY/FIXTURE_TESTED_COMPILE —
    # we never claim a skeleton compiles or passes without an executed test.
    readiness = NEAR_COMPILE if (assertions.has_specific_assertions(family)
                                 and actor_names) else TEMPLATE_ONLY
    severity_line = candidate.economic_severity or candidate.severity_hint or "see economic gate"

    fork_env = []
    header = [
        "// SPDX-License-Identifier: MIT",
        "pragma solidity ^0.8.20;",
        "",
        'import "forge-std/Test.sol";',
        "",
        f"// Arkheionx V10 PoC skeleton — candidate {candidate.id} [{family}]",
        f"// Broken invariant: {candidate.broken_invariant}",
        f"// Attacker: {candidate.attacker_capability} | Victim: {candidate.victim} | "
        f"Asset: {candidate.asset}",
        f"// Entry: {candidate.entry_function} | Proof: {candidate.proof_strategy}",
        f"// Economic severity (pre-proof gate): {severity_line}",
        f"// Compile-readiness: {readiness} (SKELETON, not a passing PoC).",
        "// EXPECTED: with the bug present the invariant assertion below should FAIL",
        "//   (that failure is the proof); against a fixed target it should PASS.",
        "// SKELETON ONLY — will not compile unmodified. MANUAL FILL: the target import,",
        "// constructor args, and TODO markers. Local simulation only: no broadcast,",
        "// no private keys, no live network.",
    ]
    if candidate.fork_requirement:
        fork_env = ["FORK_RPC_URL (env var name only; never hardcode the URL)"]
        header += [
            "// FORK REQUIRED: set the fork RPC via an env var (name only). Use",
            "//   vm.createSelectFork(vm.envString(\"FORK_RPC_URL\")); in setUp().",
            "// SECRET REDACTION: never commit the RPC URL, key, or mnemonic — env name only.",
        ]

    body = [f"contract {test_contract} is Test {{", ""]
    body += ["    " + d for d in actors.actor_decls(actor_names)]
    body += ["", "    function setUp() public {"]
    if candidate.fork_requirement:
        body += ['        // vm.createSelectFork(vm.envString("FORK_RPC_URL"));']
    body += ["        " + ln for ln in setup_sol]
    body += ["    }", "", f"    function {test_name}() public {{"]
    body += ["        " + ln for ln in action]
    body += [""]
    body += ["        " + ln for ln in assert_lines]
    body += ["    }", "}"]

    source = "\n".join(header + [""] + body) + "\n"

    return PoCSkeleton(
        candidate_id=candidate.id, family=family, test_name=test_name, file_name=file_name,
        actors=actor_names, setup_steps=setup_builder.setup_steps(family, contract),
        action_sequence=action, assertions=assert_lines,
        required_mocks=["target contract import + constructor", "mock ERC20(s) as noted"],
        required_fork_env=fork_env,
        comments=[
            f"Severity context: {severity_line}",
            f"Compile-readiness: {readiness} (skeleton, not a passing PoC).",
            "Expected: the invariant assertion fails on the vulnerable target.",
        ],
        source=source, confidence=candidate.confidence,
        compile_ready_level=REQUIRES_MANUAL_FILL,
        compile_readiness=readiness,
    )


def build_skeletons(graph, smap=None, top_n=5, include_role_gated=False) -> list:
    out = []
    count = 0
    for c in graph.candidates:
        if count >= top_n:
            break
        if c.role_gated and not include_role_gated:
            continue  # role-gated candidates are killed; no PoC by default
        out.append(build_skeleton(c, smap))
        c.poc_skeleton = f"11-poc-skeletons/{out[-1].file_name}"
        count += 1
    return out
