"""Hunter lead builder.

Fuses the proven senior-triage review-map leads with the V9 signals — value-flow,
state-machine, deployment reality, live-registry diff, source provenance, and program
identity — into ``HunterLead`` objects, and adds synthetic leads for situations a
source-only reading would miss: a live deployment mismatch, a live-registry diff, and
a source-recovery gap on a value-bearing contract.

Every lead carries at least one kill condition. Scoring and the decision policy are
applied separately in ``scoring.py``.
"""
from __future__ import annotations

from . import lane_templates
from . import lead_types
from . import models as M
from . import reachability as R
from .deployment import deployment_status_for_contract
from .source_recovery import source_status_for_contract
from .state_machine import state_machines_for_contract
from .value_flow import value_paths_for_contract


def _reach_str(score: int, precise: str = "") -> str:
    if precise:
        return precise
    if score >= 70:
        return "UNPRIVILEGED_EXTERNAL"
    if score >= 41:
        return "CONDITIONAL_REACH"
    return "INTERNAL_OR_GUARDED"


def _band(score: int) -> str:
    if score >= 70:
        return M.HIGH
    if score >= 45:
        return M.MEDIUM
    return M.LOW


def _reachability_score(original: int, label: str) -> int:
    """Normalize the legacy visibility score using the resolved who-can-call label."""
    if R.is_attacker_reachable(label):
        return max(original, 80)
    if R.is_unknown_gated(label) or R.is_context_gated(label):
        return min(original, 40)
    if R.is_trusted_role_gated(label):
        return min(original, 20)
    if R.is_internal(label) or R.is_non_value(label):
        return 0
    return original


def _value_path_for_surface(value_paths: list, surface: str):
    surface = (surface or "").lower()
    for vp in value_paths:
        if surface in (vp.entry_function.lower(), vp.exit_function.lower()):
            return vp
    contract = surface.split(".")[0]
    for vp in value_paths:
        if contract and contract == (vp.entry_function or vp.exit_function or "").split(".")[0].lower():
            return vp
    return None


def _kill_conditions(base: str, lead_type: str) -> list:
    kills = [base] if base else []
    for tmpl in lane_templates.templates_for_lead_type(lead_type):
        kills.extend(tmpl["common_kill_conditions"])
    # Dedupe preserving order.
    seen: set = set()
    out: list = []
    for k in kills:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out[:5]


