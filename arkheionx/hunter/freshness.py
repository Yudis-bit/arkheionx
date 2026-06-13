"""Freshness engine (V9) for hunter mode.

Freshness here is strictly evidence-based. It is *not* "Arkheionx has not seen this
before", a new-looking filename, an interesting function name, or a freshly cloned
repo. A positive freshness status is only emitted when at least one concrete signal
supports it:

    git diff after an explicit baseline ref/date; a user fresh-allowlist; a deployed
    implementation that differs from the audited one; a live registry entry not in
    the listed set; an audit corpus that demonstrably does not cover the surface; a
    post-baseline value-out path or state-machine value-flow path.

With no baseline of any kind, freshness is FRESHNESS_UNKNOWN / BASELINE_UNKNOWN and
the scorer caps the lead to PARK_BASELINE. Read-only; git is consulted only when a
baseline is explicitly provided.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.senior_triage import models as SM
from arkheionx.senior_triage.freshness import _git_changed_basenames

from . import models as M

_VALUE_OUT_NOTES = ("value-out",)


def _audit_text(corpus: list) -> str:
    return "\n".join(d.lower for d in corpus if getattr(d, "kind", "") == "audit")


# Markers that mean a surface is *not* covered by the audit (an audit gap), even though
# the audit text names it (typically to say it was added after the review).
_GAP_MARKERS = (
    "not covered", "after this audit", "added after", "post-audit", "post audit",
    "out of scope", "not in scope", "was not in scope", "not reviewed",
    "added this release", "newly added",
)
# Markers that explicitly assert the surface *was* covered.
_COVERED_MARKERS = (
    "reviewed", "verified", "no issue", "audited", "assessed", "checked",
    "in scope of this audit", "examined",
)


def _audit_coverage(token: str, audit_text: str) -> str:
    """Return 'covered' | 'gap' | 'absent' for a token in the audit corpus.

    Line/section based: a '## Not covered' heading marks its bullets as gaps, while an
    explicit covered marker ('reviewed'/'verified') on the token's own line wins. This
    keeps a nearby 'not covered' section from bleeding onto a reviewed contract.
    """
    if not token or token not in audit_text:
        return "absent"
    covered = gap = False
    section_gap = False
    for raw in audit_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            section_gap = any(m in line for m in _GAP_MARKERS)
            continue
        if token not in line:
            continue
        has_covered = any(m in line for m in _COVERED_MARKERS)
        has_gap = any(m in line for m in _GAP_MARKERS) or section_gap
        if has_covered:
            covered = True            # explicit review wins on the token's own line
        elif has_gap:
            gap = True
    if covered:
        return "covered"
    return "gap" if gap else "covered"


def _surface_tokens(lead) -> list:
    tokens = [Path(p).stem.lower() for p in getattr(lead, "linked_files", []) or []]
    surface = getattr(lead, "surface", "") or ""
    tokens.append(surface.split(".")[0].lower())
    return [t for t in tokens if t and len(t) >= 4]


def _allowlisted(lead, allowlist: list) -> bool:
    if not allowlist:
        return False
    hay = " ".join([getattr(lead, "surface", ""), getattr(lead, "title", ""),
                    " ".join(getattr(lead, "linked_files", []) or [])]).lower()
    return any(str(tok).lower() in hay for tok in allowlist if tok)


def assess_freshness(
    ctx: M.HunterContext,
    root: Path,
    senior_leads: list,
    corpus: list,
    *,
    deployment_status_by_lead: dict | None = None,
    value_state_machine_contracts: set | None = None,
) -> list:
    deployment_status_by_lead = deployment_status_by_lead or {}
    value_state_machine_contracts = {c.lower() for c in (value_state_machine_contracts or set())}
    audit_docs = [d for d in corpus if getattr(d, "kind", "") == "audit"]
    audit_text = _audit_text(corpus)
    have_audit_baseline = bool(audit_docs)

    changed = _git_changed_basenames(root, ctx.baseline_ref, ctx.since_date)
    have_git_baseline = changed is not None and (bool(ctx.baseline_ref) or bool(ctx.since_date))
    have_baseline = have_git_baseline or have_audit_baseline or bool(ctx.fresh_allowlist)

    verdicts: list = []
    for lead in senior_leads:
        notes: list = []
        evidence: list = []
        caps: list = []
        value_out = "value-out" in (getattr(lead, "notes", []) or [])
        contract = (getattr(lead, "surface", "") or "").split(".")[0].lower()
        basenames = [Path(p).name for p in getattr(lead, "linked_files", []) or []]
        tokens = _surface_tokens(lead)
        coverages = [_audit_coverage(t, audit_text) for t in tokens] if audit_text else []
        audit_covered = "covered" in coverages
        deploy_status = deployment_status_by_lead.get(getattr(lead, "id", ""), "")

        status = M.FRESHNESS_UNKNOWN
        confidence = M.LOW
        score = 40

        if deploy_status in M.DEPLOYMENT_MISMATCH_STATUSES:
            status, confidence, score = M.IMPLEMENTATION_CHANGED, M.HIGH, 95
            notes.append("Deployed implementation differs from the expected/audited implementation.")
            evidence.append({"source": "deployment", "reason": deploy_status})
        elif _allowlisted(lead, ctx.fresh_allowlist):
            status, confidence, score = M.POST_AUDIT_CHANGE, M.HIGH, 88
            notes.append("Surface is in the user-provided fresh allowlist.")
            evidence.append({"source": "fresh-allowlist", "reason": "user marked fresh"})
        elif have_git_baseline and any(b in (changed or set()) for b in basenames):
            changed_paths = [p for p, b in zip(getattr(lead, "linked_files", []), basenames)
                             if b in (changed or set())]
            if value_out:
                status, confidence, score = M.NEW_VALUE_OUT_SURFACE, M.HIGH, 100
                notes.append(f"Value-out path changed after baseline ({ctx.baseline_ref or ctx.since_date}).")
            else:
                status, confidence, score = M.POST_AUDIT_CHANGE, M.HIGH, 90
                notes.append(f"Code changed after baseline ({ctx.baseline_ref or ctx.since_date}).")
            for p in changed_paths:
                evidence.append({"source_path": p, "reason": "changed after baseline (git diff)"})
        elif have_audit_baseline and audit_covered:
            status, confidence, score = M.AUDIT_COVERED, M.HIGH, 20
            notes.append("Surface appears in the audit baseline (covered / not a priority change).")
            caps.append("Audit-covered: not boosted as fresh without a post-audit change signal.")
        elif have_audit_baseline and contract in value_state_machine_contracts:
            status, confidence, score = M.NEW_STATE_MACHINE_VALUE_FLOW, M.MEDIUM, 90
            notes.append("State-machine value-flow surface is absent from the audit baseline.")
            evidence.append({"source": "audit-coverage-gap", "reason": "state-machine value-flow not audit-covered"})
        elif have_audit_baseline and value_out:
            status, confidence, score = M.NEW_VALUE_OUT_SURFACE, M.MEDIUM, 82
            notes.append("Value-out surface is absent from the audit baseline (audit shows it not covered).")
            evidence.append({"source": "audit-coverage-gap", "reason": "value-out surface not audit-covered"})
        elif have_baseline:
            status, confidence, score = M.FRESHNESS_UNKNOWN, M.LOW, 45
            notes.append("Baseline present but this surface shows no concrete change signal.")
        elif (ctx.source_dir or ctx.source_recovery_mode not in ("", "none")) and not have_baseline:
            status, confidence, score = M.SOURCE_RECOVERED_NO_BASELINE, M.LOW, 42
            notes.append("Source available but no audit/git baseline to diff against.")
            caps.append("No baseline: cannot assert post-audit freshness.")
        else:
            status, confidence, score = M.BASELINE_UNKNOWN, M.LOW, 40
            notes.append("No baseline (provide --baseline-ref / --since-date / --audits / --fresh-allowlist).")

        if status in M.FRESHNESS_NO_BASELINE:
            caps.append("No freshness baseline -> capped to PARK_BASELINE unless a hard deployment mismatch exists.")

        verdicts.append(M.FreshnessVerdict(
            lead_id=getattr(lead, "id", ""), freshness_status=status,
            freshness_confidence=confidence, freshness_evidence=evidence[:6],
            freshness_caps=caps, score=score,
        ))
        # Carry notes onto the first evidence reason if no structured evidence exists.
        if not evidence and notes:
            verdicts[-1].freshness_evidence = [{"source": "inference", "reason": notes[0]}]
    return verdicts
