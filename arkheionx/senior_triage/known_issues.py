"""Step 2 — known-issue / dedup mapping before any proof-of-concept.

Senior mode is brutal about duplicates. If a behavior is already covered by a
public test, an audit finding, or an acknowledged/by-design note, the lead should
die before anyone writes a test. This mapper is heuristic and local-only: it never
claims an exact duplicate unless the evidence is strong, and uses SIMILAR_KNOWN when
uncertain.
"""
from __future__ import annotations

from . import models as M
from .corpus import (
    ACK_TERMS,
    DUP_TERMS,
    TEST_INTENT,
    Doc,
    behavior_terms_in,
    is_test_doc,
    windows_around,
)

# Generic tokens that must not, on their own, count as a name match.
_STOP_TOKENS = {
    "value", "path", "function", "contract", "both", "none", "the", "and", "for",
    "out", "in", "lead", "move", "moves", "surface", "call", "external",
}

# Duplicate-risk score by status.
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


def lead_name_tokens(lead: M.LeadCandidate) -> list[str]:
    raw: list[str] = []
    for disp in lead.linked_functions:
        raw += disp.replace("(", " ").replace(")", " ").replace(".", " ").split()
    raw += lead.surface.replace(".", " ").split()
    raw += lead.title.replace("(", " ").replace(")", " ").replace(".", " ").split()
    tokens: list[str] = []
    seen: set[str] = set()
    for tok in raw:
        low = tok.strip().lower()
        if len(low) >= 4 and low not in _STOP_TOKENS and low not in seen:
            seen.add(low)
            tokens.append(low)
    return tokens


def lead_behaviors(lead: M.LeadCandidate) -> list[str]:
    blob = " ".join([lead.title, lead.surface, lead.reason, " ".join(lead.notes)])
    behaviors = set(behavior_terms_in(blob))
    # notes carry review-map risk signals; map a couple to behavior words.
    for note in lead.notes:
        if note == "value-out":
            behaviors.add("withdraw")
        if note == "oracle-dependent":
            behaviors.add("oracle")
    return sorted(behaviors)


def map_known_issue(
    lead: M.LeadCandidate,
    docs: list[Doc],
    *,
    trusted_role_oos: bool,
    corpus_provided: bool,
) -> M.KnownIssueSignal:
    behaviors = lead_behaviors(lead)
    privileged = "privileged" in lead.notes

    # The contract name is the unique anchor; a short function name like "fund"
    # would collide with words like "funds" elsewhere, so it is not used as a
    # doc-wide anchor. Behavior terms add specificity inside the contract window.
    contract_token = lead.surface.split(".")[0].lower() if "." in lead.surface else lead.surface.lower()
    func_token = lead.surface.split(".")[1].lower() if "." in lead.surface else ""
    anchor_tokens = [contract_token] if len(contract_token) >= 4 else []
    if len(func_token) >= 6:
        anchor_tokens.append(func_token)

    matched_terms: set[str] = set()
    sources: list[str] = []
    public_test = False
    dup_known = False
    similar = False
    ack = False
    documented = False
    radius = 90

    for doc in docs:
        low = doc.lower
        windows = []
        for tok in anchor_tokens:
            windows += windows_around(doc.text, tok, radius=radius)

        if not windows:
            # No anchor in this doc: at most a weak "similar" hit on behavior alone.
            if doc.kind in ("known", "audit") and any(b and b in low for b in behaviors):
                similar = True
                _add(sources, doc.rel_path)
            continue

        joined = " ".join(windows)
        beh_in_window = sorted({b for b in behaviors if b and b in joined})
        matched_terms.update(beh_in_window)

        if is_test_doc(doc):
            if beh_in_window or any(t in joined for t in TEST_INTENT):
                public_test = True
                _add(sources, doc.rel_path)

        if doc.kind in ("known", "audit"):
            _add(sources, doc.rel_path)
            if beh_in_window:
                dup_known = True
            else:
                similar = True
            if any(a in joined for a in ACK_TERMS):
                ack = True
            if any(d in joined for d in DUP_TERMS):
                dup_known = True

        if doc.kind in ("doc", "src"):
            if beh_in_window and any(a in joined for a in ACK_TERMS):
                documented = True
                _add(sources, doc.rel_path)

    # Status precedence: the most blocking verdict wins.
    if privileged and trusted_role_oos:
        status = M.KNOWN_OUT_OF_SCOPE
        note = "Triggered only by a trusted role the scope marks out of scope."
    elif privileged:
        status = M.KNOWN_TRUSTED_ROLE
        note = "Reachable only through a trusted/privileged role; not an external-attacker path."
    elif public_test:
        status = M.KNOWN_PUBLIC_TEST
        note = "A public/local test already exercises this behavior."
    elif ack:
        status = M.KNOWN_ACK_RISK
        note = "Found near an acknowledged / by-design / won't-fix note."
    elif dup_known:
        status = M.KNOWN_LIKELY_DUP
        note = "Same surface and behavior appear in known/audit material."
    elif documented:
        status = M.KNOWN_DOCUMENTED
        note = "Behavior is documented in the repository as expected."
    elif similar:
        status = M.KNOWN_SIMILAR
        note = "Similar behavior appears in known material on a different surface."
    elif corpus_provided or docs:
        status = M.KNOWN_NO_MATCH
        note = "No matching known issue found in the provided material."
    else:
        status = M.KNOWN_UNKNOWN
        note = "No known-issue material provided; dedup confidence is low."

    return M.KnownIssueSignal(
        lead_id=lead.id,
        status=status,
        duplicate_risk_score=_DUP_SCORE.get(status, 50),
        public_test_covered=public_test,
        matched_terms=sorted(matched_terms),
        sources=sources[:8],
        note=note,
    )


def trusted_role_risk(lead: M.LeadCandidate, signal: M.KnownIssueSignal) -> int:
    if signal.status in (M.KNOWN_TRUSTED_ROLE, M.KNOWN_OUT_OF_SCOPE) and "privileged" in lead.notes:
        return 85
    if "privileged" in lead.notes:
        return 70
    return 10


def _add(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)
