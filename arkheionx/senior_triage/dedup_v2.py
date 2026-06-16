"""Semantic-ish dedup v2 (no LLM, no external API, fully local).

Combines token-shingle Jaccard similarity, weighted behavior/entity overlap, and
audit-status / public-test proximity into an explainable dedup verdict with located
evidence. It is deliberately conservative: it never claims an exact duplicate without
a contract anchor plus matching behavior, and falls back to SIMILAR_KNOWN when only
broad behavior overlaps. Every verdict carries reasons and evidence snippets.
"""
from __future__ import annotations

from . import evidence_snippets as ev
from . import models as M
from .corpus import ACK_TERMS, DUP_TERMS, TEST_INTENT, windows_around
from .corpus_v2 import detect_behaviors, token_shingles

_DUP_SCORE = {
    M.KNOWN_PUBLIC_TEST: 90,
    M.KNOWN_LIKELY_DUP: 85,
    M.KNOWN_ACK_RISK: 80,
    M.KNOWN_DOCUMENTED: 75,
    M.KNOWN_OUT_OF_SCOPE: 60,
    M.KNOWN_SIMILAR: 55,
    M.KNOWN_TRUSTED_ROLE: 40,
    M.KNOWN_NO_MATCH: 15,
    M.KNOWN_UNKNOWN: 50,
}

# Higher = more likely the behavior is already known (used by scoring, inverted).
_KNOWN_CONFIDENCE_SCORE = {
    M.KNOWN_PUBLIC_TEST: 90,
    M.KNOWN_LIKELY_DUP: 85,
    M.KNOWN_ACK_RISK: 82,
    M.KNOWN_DOCUMENTED: 78,
    M.KNOWN_OUT_OF_SCOPE: 70,
    M.KNOWN_TRUSTED_ROLE: 65,
    M.KNOWN_SIMILAR: 50,
    M.KNOWN_NO_MATCH: 15,
    M.KNOWN_UNKNOWN: 45,
}

_RADIUS = 90

# Generic behaviors are too common to imply a duplicate on their own. A behavior-only
# match (no contract anchor) only counts as SIMILAR_KNOWN when a *specific* behavior
# overlaps.
_SPECIFIC_BEHAVIORS = {
    "inflation", "first-depositor", "first depositor", "rounding", "liquidation",
    "solvency", "settlement", "reentrancy", "donation", "oracle", "migration",
    "adapter", "registry", "proxy", "implementation", "vesting", "slippage",
}


def lead_behaviors(lead: M.LeadCandidate) -> set:
    blob = " ".join([lead.title, lead.surface, lead.reason, " ".join(lead.notes)])
    beh = {b.lower() for b in detect_behaviors(blob)}
    for note in lead.notes:
        if note == "value-out":
            beh |= {"withdraw", "withdrawal"}
        elif note == "value-in":
            beh |= {"deposit"}
        elif note == "oracle-dependent":
            beh |= {"oracle", "price"}
        elif note == "privileged":
            beh |= {"admin", "owner"}
        elif note == "external-call":
            beh |= {"reentrancy"}
        elif note == "debt-or-liquidation":
            beh |= {"liquidation", "debt"}
    return beh


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _anchor_tokens(lead: M.LeadCandidate) -> list:
    contract = lead.surface.split(".")[0].lower() if "." in lead.surface else lead.surface.lower()
    func = lead.surface.split(".")[1].lower() if "." in lead.surface else ""
    anchors = [contract] if len(contract) >= 4 else []
    if len(func) >= 6:
        anchors.append(func)
    return anchors


