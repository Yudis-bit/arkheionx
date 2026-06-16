"""Fork requirement builder (Layer 8).

Decides which candidates need fork proof and what that proof must verify. Local
only: the plan references env var names, never URLs or keys, and never broadcasts.
"""
from __future__ import annotations

import re

from . import env_detect
from .models import ForkRequirement

_FORK_LABELS = {"NEEDS_FORK_PROOF", "NEEDS_REAL_ASSET_PROOF"}

_REASON = {
    "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA":
        "Real AMM liquidity / exactOutput pool depth sets the input consumed and the "
        "victim's refund delta; local mocks cannot quantify the buffer loss.",
    "SWAP_ACTUAL_RECEIVED_VS_CREDITED":
        "Real token/pool behavior (fee-on-transfer, slippage, fee tier and liquidity) "
        "sets the actual received amount.",
    "CROSS_CHAIN_SUPPLY_CONSERVATION":
        "Deployed endpoint/peer configuration and token decimals set cross-chain "
        "mint/burn/lock/unlock accounting.",
}

_EXTERNAL_HINT = re.compile(r"router|adapter|swap|pool|dex|timelock|oracle|aggregator|endpoint",
                            re.I)


def _infer_chain(scope) -> str:
    if not scope:
        return "unknown"
    chain = (scope.get("chain") or scope.get("network") or "").strip()
    if chain:
        return chain
    text = " ".join(str(v) for v in scope.values())
    for c in ("arbitrum", "optimism", "base", "polygon", "mainnet", "ethereum"):
        if c in text.lower():
            return c
    return "unknown"


def _targets(candidate) -> list:
    out = []
    for edge in candidate.call_sequence:
        # "Caller -> Callee (kind)"
        m = re.search(r"->\s*([^()]+?)\s*\(", edge)
        if m:
            callee = m.group(1).strip()
            if _EXTERNAL_HINT.search(callee) or "<external>" in callee:
                out.append(callee)
    return sorted(set(out))


def build_fork_plan(graph, smap=None, scope=None) -> list:
    chain = _infer_chain(scope)
    env_name = env_detect.env_for_chain(chain)
    reqs = []
    for c in graph.candidates:
        needs = c.fork_requirement or c.economic_severity in _FORK_LABELS
        if not needs:
            continue
        reqs.append(ForkRequirement(
            candidate_id=c.id, chain=chain, required_env=[env_name],
            reason=_REASON.get(c.invariant_family,
                               "Behavior depends on deployed external state; verify on a fork."),
            contracts_to_verify=_targets(c) or ["(entry contract + external call targets)"],
            static_calls_needed=[
                "verify deployed code at the adapter/router/pool/timelock address",
                "read pool liquidity / slot0 (or equivalent depth)",
                "read token.decimals() for each asset",
            ],
            candidate_tests=[c.poc_skeleton or c.id],
            do_not_broadcast=True, secret_redaction_required=True,
        ))
    return reqs
