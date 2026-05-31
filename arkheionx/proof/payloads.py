"""Deterministic proof.json and trace.json payload builders."""
from __future__ import annotations

from arkheionx.version import PACKAGE_VERSION, __version__

from .runner import ExecResult

PROOF_SCHEMA_VERSION = "1.0.0"
TRACE_SCHEMA_VERSION = "1.0.0"


def target_slug(display_id: str) -> str:
    return display_id.replace(".", "_").replace("/", "_").replace(":", "_")


def build_proof_payload(
    target_display: str,
    target_id: str,
    project_root: str,
    status: str,
    evidence_level: str,
    result: ExecResult,
    generated_files: list[str],
    raw_output_path: str,
    trace_paths: tuple[str, str],
    next_commands: list[str],
) -> dict:
    trace = result.trace or {}
    return {
        "schema_version": PROOF_SCHEMA_VERSION,
        "arkheionx_version": __version__,
        "package_version": PACKAGE_VERSION,
        "target": target_display,
        "target_id": target_id,
        "project_root": project_root,
        "status": status,
        "evidence_level": evidence_level,
        "foundry": {
            "available": result.foundry.forge_available,
            "version": result.foundry.forge_version,
            "build_status": result.build_status,
            "test_command": result.test_command,
            "cwd": project_root,
        },
        "test_result": {
            "tests_run": trace.get("tests_run", 0),
            "passed": trace.get("passed", 0),
            "failed": trace.get("failed", 0),
            "skipped": trace.get("skipped", 0),
            "duration": "",
            "failed_tests": trace.get("failing_tests", []),
            "skipped_tests": trace.get("skipped_tests", []),
            "raw_output_path": raw_output_path,
        },
        "trace": {
            "raw_trace_path": trace_paths[0],
            "trace_json_path": trace_paths[1],
            "summary_available": bool(trace),
        },
        "generated_files": generated_files,
        "limitations": _limitations(status, evidence_level),
        "next_commands": next_commands,
    }


def build_trace_payload(target_display: str, status: str, evidence_level: str, raw_output_path: str, trace: dict) -> dict:
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "target": target_display,
        "status": status,
        "evidence_level": evidence_level,
        "source_raw_output": raw_output_path,
        "tests_run": trace.get("tests_run", 0),
        "passed": trace.get("passed", 0),
        "failed": trace.get("failed", 0),
        "skipped": trace.get("skipped", 0),
        "failing_tests": trace.get("failing_tests", []),
        "skipped_tests": trace.get("skipped_tests", []),
        "reverts": trace.get("reverts", []),
        "assertion_failures": trace.get("assertion_failures", []),
        "call_sequence": trace.get("call_sequence", []),
        "logs": trace.get("logs", []),
        "limitations": trace.get("limitations", []),
    }


def _limitations(status: str, evidence_level: str) -> list[str]:
    out = ["Local static/heuristic workbench output. Not a formal audit; no severity guarantee."]
    if evidence_level != "EXECUTION_CONFIRMED":
        out.append("No test executed for this target yet; this is not proof of a bug.")
    if status in {"tested_passed"}:
        out.append("A passing test does not prove the absence of a bug.")
    if status in {"tested_failed", "tested_mixed"}:
        out.append("A failing test does not by itself prove an exploitable vulnerability.")
    return out
