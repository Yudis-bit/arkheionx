"""Threshold and signer-uniqueness analysis."""
from __future__ import annotations

import re

from . import models as M


def analyze_threshold(contract: str, function: str, body: str, source_text: str) -> M.ThresholdAnalysis | None:
    lowered = body.lower()
    if "ecrecover" not in lowered and "signaturechecker" not in lowered:
        return None
    membership = bool(re.search(r"(owners|signers|isowner)\s*\[", body, re.I))
    sorted_check = bool(re.search(r"signer\s*>\s*(last|previous)", body, re.I))
    seen_check = bool(re.search(r"(seen|usedsigner|approved)\s*\[\s*signer\s*\]", body, re.I))
    duplicate_check = sorted_check or seen_check
    zero_rejection = bool(re.search(r"signer\s*!=\s*address\s*\(\s*0\s*\)", body, re.I))
    low_s = bool(re.search(r"secp256k1n|half[_ ]?order|low[_ -]?s", source_text, re.I))
    v_norm = bool(re.search(r"\bv\s*<\s*27|v\s*\+=\s*27|v\s*==\s*27|v\s*==\s*28", source_text, re.I))
    threshold_source = "threshold" if "threshold" in lowered else ""
    if membership and duplicate_check and threshold_source:
        verdict = "SAFE_THRESHOLD_BINDING"
    elif membership and not duplicate_check and threshold_source:
        verdict = "DUPLICATE_SIGNER_THRESHOLD_BYPASS"
    else:
        verdict = "THRESHOLD_REVIEW_REQUIRED"
    malleability = (
        "same signer cannot increase unique signer count"
        if duplicate_check
        else "malleable signatures may count the same signer more than once"
    )
    return M.ThresholdAnalysis(
        contract=contract,
        function=function,
        required_threshold=threshold_source or "unknown",
        signer_membership_check=membership,
        duplicate_signer_check=duplicate_check,
        sorted_order_check=sorted_check,
        zero_address_rejection=zero_rejection,
        ecrecover_failure_handling=zero_rejection,
        low_s_check=low_s,
        v_normalization=v_norm,
        malleability_impact=malleability,
        unique_signer_count="enforced" if duplicate_check else "not enforced",
        verdict=verdict,
        evidence=[f"{contract}.{function}: signer recovery loop"],
    )
