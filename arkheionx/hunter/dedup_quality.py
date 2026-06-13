"""Dedup quality model for hunter mode.

Two layers on top of the proven senior-triage corpus + semantic dedup engines:

1. A *corpus quality* verdict for the whole run — DEDUP_BLIND / DEDUP_PARTIAL /
   DEDUP_USABLE / DEDUP_STRONG — so a researcher knows how much to trust a
   "no duplicate found" result.
2. A per-lead known-match verdict mapped to the V9 vocabulary, carrying a confidence
   cap derived from the corpus quality. With an empty corpus the engine says
   DEDUP_BLIND honestly rather than pretending dedup is usable.
"""
from __future__ import annotations

from arkheionx.senior_triage import dedup_v2
from arkheionx.senior_triage import models as SM

from . import models as M

# Senior known-status -> V9 known-match status.
_SENIOR_TO_V9 = {
    SM.KNOWN_NO_MATCH: M.NO_MATCH_FOUND,
    SM.KNOWN_SIMILAR: M.SIMILAR_KNOWN,
    SM.KNOWN_LIKELY_DUP: M.LIKELY_DUPLICATE,
    SM.KNOWN_DOCUMENTED: M.DOCUMENTED_BEHAVIOR,
    SM.KNOWN_ACK_RISK: M.ACKNOWLEDGED_RISK,
    SM.KNOWN_OUT_OF_SCOPE: M.OUT_OF_SCOPE,
    SM.KNOWN_TRUSTED_ROLE: M.TRUSTED_ROLE_ONLY,
    SM.KNOWN_PUBLIC_TEST: M.PUBLIC_TEST_COVERED,
    SM.KNOWN_UNKNOWN: M.KNOWN_UNKNOWN,
}

# Corpus quality -> the strongest per-lead confidence the run is allowed to assert.
_QUALITY_CONF_CAP = {
    M.DEDUP_BLIND: M.LOW,
    M.DEDUP_PARTIAL: M.MEDIUM,
    M.DEDUP_USABLE: M.HIGH,
    M.DEDUP_STRONG: M.HIGH,
}

_CONF_RANK = {M.LOW: 0, M.MEDIUM: 1, M.HIGH: 2}


def assess_dedup_quality(corpus: list, *, known_provided: bool, audits_provided: bool) -> M.DedupQuality:
    """Grade the known-issue corpus for the whole run."""
    known_docs = [d for d in corpus if getattr(d, "kind", "") == "known"]
    audit_docs = [d for d in corpus if getattr(d, "kind", "") == "audit"]
    test_docs = [d for d in corpus if getattr(d, "is_test", lambda: False)()]
    unparsed = [getattr(d, "rel_path", "?") for d in corpus
                if getattr(d, "note", "") == M.UNPARSED_PDF]

    # "Useful" material = explicit known/audit docs or repo tests that actually
    # exercise behavior. A corpus with only README-style docs is still blind for dedup.
    useful_known = len(known_docs) + len(audit_docs)
    useful_tests = len(test_docs)
    reasons: list = []

    if useful_known == 0 and useful_tests == 0:
        status = M.DEDUP_BLIND
        reasons.append("No known-issue / audit documents and no behavior-exercising tests were parsed.")
    elif useful_known == 0:
        # Only local tests; no external known/audit material.
        status = M.DEDUP_PARTIAL
        reasons.append("Local tests parsed but no external known/audit material provided.")
    elif known_docs and audit_docs and useful_tests and not unparsed:
        status = M.DEDUP_STRONG
        reasons.append("Known issues, audits, and tests parsed with located evidence.")
    elif (known_docs or audit_docs) and (useful_tests or known_docs and audit_docs):
        status = M.DEDUP_USABLE
        reasons.append("Known/audit material parsed sufficiently for evidence-backed dedup.")
    else:
        status = M.DEDUP_PARTIAL
        reasons.append("Some material parsed, but important known/audit/test coverage is missing.")

    if unparsed:
        reasons.append(f"{len(unparsed)} PDF(s) could not be parsed ({M.UNPARSED_PDF}).")
        if status == M.DEDUP_STRONG:
            status = M.DEDUP_USABLE
    if not known_provided and not audits_provided and status not in (M.DEDUP_BLIND,):
        reasons.append("No --known/--audits folders supplied; dedup relies on repo material only.")

    return M.DedupQuality(
        status=status, parsed_docs=len(corpus), known_docs=len(known_docs),
        audit_docs=len(audit_docs), test_docs=len(test_docs), unparsed=unparsed, reasons=reasons,
    )


def _cap_confidence(confidence: str, quality_status: str) -> str:
    cap = _QUALITY_CONF_CAP.get(quality_status, M.LOW)
    return confidence if _CONF_RANK.get(confidence, 0) <= _CONF_RANK.get(cap, 0) else cap


def classify_lead(
    senior_lead,
    corpus: list,
    quality: M.DedupQuality,
    *,
    trusted_role_oos: bool,
    corpus_provided: bool,
) -> M.KnownMatch:
    """Run semantic dedup for one (senior) lead and map it to the V9 known-match shape."""
    sig = dedup_v2.classify(senior_lead, corpus, trusted_role_oos=trusted_role_oos,
                            corpus_provided=corpus_provided)
    v9_status = _SENIOR_TO_V9.get(sig.status, M.KNOWN_UNKNOWN)

    # In a blind corpus, an apparent "no match" is not trustworthy: report UNKNOWN.
    if quality.status == M.DEDUP_BLIND and v9_status == M.NO_MATCH_FOUND:
        v9_status = M.KNOWN_UNKNOWN
        sig.reasons.append("Corpus is DEDUP_BLIND: 'no match' is unverified, reported as UNKNOWN.")

    confidence_cap = _cap_confidence(sig.confidence, quality.status)
    return M.KnownMatch(
        lead_id=getattr(senior_lead, "id", ""),
        dedup_status=quality.status,
        known_match_status=v9_status,
        known_issue_confidence=confidence_cap,
        dedup_similarity_score=round(sig.similarity_score / 100.0, 2),
        dedup_evidence=sig.evidence,
        dedup_reasoning=sig.reasons,
        dedup_confidence_cap=confidence_cap,
        public_test_covered=sig.public_test_covered,
    )
