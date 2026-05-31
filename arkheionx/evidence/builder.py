"""Build a structured evidence package from proof + trace artifacts."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.proof.payloads import target_slug
from arkheionx.protocol.model import COMPILER_CONFIRMED, EXECUTION_CONFIRMED, HEURISTIC
from arkheionx.version import __version__

from . import model as M
from .model import EvidencePackage


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _bug_classes_for(target_id: str, analysis) -> tuple[str, str, list[str], int]:
    """Return (role, money_flow_role, bug_classes, score) from analysis context."""
    role = ""
    score = 0
    bug_classes: list[str] = []
    for t in analysis.hunter_targets:
        if t.target_id == target_id:
            bug_classes = list(t.bug_classes)
            score = t.score
            break
    fr = next((f for f in analysis.all_functions if f.function_id == target_id), None)
    if fr is not None:
        role = fr.role
    flow = analysis.money_flow
    money_role = "internal"
    if target_id in flow.entrypoints:
        money_role = "entry"
    elif target_id in flow.exits:
        money_role = "exit"
    elif target_id in flow.privileged_movers:
        money_role = "privileged"
    elif target_id in flow.pricing_dependencies:
        money_role = "pricing"
    return role, money_role, bug_classes, score


def build_evidence(match, root: Path, writer: ArtifactWriter, analysis, write: bool = True,
                   proof_override: dict | None = None, trace_override: dict | None = None) -> EvidencePackage:
    slug = target_slug(match.display_id)
    proof = proof_override if proof_override is not None else _read_json(writer.path_for(f"proof/{slug}/proof.json"))
    trace = trace_override if trace_override is not None else _read_json(writer.path_for(f"proof/{slug}/trace.json"))

    if proof is None:
        pkg = EvidencePackage(
            target=match.qualified_id,
            target_id=match.stable_id or match.display_id,
            evidence_level=HEURISTIC,
            status=M.NO_PROOF,
            next_command=f"arkheionx prove . --target {match.display_id} --run",
        )
        return pkg

    proof_level = proof.get("evidence_level", HEURISTIC)
    trace_found = trace is not None
    if proof_level == EXECUTION_CONFIRMED and trace_found:
        evidence_level = M.EVIDENCE_READY
        status = M.EVIDENCE_READY_STATUS
    elif proof_level == EXECUTION_CONFIRMED:
        evidence_level = EXECUTION_CONFIRMED
        status = M.EXECUTION_CONFIRMED
    elif proof_level == COMPILER_CONFIRMED:
        evidence_level = COMPILER_CONFIRMED
        status = M.COMPILER_CONFIRMED_ONLY
    else:
        evidence_level = HEURISTIC
        status = M.SCAFFOLD_ONLY

    test_result = proof.get("test_result", {})
    role, money_role, bug_classes, score = _bug_classes_for(match.stable_id or match.display_id, analysis)
    line_range = getattr(match, "line_range", []) or []
    affected = f"{match.contract_name}.{match.function_name}"
    if match.file_path:
        loc = f"#L{line_range[0]}-L{line_range[1]}" if len(line_range) == 2 and line_range[0] else ""
        affected = f"{match.file_path}:{affected}{loc}"

    candidate_impact = "; ".join(bug_classes) if bug_classes else "value-flow review surface"
    payload = {
        "schema_version": "1.0.0",
        "arkheionx_version": __version__,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "project_root": str(root),
        "target": match.qualified_id,
        "target_id": match.stable_id or match.display_id,
        "evidence_level": evidence_level,
        "status": status,
        "source_artifacts": {
            "proof_json": str(writer.path_for(f"proof/{slug}/proof.json")),
            "trace_json": str(writer.path_for(f"proof/{slug}/trace.json")) if trace_found else "",
            "raw_foundry_output": (proof.get("test_result", {}) or {}).get("raw_output_path", ""),
            "generated_test": next((f for f in proof.get("generated_files", []) if f.endswith(".sol")), ""),
        },
        "proof_summary": {
            "status": proof.get("status", ""),
            "tests_run": test_result.get("tests_run", 0),
            "passed": test_result.get("passed", 0),
            "failed": test_result.get("failed", 0),
            "skipped": test_result.get("skipped", 0),
            "failed_tests": test_result.get("failed_tests", []),
            "skipped_tests": test_result.get("skipped_tests", []),
            "foundry_command": (proof.get("foundry", {}) or {}).get("test_command", ""),
        },
        "trace_summary": {
            "summary_available": trace_found,
            "reverts": (trace or {}).get("reverts", []),
            "assertion_failures": (trace or {}).get("assertion_failures", []),
            "call_sequence": (trace or {}).get("call_sequence", []),
            "logs": (trace or {}).get("logs", []),
        },
        "protocol_context": {
            "role": role,
            "score": score,
            "why_it_matters": match.reasons,
            "likely_bug_classes": bug_classes,
            "money_flow_role": money_role,
        },
        "impact_notes": {
            "candidate_impact": candidate_impact,
            "affected_components": [affected],
            "assumptions": [
                "Local Foundry results reflect the committed test code and mocks only.",
                "Behavior on a live deployment may differ from the local harness.",
            ],
            "limitations": [
                "Not a formal audit. Not a severity guarantee.",
                "A passing test does not prove absence of bugs; a failing test does not by itself prove a vulnerability.",
                "Human review is required to determine whether this represents a valid vulnerability.",
            ],
        },
        "recommended_next_steps": [
            f"arkheionx report . --target {match.display_id}",
            "Review the proof/trace artifacts and confirm the property under test.",
        ],
    }

    pkg = EvidencePackage(
        target=match.qualified_id,
        target_id=match.stable_id or match.display_id,
        evidence_level=evidence_level,
        status=status,
        proof_found=True,
        trace_found=trace_found,
        tests_run=test_result.get("tests_run", 0),
        passed=test_result.get("passed", 0),
        failed=test_result.get("failed", 0),
        skipped=test_result.get("skipped", 0),
        next_command=f"arkheionx report . --target {match.display_id}",
        payload=payload,
    )
    if write:
        pkg.json_path = str(writer.write_text(f"evidence/{slug}/evidence.json", json.dumps(payload, indent=2)))
        from .render import evidence_text

        pkg.text_path = str(writer.write_text(f"evidence/{slug}/evidence.txt", evidence_text(payload)))
    return pkg