def build_leads(
    senior_leads: list,
    *,
    known_matches: dict,
    freshness_verdicts: dict,
    value_paths: list,
    state_machines: list,
    deployment: M.DeploymentReality,
    registry_diff: M.RegistryDiff,
    source_provenance: M.SourceProvenance,
    program_identity: M.ProgramIdentity,
    reach_map=None,
) -> list:
    leads: list = []
    covered_contracts: set = set()

    for sl in senior_leads:
        surface = getattr(sl, "surface", "") or ""
        contract = surface.split(".")[0] if surface else ""
        function = surface.split(".")[1] if "." in surface else ""
        covered_contracts.add(contract.lower())
        notes = list(getattr(sl, "notes", []) or [])

        vp = _value_path_for_surface(value_paths, surface)
        ordering = vp.state_update_ordering if vp else ""
        precise_reach = vp.attacker_reachability if vp else ""
        trusted_required = bool(vp.trusted_role_required) if vp else False
        reach_conf = vp.reachability_confidence if vp else ""
        reach_class = vp.reachability_decision_class if vp else ""
        reach_ev = list(vp.reachability_evidence) if vp else []
        reach_warn = list(vp.reachability_warnings) if vp else []

        # The Reachability Truth Engine map takes precedence (it covers functions with
        # no value path, e.g. role-gated setters/rate updates) and is the most precise.
        fr = reach_map.lookup(contract, function) if (reach_map is not None and contract and function) else None
        if fr is not None:
            precise_reach = fr.final_label
            trusted_required = R.is_trusted_role_gated(fr.final_label)
            reach_conf = fr.confidence
            reach_class = fr.decision_class
            reach_ev = [f"{e.evidence_type}: {e.detail}" for e in fr.evidence]
            reach_warn = list(fr.warnings)

        deployment_status = deployment_status_for_contract(deployment, contract)
        sm_ids = state_machines_for_contract(state_machines, contract)
        sm_touches_value = bool(sm_ids)
        source_status = source_status_for_contract(source_provenance, contract)

        lead_type = lead_types.classify_lead_type(
            surface=surface, notes=notes, title=getattr(sl, "title", ""),
            state_machine_touches_value=sm_touches_value,
            deployment_status=deployment_status, ordering=ordering,
        )

        km = known_matches.get(getattr(sl, "id", ""), M.KnownMatch(lead_id=getattr(sl, "id", "")))
        fv = freshness_verdicts.get(getattr(sl, "id", ""), M.FreshnessVerdict(lead_id=getattr(sl, "id", "")))

        reach_score = _reachability_score(
            getattr(sl, "attacker_reachability_score", 0), precise_reach)
        materiality_score = getattr(sl, "materiality_score", 0)
        proof_score = getattr(sl, "proof_difficulty_score", 50)
        trusted_gated = R.is_trusted_role_gated(precise_reach) or trusted_required
        unknown_gated = R.is_unknown_gated(precise_reach)
        if trusted_gated or km.known_match_status == M.TRUSTED_ROLE_ONLY:
            trusted_score = 80
        elif unknown_gated:
            trusted_score = 50
        else:
            trusted_score = 20

        lead = M.HunterLead(
            lead_id=getattr(sl, "id", ""),
            title=getattr(sl, "title", surface),
            lead_type=lead_type,
            contract=contract,
            function=function,
            surface=surface,
            source_lines=(vp.source_lines if vp else []),
            linked_files=list(getattr(sl, "linked_files", []) or []),
            value_path_ids=value_paths_for_contract(value_paths, contract),
            state_machine_ids=sm_ids,
            scope_confidence=program_identity.scope_confidence,
            freshness_status=fv.freshness_status,
            dedup_status=km.dedup_status,
            known_match_status=km.known_match_status,
            deployment_status=deployment_status,
            attacker_reachability=_reach_str(reach_score, precise_reach),
            reachability_confidence=reach_conf,
            reachability_decision_class=reach_class or R.decision_class(_reach_str(reach_score, precise_reach)),
            reachability_evidence=reach_ev,
            reachability_warnings=reach_warn,
            trusted_role_risk=_band(trusted_score),
            materiality=_band(materiality_score),
            proof_difficulty=_band(proof_score),
            source_status=source_status,
            kill_conditions=_kill_conditions(getattr(sl, "kill_condition", ""), lead_type),
            notes=notes,
            scope_confidence_score=_scope_score(program_identity.scope_confidence),
            freshness_score=fv.score,
            attacker_reachability_score=reach_score,
            materiality_score=materiality_score,
            duplicate_risk_score=int(round(km.dedup_similarity_score * 100)),
            trusted_role_risk_score=trusted_score,
            proof_difficulty_score=proof_score,
        )
        leads.append(lead)

    leads.extend(_synthetic_leads(
        start_index=len(leads), deployment=deployment, registry_diff=registry_diff,
        source_provenance=source_provenance, program_identity=program_identity,
        covered_contracts=covered_contracts, freshness_verdicts=freshness_verdicts,
    ))
    return leads[: M.RAW_LEAD_LIMIT]


def _scope_score(confidence: str) -> int:
    return {M.LOW: 30, M.MEDIUM: 60, M.HIGH: 85}.get(confidence, 30)


