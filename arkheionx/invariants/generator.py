"""Invariant generator (Layer 4).

Instantiates invariant templates against state transitions and evaluates, for
each, whether it looks *suspicious here* using semantic signals (flags, data
flow, entities, raw body ordering). Only suspicious invariants become candidates
downstream — "no finding until an invariant breaks."
"""
from __future__ import annotations

import re

from . import models as M
from .templates import TEMPLATES
from arkheionx.semantic import models as SM


def _bodies(smap):
    parse = getattr(smap, "_parse", None)
    return getattr(parse, "bodies", {}) if parse else {}


def _body_text(bodies, qn):
    fb = bodies.get(qn)
    return fb.body if fb is not None and fb.body else ""


def _route_field_in_consent(smap, function) -> bool:
    """True if a route-shaped calldata field is bound into a hash in this function."""
    hashed = [h for h in smap.dataflow_hints
              if h.function == function and h.sink_kind == SM.SINK_HASH_INPUT]
    return any(re.search(r"data|route|path|swap", h.source_expr, re.I) for h in hashed)


def _suspicion(family, tr, smap, emap, bodies):
    flags = set(tr.flags)
    body = _body_text(bodies, tr.function)
    etypes = emap.types() if emap is not None else set()
    reasons = []

    if family == "DEBT_REPAYMENT_RECONCILIATION":
        if "has_division" in flags:
            reasons.append("Per-tranche/independent integer division floors lender credit, so "
                           "summed credit can be strictly less than the debt reduction.")
            # debt reduced before distribution?
            dm = re.search(r"\bdebt\b", body)
            cm = re.search(r"_?distribut|_?settle|_?credit", body)
            if dm and cm and dm.start() < cm.start():
                reasons.append("Debt is reduced before per-lender distribution is computed.")
            if "Collateral" in etypes and re.search(r"status\s*=|collateral", body, re.I):
                reasons.append("Loan close / collateral release keys on the debt counter, not on "
                               "proven lender settlement.")
        return bool(reasons), reasons

    if family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA":
        if "calldata_route" in flags:
            reasons.append("Counterparty-controlled calldata reaches a value path (swap route).")
            if not _route_field_in_consent(smap, tr.function) and not any(
                    _route_field_in_consent(smap, q) for q in bodies):
                reasons.append("The consent/terms hash does not bind that calldata.")
            if not re.search(r"minRefund|maxInput|minOut|minReturn|slippage", body, re.I):
                reasons.append("No min-refund / max-input / minOut guard protects the victim.")
        return bool(reasons), reasons

    if family == "BORROW_CONSERVATION":
        if "ext_before_write" in flags:
            reasons.append("An external call occurs before a protecting state write.")
        if "calldata_route" in flags and "Collateral" in etypes and not re.search(
                r"escrow|transferFrom\([^)]*collateral", body, re.I):
            reasons.append("Funds may be released without a clear collateral-escrow effect.")
        return bool(reasons), reasons

    if family == "DEPOSIT_CONSUMPTION":
        # The double-use / reentrancy window only matters if the deposit is actually
        # *consumed* (deleted / flag cleared / status changed) after an external call.
        # A plain credit increment after a pull is NOT a consumption bug (it is the
        # actual-received-vs-credited shape, handled by SWAP_ACTUAL_RECEIVED).
        consume_effect = re.search(
            r"\bdelete\b|\.active\s*=\s*false|\bconsumed\s*=\s*true|\.status\s*=\s*(?!=)"
            r"|\bstatus\s*=\s*(?!=)|\.used\s*=\s*true",
            body, re.I)
        if "ext_before_write" in flags and consume_effect:
            reasons.append("The deposit's active/consumed flag is cleared AFTER an external "
                           "transfer, opening a reentrancy / double-use window.")
        if re.search(r"mapping\s*\(\s*bytes32", body) and not re.search(r"token|amount|target", body, re.I):
            reasons.append("Deposit key may omit value-affecting context (token/amount/target).")
        return bool(reasons), reasons

    if family == "VAULT_SHARE_ASSET_RECONCILIATION":
        if "balance_based_assets" in flags:
            reasons.append("totalAssets is balance-based, so a direct donation inflates the share "
                           "price.")
        if not re.search(r"require\s*\([^;]*shares?[^;]*(>|!=)\s*0", body, re.I) and \
                not re.search(r"deadShares|_decimalsOffset|1000|MINIMUM_LIQUIDITY", body):
            reasons.append("No zero-share guard / dead-shares / offset detected.")
        # only suspicious if the inflation vector is present
        return ("balance_based_assets" in flags), reasons

    if family == "COLLATERAL_STATUS_RELEASE":
        rel = re.search(r"collateral|released|status", body, re.I)
        if rel and "has_division" in flags:
            reasons.append("Collateral release is gated on a debt counter affected by rounding, "
                           "not on proven full settlement.")
        return bool(reasons), reasons

    if family == "SWAP_ACTUAL_RECEIVED_VS_CREDITED":
        if "credit_no_balance_delta" in flags:
            reasons.append("Protocol credits the nominal transferred amount, not the measured "
                           "balance delta (balanceOf before/after). A fee-on-transfer / rebasing "
                           "token then over-credits the depositor versus assets actually received.")
        elif "Adapter" in etypes and "balanceof" not in body.lower():
            reasons.append("Credited output is not reconciled against a measured balance delta.")
        return bool(reasons), reasons

    if family == "ORACLE_DECIMAL_NORMALIZATION":
        if "oracle_hardcoded_scale" in flags:
            reasons.append("A hardcoded scale (e.g. 1e18) is applied to an oracle price without "
                           "reading the feed's decimals() or the token's decimals(); mixed-decimal "
                           "mispricing over-credits the borrow/collateral value.")
        elif "oracle_value_math" in flags:
            reasons.append("An oracle price flows into a value/limit computation without an "
                           "explicit decimal-normalization step.")
        elif re.search(r"1e18|1e8|10\s*\*\*", body) and re.search(r"decimals", body, re.I):
            reasons.append("Mixed/hardcoded decimal scaling near a price conversion.")
        return bool(reasons), reasons

    if family == "CROSS_CHAIN_SUPPLY_CONSERVATION":
        if "xchain_overmint" in flags:
            reasons.append("A cross-chain message mints on the destination with no "
                           "processed/consumed/replay guard, so the same message id can be "
                           "replayed to mint repeatedly (destination supply not conserved).")
        elif not re.search(r"processed|consumed|nonce|usedHash|replay", body, re.I):
            reasons.append("No message-consumed/replay guard detected around mint/burn.")
        return bool(reasons), reasons

    return False, reasons