def classify(
    lead: M.LeadCandidate,
    corpus: list,
    *,
    trusted_role_oos: bool,
    corpus_provided: bool,
) -> M.KnownIssueSignal:
    behaviors = lead_behaviors(lead)
    lead_shingles = token_shingles(
        " ".join([lead.title, lead.surface, lead.reason, " ".join(sorted(behaviors))])
    )
    privileged = "privileged" in lead.notes
    anchors = _anchor_tokens(lead)

    matched: set = set()
    sources: list = []
    evidence: list = []
    reasons: list = []
    best_sim = 0
    public_test = dup_known = similar = ack = documented = False

    for doc in corpus:
        low = doc.lower
        windows = []
        for tok in anchors:
            windows += windows_around(doc.text, tok, radius=_RADIUS)
        sim_pct = int(round(_jaccard(lead_shingles, doc.fingerprint.shingles) * 100))

        if not windows:
            if doc.kind in ("known", "audit"):
                shared = [b for b in behaviors if b and b in low]
                if any(b in _SPECIFIC_BEHAVIORS for b in shared):
                    similar = True
                    best_sim = max(best_sim, min(sim_pct, 45))
                    snip = ev.first_snippet(doc, [b for b in shared if b in _SPECIFIC_BEHAVIORS],
                                            reason="Similar specific behavior, different surface")
                    if snip:
                        evidence.append(snip.to_dict())
                        _add(sources, doc.rel_path)
            continue

        joined = " ".join(windows)
        beh_here = sorted({b for b in behaviors if b and b in joined})
        func_here = bool(anchors[1:]) and any(a in joined for a in anchors[1:])
        matched.update(beh_here)
        best_sim = max(best_sim, sim_pct, 40 if beh_here else sim_pct)

        # Public/local test coverage: require a real behavior or function-name match,
        # not just the generic word "test" near the contract name.
        if doc.is_test() and (beh_here or func_here):
            public_test = True
            snip = ev.first_snippet(doc, (beh_here + anchors) or anchors,
                                    reason="Public/local test exercises this behavior")
            if snip:
                evidence.append(snip.to_dict())
            _add(sources, doc.rel_path)

        if doc.kind in ("known", "audit"):
            has_dup = any(d in joined for d in DUP_TERMS)
            has_ack = any(a in joined for a in ACK_TERMS)
            # A duplicate/known verdict needs an *explicit* signal near the surface;
            # a neutral mention ("reviewed", "added after audit", "not covered") does
            # not make a lead a duplicate.
            if beh_here and has_dup:
                dup_known = True
            if beh_here and has_ack:
                ack = True
            if dup_known or ack:
                _add(sources, doc.rel_path)
                snip = ev.first_snippet(doc, (beh_here + anchors) or anchors,
                                        reason="Known/audit finding on the same surface")
                if snip:
                    evidence.append(snip.to_dict())

        if doc.kind in ("doc", "src") and beh_here and any(a in joined for a in ACK_TERMS):
            documented = True
            snip = ev.first_snippet(doc, beh_here, reason="Documented / by-design behavior")
            if snip:
                evidence.append(snip.to_dict())

    status, note = _status(privileged, trusted_role_oos, public_test, ack, dup_known,
                           documented, similar, corpus_provided or bool(corpus))
    confidence = _confidence(status, best_sim, bool(matched), public_test or ack or dup_known or documented)

    duplicate_risk = max(_DUP_SCORE.get(status, 50), best_sim if status in (M.KNOWN_LIKELY_DUP, M.KNOWN_SIMILAR) else 0)
    known_confidence = _KNOWN_CONFIDENCE_SCORE.get(status, 45)

    reasons.append(f"similarity {best_sim}/100 vs best local match; confidence {confidence}.")
    if matched:
        reasons.append(f"behavior overlap: {', '.join(sorted(matched))}.")
    reasons.append(f"verdict: {status} — {note}")

    return M.KnownIssueSignal(
        lead_id=lead.id,
        status=status,
        duplicate_risk_score=duplicate_risk,
        similarity_score=best_sim,
        confidence=confidence,
        public_test_covered=public_test,
        matched_terms=sorted(matched),
        sources=sources[:8],
        evidence=evidence[:8],
        reasons=reasons,
        note=note,
    )


def _status(privileged, trusted_role_oos, public_test, ack, dup_known, documented, similar, corpus_present):
    if privileged and trusted_role_oos:
        return M.KNOWN_OUT_OF_SCOPE, "Triggered only by a trusted role the scope marks out of scope."
    if privileged:
        return M.KNOWN_TRUSTED_ROLE, "Reachable only through a trusted/privileged role; not an external-attacker path."
    if public_test:
        return M.KNOWN_PUBLIC_TEST, "A public/local test already exercises this behavior."
    if ack:
        return M.KNOWN_ACK_RISK, "Found near an acknowledged / by-design / won't-fix note."
    if dup_known:
        return M.KNOWN_LIKELY_DUP, "Same surface and behavior appear in known/audit material."
    if documented:
        return M.KNOWN_DOCUMENTED, "Behavior is documented in the repository as expected."
    if similar:
        return M.KNOWN_SIMILAR, "Similar behavior appears in known material on a different surface."
    if corpus_present:
        return M.KNOWN_NO_MATCH, "No matching known issue found in the provided material."
    return M.KNOWN_UNKNOWN, "No known-issue material provided; dedup confidence is low."


def _confidence(status, best_sim, has_behavior, has_status_signal):
    if status in (M.KNOWN_PUBLIC_TEST, M.KNOWN_OUT_OF_SCOPE):
        return M.CONF_HIGH
    if status in (M.KNOWN_LIKELY_DUP, M.KNOWN_ACK_RISK, M.KNOWN_DOCUMENTED):
        return M.CONF_HIGH if (has_behavior and has_status_signal) else M.CONF_MEDIUM
    if status == M.KNOWN_TRUSTED_ROLE:
        return M.CONF_MEDIUM
    if status == M.KNOWN_SIMILAR:
        return M.CONF_MEDIUM if best_sim >= 40 else M.CONF_LOW
    if status == M.KNOWN_NO_MATCH:
        return M.CONF_MEDIUM if best_sim < 25 else M.CONF_LOW
    return M.CONF_LOW


def _add(items: list, value: str) -> None:
    if value and value not in items:
        items.append(value)