def _synthetic_leads(*, start_index, deployment, registry_diff, source_provenance,
                     program_identity, covered_contracts, freshness_verdicts) -> list:
    out: list = []
    n = start_index

    # 1) Deployment mismatch leads (live differs from expected) — even with no source lead.
    for mm in deployment.mismatches:
        if mm.get("type") not in M.DEPLOYMENT_MISMATCH_STATUSES:
            continue
        name = mm.get("name", "contract")
        n += 1
        lead_id = f"LEAD-D{n:02d}"
        out.append(M.HunterLead(
            lead_id=lead_id,
            title=f"Deployed implementation differs from expected on {name}",
            lead_type=M.DEPLOYMENT_MISMATCH,
            contract=name,
            surface=f"{name} (deployed)",
            deployment_status=mm.get("type", M.DEPLOY_IMPLEMENTATION_CHANGED),
            freshness_status=M.IMPLEMENTATION_CHANGED,
            dedup_status=M.DEDUP_USABLE,
            known_match_status=M.NO_MATCH_FOUND,
            scope_confidence=program_identity.scope_confidence,
            attacker_reachability="UNPRIVILEGED_EXTERNAL",
            materiality=M.HIGH,
            proof_difficulty=M.MEDIUM,
            source_status=M.SOURCE_LOCAL,
            kill_conditions=[
                "Kill if the live implementation actually matches the audited implementation.",
                "Kill if the differing implementation is a known/expected upgrade documented in scope.",
            ],
            notes=["deployment-mismatch", "value-bearing"],
            scope_confidence_score=_scope_score(program_identity.scope_confidence),
            freshness_score=95, attacker_reachability_score=85, materiality_score=85,
            duplicate_risk_score=10, trusted_role_risk_score=20, proof_difficulty_score=50,
        ))

    # 2) Live registry diff lead.
    if registry_diff.status in (M.LIVE_NOT_LISTED, M.LISTED_NOT_LIVE):
        n += 1
        out.append(M.HunterLead(
            lead_id=f"LEAD-R{n:02d}",
            title=f"Live registry set differs from listed scope set ({registry_diff.status})",
            lead_type=M.LIVE_REGISTRY_DIFF,
            contract="Registry",
            surface="Registry (live set)",
            deployment_status="",
            freshness_status=(M.NEW_LIVE_REGISTRY_ENTRY if registry_diff.status == M.LIVE_NOT_LISTED
                              else M.FRESHNESS_UNKNOWN),
            dedup_status=M.DEDUP_USABLE,
            known_match_status=M.NO_MATCH_FOUND,
            scope_confidence=program_identity.scope_confidence,
            attacker_reachability="UNPRIVILEGED_EXTERNAL",
            materiality=M.MEDIUM,
            proof_difficulty=M.MEDIUM,
            source_status=M.SOURCE_LOCAL,
            kill_conditions=[
                "Kill if the program confirms live registry entries are in scope and intended.",
                "Kill if the extra/missing entry carries no value.",
            ],
            notes=["registry", "live-set-diff"],
            scope_confidence_score=_scope_score(program_identity.scope_confidence),
            freshness_score=70 if registry_diff.status == M.LIVE_NOT_LISTED else 45,
            attacker_reachability_score=70, materiality_score=65,
            duplicate_risk_score=10, trusted_role_risk_score=20, proof_difficulty_score=55,
        ))

    # 3) Source-recovery gap on a value-bearing contract (source missing/ABI-only).
    for rec in source_provenance.records:
        if rec.get("source_origin") not in M.SOURCE_INADEQUATE:
            continue
        name = rec.get("contract_name", "") or "contract"
        if name.lower() in covered_contracts:
            continue
        n += 1
        out.append(M.HunterLead(
            lead_id=f"LEAD-S{n:02d}",
            title=f"Source unavailable for in-scope contract {name}",
            lead_type=M.SOURCE_RECOVERY_GAP,
            contract=name,
            surface=f"{name} (source gap)",
            deployment_status="",
            freshness_status=M.SOURCE_RECOVERED_NO_BASELINE,
            dedup_status=M.DEDUP_PARTIAL,
            known_match_status=M.KNOWN_UNKNOWN,
            scope_confidence=program_identity.scope_confidence,
            attacker_reachability="CONDITIONAL_REACH",
            materiality=M.MEDIUM,
            proof_difficulty=M.HIGH,
            source_status=rec.get("source_origin", M.SOURCE_MISSING),
            kill_conditions=[
                "Kill if authoritative source can be recovered and shows the path is safe.",
                "Kill if the contract holds no value.",
            ],
            notes=["source-gap"],
            scope_confidence_score=_scope_score(program_identity.scope_confidence),
            freshness_score=42, attacker_reachability_score=55, materiality_score=55,
            duplicate_risk_score=20, trusted_role_risk_score=20, proof_difficulty_score=75,
        ))
    return out
