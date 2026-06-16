"""Candidate-ranking renderer (10-candidate-ranking.md), exact spec format."""
from __future__ import annotations


def _decision(c) -> str:
    sev = c.economic_severity or ""
    if sev.startswith("SUBMIT"):
        return "Submit"
    if sev.startswith("KILL"):
        return "Kill"
    if sev in ("NEEDS_FORK_PROOF", "NEEDS_REAL_ASSET_PROOF"):
        return "Fork"
    if sev.startswith("PARK"):
        return "Park"
    if sev in ("VALID_BUT_LOW", "VALID_BUT_LOW_LIKELIHOOD", "SUBMIT_LOW_ONLY"):
        return "Low"
    return "Fork" if c.fork_requirement else "Investigate"


def _next_action(c) -> str:
    sev = c.economic_severity or ""
    if sev.startswith("KILL"):
        return "kill"
    if sev.startswith("PARK"):
        return "park"
    if c.fork_requirement or sev in ("NEEDS_FORK_PROOF", "NEEDS_REAL_ASSET_PROOF"):
        return "fork: run the fork plan, then re-evaluate"
    return f"write PoC ({c.poc_skeleton})" if c.poc_skeleton else "write PoC"


def candidate_ranking_md(graph) -> str:
    lines = [
        "# 10 Candidate Ranking",
        "",
        "Ranked research directions. A candidate is not a finding; no report is",
        "generated. Apply each kill/park decision and prove the rest locally or on a",
        "fork before any human submission decision.",
        "",
    ]
    for c in graph.candidates:
        d = c.severity_detail or {}
        lines += [
            f"## Candidate {c.id}: {c.title}",
            "",
            f"Decision: {_decision(c)}",
            "",
            f"Root cause: {c.root_cause}",
            "",
            f"Broken invariant: {c.broken_invariant}",
            "",
            f"Attacker: {c.attacker_capability}",
            "",
            f"Victim: {c.victim}",
            "",
            f"Asset at risk: {c.asset}",
            "",
            "Entry point:",
            f"{c.entry_function}",
            "",
            "Attack sequence:",
        ]
        if c.call_sequence:
            lines += [f"{i}. {s}" for i, s in enumerate(c.call_sequence, 1)]
        else:
            lines.append("1. (single-function effect)")
        lines += ["", "Evidence:"]
        lines += [f"* {e}" for e in (c.evidence or ["(see semantic map)"])]
        lines += [
            "",
            f"PoC strategy: {c.proof_strategy}",
            f"Skeleton: {c.poc_skeleton or '(not generated)'}",
            "",
            "Economic gate:",
            f"* impact: {d.get('impact', 'pending')}",
            f"* likelihood: {d.get('likelihood', 'pending')}",
            f"* cap: {d.get('cap', 'pending')}",
            f"* repeatability: {d.get('repeatability', 'pending')}",
            f"* gas: {d.get('gas', 'pending')}",
            f"* realism: {d.get('realism', 'pending')}",
            f"* final recommendation: {c.economic_severity or 'pending'}",
            "",
            "Dedup/scope:",
            f"* same root cause: {c.duplicate_risk}",
            f"* out of scope risk: {c.scope_risk}",
            f"* known duplicate risk: {c.duplicate_risk}",
            "",
            f"Next action: {_next_action(c)}",
            "",
        ]
    return "\n".join(lines) + "\n"
