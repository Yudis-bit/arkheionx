"""War-run quality gates (Layer 10+).

A verification pass over the assembled candidates/verdicts before output. Each gate
returns pass / warn / fail with the affected candidates and an explanation. The hard
gates (required fields, no-secret, no-trusted-role-submit, no-duplicate-submit,
no-scope-submit, no-dust-high) must hold for any SUBMIT_* candidate; if one does not,
``enforce`` downgrades the offending candidate so war-run cannot output a submit
candidate that violates the gates. This is defense-in-depth: the economic gate
already enforces most of these upstream.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from arkheionx.severity import models as S

PASS, WARN, FAIL = "pass", "warn", "fail"

REQUIRED_FIELDS_GATE = "REQUIRED_FIELDS_GATE"
NO_REPORT_GATE = "NO_REPORT_GATE"
NO_SECRET_GATE = "NO_SECRET_GATE"
NO_DUST_HIGH_GATE = "NO_DUST_HIGH_GATE"
NO_TRUSTED_ROLE_SUBMIT_GATE = "NO_TRUSTED_ROLE_SUBMIT_GATE"
NO_DUPLICATE_SUBMIT_GATE = "NO_DUPLICATE_SUBMIT_GATE"
NO_SCOPE_SUBMIT_GATE = "NO_SCOPE_SUBMIT_GATE"
FORK_DEPENDENCY_GATE = "FORK_DEPENDENCY_GATE"
PROOF_QUALITY_GATE = "PROOF_QUALITY_GATE"
HUMAN_REVIEW_GATE = "HUMAN_REVIEW_GATE"

# Hard gates whose failure must downgrade the offending submit candidate.
_HARD = {REQUIRED_FIELDS_GATE, NO_DUST_HIGH_GATE, NO_TRUSTED_ROLE_SUBMIT_GATE,
         NO_DUPLICATE_SUBMIT_GATE, NO_SCOPE_SUBMIT_GATE}


@dataclass
class QualityGate:
    id: str = ""
    status: str = PASS
    affected: list = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _is_submit(label) -> bool:
    return (label or "") in S.SUBMIT_LABELS


def run_quality_gates(graph, verdicts, fork_reqs, *, secret_warnings=None,
                      report_generated=False) -> list:
    secret_warnings = secret_warnings or []
    vby_id = {v.candidate_id: v for v in verdicts}
    submit = [c for c in graph.candidates if _is_submit(c.economic_severity)]
    gates = []

    missing = [c.id for c in submit if not (c.attacker_capability and c.victim and c.asset
                                            and c.broken_invariant and c.entry_function)]
    gates.append(QualityGate(REQUIRED_FIELDS_GATE, FAIL if missing else PASS, missing,
                             "Every SUBMIT_* candidate must carry attacker/victim/asset/"
                             "broken_invariant/entry."))

    gates.append(QualityGate(NO_REPORT_GATE, FAIL if report_generated else PASS, [],
                             "war-run never generates a bounty report."))

    gates.append(QualityGate(NO_SECRET_GATE, FAIL if secret_warnings else PASS, [],
                             "No RPC URLs / private keys / secrets may appear in artifacts."))

    dust_high = [c.id for c in submit
                 if vby_id.get(c.id) and vby_id[c.id].impact_type == S.DUST_ONLY
                 and c.economic_severity in (S.SUBMIT_HIGH_CANDIDATE, S.SUBMIT_CRITICAL_CANDIDATE)]
    gates.append(QualityGate(NO_DUST_HIGH_GATE, FAIL if dust_high else PASS, dust_high,
                             "Dust-only impact cannot be High/Critical."))

    role_submit = [c.id for c in submit if c.role_gated]
    gates.append(QualityGate(NO_TRUSTED_ROLE_SUBMIT_GATE, FAIL if role_submit else PASS,
                             role_submit, "Trusted-role candidates cannot be SUBMIT_*."))

    dup_submit = [c.id for c in submit if c.duplicate_risk == "SAME_ROOT_CAUSE"]
    gates.append(QualityGate(NO_DUPLICATE_SUBMIT_GATE, FAIL if dup_submit else PASS,
                             dup_submit, "Duplicate root causes cannot be SUBMIT_*."))

    scope_submit = [c.id for c in submit if c.scope_risk == "OUT_OF_SCOPE"]
    gates.append(QualityGate(NO_SCOPE_SUBMIT_GATE, FAIL if scope_submit else PASS,
                             scope_submit, "Out-of-scope candidates cannot be SUBMIT_*."))

    fork_ids = {r.candidate_id for r in fork_reqs}
    needs_fork = [c.id for c in graph.candidates
                  if c.economic_severity in (S.NEEDS_FORK_PROOF, S.NEEDS_REAL_ASSET_PROOF)]
    missing_fork = [cid for cid in needs_fork if cid not in fork_ids]
    gates.append(QualityGate(FORK_DEPENDENCY_GATE, WARN if missing_fork else PASS,
                             missing_fork, "Fork-dependent candidates should carry a fork plan."))

    weak = [c.id for c in submit
            if vby_id.get(c.id) and vby_id[c.id].proof_quality == S.STATIC_ONLY]
    gates.append(QualityGate(PROOF_QUALITY_GATE, WARN if weak else PASS, weak,
                             "SUBMIT_* candidates should have at least a local PoC skeleton."))

    gates.append(QualityGate(HUMAN_REVIEW_GATE, PASS, [],
                             "Human review is always required; war-run never auto-submits."))
    return gates


def overall_status(gates) -> str:
    if any(g.status == FAIL for g in gates):
        return FAIL
    if any(g.status == WARN for g in gates):
        return WARN
    return PASS


def enforce(graph, gates, verdicts=None):
    """Downgrade any submit candidate flagged by a hard FAIL gate. Returns the list of
    (candidate_id, gate_id) downgrades applied. Normally empty (the economic gate
    enforces these upstream)."""
    flagged = {}
    for g in gates:
        if g.status == FAIL and g.id in _HARD:
            for cid in g.affected:
                flagged.setdefault(cid, g.id)
    if not flagged:
        return []
    vby_id = {v.candidate_id: v for v in (verdicts or [])}
    applied = []
    for c in graph.candidates:
        if c.id in flagged and _is_submit(c.economic_severity):
            c.economic_severity = S.PARK_INCOMPLETE
            c.recommendation = S.PARK_INCOMPLETE
            if c.id in vby_id:
                vby_id[c.id].label = S.PARK_INCOMPLETE
                vby_id[c.id].final_recommendation = S.PARK_INCOMPLETE
                vby_id[c.id].reasons.append(
                    f"Downgraded by quality gate {flagged[c.id]} (must not be submit).")
            applied.append((c.id, flagged[c.id]))
    return applied


def gates_json(gates, status) -> dict:
    return {
        "schema_version": "v10-quality-gates",
        "artifact_type": "godeye_quality_gates",
        "overall_status": status,
        "gate_count": len(gates),
        "gates": [g.to_dict() for g in gates],
    }


def gates_md(gates, status) -> str:
    lines = [
        "# Quality Gates",
        "",
        f"Overall: **{status.upper()}**. Verification before output: hard gates must hold",
        "for any SUBMIT_* candidate (else it is downgraded). This is review context.",
        "",
        "| Gate | Status | Affected | Explanation |",
        "| --- | --- | --- | --- |",
    ]
    for g in gates:
        aff = ", ".join(g.affected) if g.affected else "-"
        lines.append(f"| {g.id} | {g.status} | {aff} | {g.explanation} |")
    return "\n".join(lines) + "\n"