def build_invariants(smap, emap, tmap) -> M.InvariantSet:
    bodies = _bodies(smap)
    out = M.InvariantSet(root=smap.root)
    seen = set()
    idx = 0
    for tr in tmap.transitions:
        for family in tr.possible_invariants:
            tpl = TEMPLATES.get(family)
            if tpl is None:
                continue
            key = (family, tr.function)
            if key in seen:
                continue
            seen.add(key)
            suspicious, reasons = _suspicion(family, tr, smap, emap, bodies)
            idx += 1
            related_entities = [e for e in (tpl.victim, tpl.asset)]
            # Testability override: some shapes the template marks fork-only are in
            # fact locally provable (a fee-on-transfer mock proves nominal over-credit;
            # a second identical call proves cross-chain message replay). Keep fork for
            # the cases where real deployed external state sets the loss.
            testability = tpl.testability
            flagset = set(tr.flags)
            if family == "SWAP_ACTUAL_RECEIVED_VS_CREDITED" and "credit_no_balance_delta" in flagset:
                testability = M.T_LOCAL
            elif family == "CROSS_CHAIN_SUPPLY_CONSERVATION" and "xchain_overmint" in flagset:
                testability = M.T_LOCAL
            inv = M.Invariant(
                id=f"INV-{idx:03d}", family=family, title=tpl.title,
                description=tpl.description.format(function=tr.function.split(".")[-1],
                                                   contract=tr.contract),
                related_entities=sorted(emap.types() & _family_entities(family)) if emap else [],
                related_functions=[tr.function], state_transition=tr.id,
                assertion_form=tpl.assertion_form, attacker_capability=tpl.attacker,
                victim=tpl.victim, asset=tpl.asset, why_it_matters=tpl.why_it_matters,
                testability=testability, severity_hint=tpl.severity_hint,
                suspicious=suspicious, suspicion_reasons=reasons,
                confidence=M.MEDIUM if suspicious else M.LOW,
            )
            out.invariants.append(inv)
    return out


def _family_entities(family: str) -> set:
    table = {
        "DEBT_REPAYMENT_RECONCILIATION": {"Debt", "Loan", "Tranche", "Lender", "Repayment"},
        "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA": {"Lender", "Deposit", "Refund", "Borrower"},
        "BORROW_CONSERVATION": {"Loan", "Collateral", "Lender", "Borrower"},
        "DEPOSIT_CONSUMPTION": {"Deposit"},
        "SWAP_ACTUAL_RECEIVED_VS_CREDITED": {"Adapter", "Router", "Asset"},
        "VAULT_SHARE_ASSET_RECONCILIATION": {"Vault", "Share", "Asset", "ExchangeRate"},
        "COLLATERAL_STATUS_RELEASE": {"Collateral", "Loan"},
        "ORACLE_DECIMAL_NORMALIZATION": {"OraclePrice", "ExchangeRate"},
        "CROSS_CHAIN_SUPPLY_CONSERVATION": {"CrossChainSupply"},
    }
    return table.get(family, set())
