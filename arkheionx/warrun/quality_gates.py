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
ZERO_CONTRACTS_INDEXED_WARNING = "ZERO_CONTRACTS_INDEXED_WARNING"
ZERO_REAL_CONTRACTS_INDEXED = "ZERO_REAL_CONTRACTS_INDEXED"
ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING = "ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING"
STALE_ARTIFACT_IGNORED = "STALE_ARTIFACT_IGNORED"
AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION = "AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION"
NO_SUBMIT_IF_BOUNTY_REALITY_BLOCKED = "NO_SUBMIT_IF_BOUNTY_REALITY_BLOCKED"
NO_SUBMIT_IF_KEY_REUSE_ONLY = "NO_SUBMIT_IF_KEY_REUSE_ONLY"
NO_SUBMIT_IF_OFFCHAIN_VALIDATION_ONLY = "NO_SUBMIT_IF_OFFCHAIN_VALIDATION_ONLY"
NO_SUBMIT_IF_FORCED_VALUE_TRANSFER_ONLY = "NO_SUBMIT_IF_FORCED_VALUE_TRANSFER_ONLY"
NO_SUBMIT_IF_TRUSTED_ROLE_ONLY = "NO_SUBMIT_IF_TRUSTED_ROLE_ONLY"
NO_SUBMIT_IF_DUST_ONLY = "NO_SUBMIT_IF_DUST_ONLY"
NO_SUBMIT_IF_PREVIOUSLY_REJECTED = "NO_SUBMIT_IF_PREVIOUSLY_REJECTED"
NO_SUBMIT_IF_DUPLICATE_ROOT_CAUSE = "NO_SUBMIT_IF_DUPLICATE_ROOT_CAUSE"

# Hard gates whose failure must downgrade the offending submit candidate.
_HARD = {REQUIRED_FIELDS_GATE, NO_DUST_HIGH_GATE, NO_TRUSTED_ROLE_SUBMIT_GATE,
         NO_DUPLICATE_SUBMIT_GATE, NO_SCOPE_SUBMIT_GATE,
         ZERO_REAL_CONTRACTS_INDEXED,
         NO_SUBMIT_IF_BOUNTY_REALITY_BLOCKED, NO_SUBMIT_IF_KEY_REUSE_ONLY,
         NO_SUBMIT_IF_OFFCHAIN_VALIDATION_ONLY, NO_SUBMIT_IF_FORCED_VALUE_TRANSFER_ONLY,
         NO_SUBMIT_IF_TRUSTED_ROLE_ONLY, NO_SUBMIT_IF_DUST_ONLY,
         NO_SUBMIT_IF_PREVIOUSLY_REJECTED, NO_SUBMIT_IF_DUPLICATE_ROOT_CAUSE}


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
                      report_generated=False, reality_results=None,
                      ingest_summary=None, auth_analysis=None) -> list:
    secret_warnings = secret_warnings or []
    vby_id = {v.candidate_id: v for v in verdicts}
    submit = [c for c in graph.candidates if _is_submit(c.economic_severity)]
    gates = []
    reality_results = reality_results or []
    candidates_by_id = {candidate.id: candidate for candidate in graph.candidates}

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

    zero_contracts = bool(ingest_summary is not None and ingest_summary.contracts_indexed == 0)
    gates.append(QualityGate(
        ZERO_CONTRACTS_INDEXED_WARNING,
        WARN if zero_contracts else PASS,
        [],
        "ZERO_CONTRACTS_INDEXED: check target path, framework detection, or ingestion settings."
        if zero_contracts else "At least one Solidity contract was indexed.",
    ))
    zero_real_contracts = bool(
        ingest_summary is not None and getattr(ingest_summary, "real_contracts_indexed", 0) == 0
    )
    zero_real_submit = [c.id for c in submit] if zero_real_contracts else []
    gates.append(QualityGate(
        ZERO_REAL_CONTRACTS_INDEXED,
        FAIL if zero_real_submit else WARN if zero_real_contracts else PASS,
        zero_real_submit,
        "ZERO_REAL_CONTRACTS_INDEXED: no live source-backed Solidity contracts were indexed."
        if zero_real_contracts else "At least one live source-backed Solidity contract was indexed.",
    ))
    artifact_only = bool(
        ingest_summary is not None
        and getattr(ingest_summary, "contracts_indexed", 0) > 0
        and getattr(ingest_summary, "solidity_files_indexed", 0) == 0
    )
    gates.append(QualityGate(
        ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING,
        WARN if artifact_only else PASS,
        [],
        "ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING: contracts came only from artifacts."
        if artifact_only else "No artifact-only source gap detected.",
    ))
    stale_ignored = bool(
        ingest_summary is not None
        and (
            getattr(ingest_summary, "stale_artifacts_ignored", 0)
            or getattr(ingest_summary, "sample_artifacts_ignored", 0)
        )
    )
    gates.append(QualityGate(
        STALE_ARTIFACT_IGNORED,
        WARN if stale_ignored else PASS,
        [],
        "STALE_ARTIFACT_IGNORED: ignored compiler artifacts without live source."
        if stale_ignored else "No stale compiler artifacts were ignored.",
    ))
    auth_keywords_only = bool(
        auth_analysis is not None
        and not getattr(auth_analysis, "signed_operations", [])
        and any(
            "AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION" in warning
            for warning in (getattr(auth_analysis, "warnings", []) or [])
        )
    )
    gates.append(QualityGate(
        AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION,
        WARN if auth_keywords_only else PASS,
        [],
        "AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION: keywords were present but no signed operation was detected."
        if auth_keywords_only else "Signed-operation detection is consistent with authorization activation.",
    ))

    def _reality_submit(tag=None):
        affected = []
        for result in reality_results:
            if tag is not None and tag not in result.reason_tags:
                continue
            candidate = candidates_by_id.get(result.candidate_id)
            if candidate is not None and _is_submit(candidate.economic_severity):
                affected.append(candidate.id)
        return affected

    reality_blocked_submit = [
        result.candidate_id for result in reality_results
        if result.blocked
        and result.candidate_id in candidates_by_id
        and _is_submit(candidates_by_id[result.candidate_id].economic_severity)
    ]
    gates.append(QualityGate(
        NO_SUBMIT_IF_BOUNTY_REALITY_BLOCKED,
        FAIL if reality_blocked_submit else PASS,
        reality_blocked_submit,
        "Candidates blocked by bounty reality cannot retain SUBMIT_* labels.",
    ))
    tag_gates = (
        (NO_SUBMIT_IF_KEY_REUSE_ONLY, "key_reuse"),
        (NO_SUBMIT_IF_OFFCHAIN_VALIDATION_ONLY, "offchain_validation"),
        (NO_SUBMIT_IF_FORCED_VALUE_TRANSFER_ONLY, "forced_value_transfer"),
        (NO_SUBMIT_IF_TRUSTED_ROLE_ONLY, "trusted_role"),
        (NO_SUBMIT_IF_DUST_ONLY, "dust"),
        (NO_SUBMIT_IF_PREVIOUSLY_REJECTED, "previously_rejected"),
        (NO_SUBMIT_IF_DUPLICATE_ROOT_CAUSE, "duplicate"),
    )
    for gate_id, tag in tag_gates:
        affected = _reality_submit(tag)
        gates.append(QualityGate(
            gate_id,
            FAIL if affected else PASS,
            affected,
            f"Candidates tagged {tag} by bounty reality cannot retain SUBMIT_* labels.",
        ))
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
