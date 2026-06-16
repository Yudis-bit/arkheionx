"""Step 1 — bounty eligibility, read from local scope and program rules only.

This gate never fetches a remote program page. It reads the local scope note plus
any local known/audit material the user pointed at. If there is not enough program
context, the target decision is ``NEEDS_MORE_CONTEXT`` and triage still continues
with local technical signals. Eligibility is a planning read, not a severity call.
"""
from __future__ import annotations

from . import models as M
from .corpus import Doc

# Phrase groups (lowercased substring match against the scope text).
_OOS_MARKERS = (
    "out of scope",
    "out-of-scope",
    "not in scope",
    "excluded",
    "exclusion",
    "ineligible",
    "no impact",
    "informational only",
    "will not be rewarded",
    "not rewarded",
)
_TRUSTED_ROLE_MARKERS = (
    "trusted role",
    "trusted-role",
    "trusted actor",
    "admin",
    "owner",
    "governance",
    "guardian",
    "privileged",
    "centralization",
    "multisig",
    "timelock",
)
_DUP_MARKERS = (
    "duplicate",
    "known issue",
    "already reported",
    "previously reported",
    "previously known",
)
_POC_MARKERS = (
    "proof of concept",
    "proof-of-concept",
    "poc required",
    "runnable poc",
    "coded poc",
    "working poc",
)
_REWARD_MARKERS = (
    "reward",
    "bounty",
    "payout",
    "max bounty",
    "severity",
    "critical",
    "high",
    "medium",
    "low",
    "$",
)
_KYC_MARKERS = ("kyc", "know your customer", "identity verification")


def _lines_matching(text: str, markers: tuple[str, ...], limit: int = 6) -> list[str]:
    hits: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip(" \t#-*>").strip()
        low = line.lower()
        if not low:
            continue
        if any(marker in low for marker in markers):
            snippet = line if len(line) <= 160 else line[:157] + "..."
            if snippet.lower() not in seen:
                seen.add(snippet.lower())
                hits.append(snippet)
        if len(hits) >= limit:
            break
    return hits


def _severity_ceiling(low: str) -> str:
    if not low:
        return M.SEV_UNKNOWN
    if "critical" in low:
        return M.SEV_CRITICAL
    if "high" in low:
        return M.SEV_HIGH
    if "medium" in low:
        return M.SEV_MEDIUM
    if "low" in low or "informational" in low:
        return M.SEV_LOW
    return M.SEV_UNKNOWN


def assess_eligibility(
    ctx: M.TriageContext,
    scope_text: str,
    known_docs: list[Doc],
) -> M.EligibilitySignal:
    scope_text = scope_text or ""
    low = scope_text.lower()
    scope_provided = bool(scope_text.strip())

    oos_traps = _lines_matching(scope_text, _OOS_MARKERS)
    trusted_role_traps = _lines_matching(scope_text, _TRUSTED_ROLE_MARKERS)
    excluded_impacts = _lines_matching(scope_text, ("excluded", "no impact", "informational only", "not rewarded"))
    requires_poc = any(marker in low for marker in _POC_MARKERS)
    kyc_noted = any(marker in low for marker in _KYC_MARKERS)
    reward_notes = _lines_matching(scope_text, _REWARD_MARKERS)
    has_reward_info = bool(reward_notes)

    # Scope confidence: graded by how much the local scope actually says.
    if not scope_provided:
        scope_confidence = M.CONF_LOW
    else:
        score = 0
        score += 1 if has_reward_info else 0
        score += 1 if (oos_traps or excluded_impacts) else 0
        score += 1 if _severity_ceiling(low) != M.SEV_UNKNOWN else 0
        score += 1 if len(scope_text) > 400 else 0
        scope_confidence = M.CONF_HIGH if score >= 3 else (M.CONF_MEDIUM if score >= 1 else M.CONF_LOW)

    # Initial (pre-PoC) duplicate risk from scope wording + available material.
    if any(marker in low for marker in _DUP_MARKERS):
        initial_duplicate_risk = M.CONF_HIGH
    elif known_docs:
        initial_duplicate_risk = M.CONF_MEDIUM
    elif scope_provided:
        initial_duplicate_risk = M.CONF_LOW
    else:
        initial_duplicate_risk = "UNKNOWN"

    severity_ceiling = _severity_ceiling(low)

    missing_context: list[str] = []
    if not scope_provided:
        missing_context.append("Scope / program rules (use --scope-file).")
    elif not has_reward_info:
        missing_context.append("Reward table / severity bands are not stated in the scope.")
    if not any(d.kind == "known" for d in known_docs):
        missing_context.append("Known findings / prior reports (use --known).")
    if not any(d.kind == "audit" for d in known_docs):
        missing_context.append("Prior audit reports (use --audits).")

    if not scope_provided:
        target_decision = M.TARGET_NEEDS_CONTEXT
        reason = "Scope file does not include enough program rules to estimate bounty eligibility."
        recommended_action = (
            "Provide a scope file with reward bands, in-scope contracts, and exclusions, "
            "then re-run triage. Local technical triage still continues below."
        )
    else:
        target_decision = M.TARGET_TOUCH  # provisional; reconciled against scored leads
        reason = "Scope provided; eligibility read from local program rules."
        recommended_action = (
            "Confirm in-scope value surfaces and exclusions before writing any local proof."
        )

    return M.EligibilitySignal(
        scope_provided=scope_provided,
        scope_confidence=scope_confidence,
        target_decision=target_decision,
        severity_ceiling=severity_ceiling,
        initial_duplicate_risk=initial_duplicate_risk,
        requires_poc=requires_poc,
        kyc_noted=kyc_noted,
        reward_notes=reward_notes,
        oos_traps=oos_traps,
        trusted_role_traps=trusted_role_traps,
        excluded_impacts=excluded_impacts,
        missing_context=missing_context,
        recommended_action=recommended_action,
        reason=reason,
    )
