"""Nonce ordering and replay-domain analysis."""
from __future__ import annotations

import re

from . import models as M


def _offset(pattern: str, body: str):
    match = re.search(pattern, body, re.I | re.S)
    return match.start() if match else None


def analyze_replay(operation: M.SignedOperation, body: str) -> M.ReplayAnalysis:
    nonce_present = "nonce" in operation.nonce_source.lower() or \
        operation.binding_matrix.field("nonce_or_sequence").signed
    sequence_present = "sequence" in operation.nonce_source.lower()
    consume = _offset(
        r"(?:nonce|sequence)\s*(?:\+\+|\+=\s*1|=\s*(?:nonce|sequence)\s*\+\s*1)"
        r"|used\w*\s*\[[^\]]+\]\s*=\s*true",
        body,
    )
    external = _offset(r"\.(?:call|delegatecall)\s*(?:\{|\()", body)
    consumed_before = consume is not None and (external is None or consume < external)
    chain_bound = operation.chain_binding
    wallet_bound = operation.wallet_binding
    expiry_bound = operation.binding_matrix.field("expiry").signed
    same_wallet = not nonce_present or not consumed_before
    cross_wallet = not wallet_bound
    cross_chain = not chain_bound
    requires_key_reuse = (cross_wallet or cross_chain) and not same_wallet
    if same_wallet:
        verdict = "NONCE_SEQUENCE_REPLAY"
    elif cross_wallet or cross_chain:
        verdict = "KEY_REUSE_REPLAY"
    else:
        verdict = "REPLAY_PROTECTED"
    return M.ReplayAnalysis(
        contract=operation.contract,
        function=operation.function,
        nonce_present=nonce_present,
        sequence_present=sequence_present,
        consumed_before_external_call=consumed_before,
        chain_id_bound=chain_bound,
        wallet_address_bound=wallet_bound,
        expiry_bound=expiry_bound,
        replay_same_wallet=same_wallet,
        replay_cross_wallet=cross_wallet,
        replay_cross_chain=cross_chain,
        requires_key_reuse=requires_key_reuse,
        verdict=verdict,
        evidence=[f"{operation.contract}.{operation.function}: replay domain and nonce ordering"],
    )
