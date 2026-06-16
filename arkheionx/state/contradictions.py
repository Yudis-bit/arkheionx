"""State-machine contradiction detector (Layer 3+).

Reads the reconstructed state transitions (lifecycle + shape flags + bodies) and
names broken-lifecycle contradictions: a loan marked Repaid while lenders are not
settled, a deposit consumed yet still withdrawable, a credit that exceeds what was
actually received, a cross-chain message minted without consuming its id, and so on.

Each contradiction points at the transition, the likely invariant, the PoC family,
and a severity hint. Heuristic / medium confidence — review context, not a finding.
No protocol/token name is encoded.
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field

# Contradiction families.
REPAID_BUT_LENDER_NOT_SETTLED = "REPAID_BUT_LENDER_NOT_SETTLED"
ACTIVE_WITHOUT_COLLATERAL_ESCROW = "ACTIVE_WITHOUT_COLLATERAL_ESCROW"
FUNDS_TRANSFERRED_WITHOUT_ACTIVE_LOAN = "FUNDS_TRANSFERRED_WITHOUT_ACTIVE_LOAN"
COLLATERAL_RELEASED_WITH_DEBT = "COLLATERAL_RELEASED_WITH_DEBT"
DEPOSIT_CONSUMED_STILL_WITHDRAWABLE = "DEPOSIT_CONSUMED_STILL_WITHDRAWABLE"
DEPOSIT_EXPIRED_BUT_CONSUMED = "DEPOSIT_EXPIRED_BUT_CONSUMED"
DEPOSIT_USED_FOR_WRONG_CONTEXT = "DEPOSIT_USED_FOR_WRONG_CONTEXT"
ZERO_SHARES_FOR_NONZERO_ASSETS = "ZERO_SHARES_FOR_NONZERO_ASSETS"
CREDIT_EXCEEDS_ACTUAL_RECEIVED = "CREDIT_EXCEEDS_ACTUAL_RECEIVED"
ORACLE_PRICE_ACCEPTED_STALE = "ORACLE_PRICE_ACCEPTED_STALE"
ORACLE_DECIMAL_MISMATCH = "ORACLE_DECIMAL_MISMATCH"
MESSAGE_PROCESSED_NONCE_NOT_CONSUMED = "MESSAGE_PROCESSED_NONCE_NOT_CONSUMED"
DESTINATION_MINT_EXCEEDS_SOURCE_LOCK = "DESTINATION_MINT_EXCEEDS_SOURCE_LOCK"
STATUS_WRITE_AFTER_UNTRUSTED_EXTERNAL_CALL = "STATUS_WRITE_AFTER_UNTRUSTED_EXTERNAL_CALL"
CLAIM_CREATED_WITHOUT_ASSET_BACKING = "CLAIM_CREATED_WITHOUT_ASSET_BACKING"


@dataclass
class Contradiction:
    id: str = ""
    family: str = ""
    transition: str = ""
    contract: str = ""
    evidence: list = field(default_factory=list)
    likely_invariant: str = ""
    poc_family: str = ""
    severity_hint: str = ""
    confidence: str = "MEDIUM"
    warning: str = "Heuristic lifecycle contradiction; confirm by hand."

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class ContradictionSet:
    root: str = ""
    contradictions: list = field(default_factory=list)

    def families(self):
        return {c.family for c in self.contradictions}

    def to_dict(self) -> dict:
        return {
            "schema_version": "v10-state-contradictions",
            "root": self.root,
            "contradiction_count": len(self.contradictions),
            "contradictions": [c.to_dict() for c in self.contradictions],
        }


def _bodies(smap):
    parse = getattr(smap, "_parse", None)
    return getattr(parse, "bodies", {}) if parse else {}


def _body(bodies, qn):
    fb = bodies.get(qn)
    return fb.body if fb is not None and fb.body else ""


def find_contradictions(smap, emap, tmap) -> ContradictionSet:
    out = ContradictionSet(root=smap.root)
    bodies = _bodies(smap)
    etypes = emap.types() if emap is not None else set()
    idx = 0

    def add(**kw):
        nonlocal idx
        idx += 1
        out.contradictions.append(Contradiction(id=f"SC-{idx:03d}", **kw))

    for tr in tmap.transitions:
        flags = set(tr.flags)
        body = _body(bodies, tr.function)
        low = body.lower()
        status_blob = " ".join(tr.status_changes).lower()

        # Repay closes the loan on the debt counter while lenders may be short.
        if tr.lifecycle == "repay" and "has_division" in flags:
            settled = bool(re.search(r"repaid|status\s*=\s*1|closed|settled|finaliz", status_blob + low))
            if settled or re.search(r"release|collateral", low):
                add(family=REPAID_BUT_LENDER_NOT_SETTLED, transition=tr.function,
                    contract=tr.contract,
                    evidence=["per-tranche flooring (has_division)"] + tr.status_changes[:3],
                    likely_invariant="DEBT_REPAYMENT_RECONCILIATION",
                    poc_family="DEBT_REPAYMENT_RECONCILIATION",
                    severity_hint="VALID_BUT_LOW unless per-call principal loss is meaningful")
            if re.search(r"release|collateral", low):
                add(family=COLLATERAL_RELEASED_WITH_DEBT, transition=tr.function,
                    contract=tr.contract,
                    evidence=["collateral release keyed on a rounding-affected debt counter"],
                    likely_invariant="COLLATERAL_STATUS_RELEASE",
                    poc_family="COLLATERAL_STATUS_RELEASE",
                    severity_hint="MEDIUM if collateral frees while lenders are short")

        # Credit exceeds actual received (nominal credit, no measured delta).
        if "credit_no_balance_delta" in flags:
            add(family=CREDIT_EXCEEDS_ACTUAL_RECEIVED, transition=tr.function,
                contract=tr.contract,
                evidence=["transferFrom-in then credit nominal amount; no balanceOf delta"],
                likely_invariant="SWAP_ACTUAL_RECEIVED_VS_CREDITED",
                poc_family="SWAP_ACTUAL_RECEIVED_VS_CREDITED",
                severity_hint="MEDIUM; depositor over-credited vs assets received")

        # Oracle decimal mismatch / stale acceptance.
        if "oracle_hardcoded_scale" in flags:
            add(family=ORACLE_DECIMAL_MISMATCH, transition=tr.function, contract=tr.contract,
                evidence=["hardcoded scale on an oracle price; feed/token decimals() ignored"],
                likely_invariant="ORACLE_DECIMAL_NORMALIZATION",
                poc_family="ORACLE_DECIMAL_NORMALIZATION",
                severity_hint="HIGH if unprivileged over-borrow is reachable")
        elif "oracle_value_math" in flags and not re.search(r"updatedat|staleness|block\.timestamp", low):
            add(family=ORACLE_PRICE_ACCEPTED_STALE, transition=tr.function, contract=tr.contract,
                evidence=["oracle price used without a freshness (updatedAt) check"],
                likely_invariant="ORACLE_FRESHNESS_AND_DECIMALS",
                poc_family="ORACLE_DECIMAL_NORMALIZATION",
                severity_hint="depends on exploit path")

        # Cross-chain destination overmint / message not consumed.
        if "xchain_overmint" in flags:
            add(family=MESSAGE_PROCESSED_NONCE_NOT_CONSUMED, transition=tr.function,
                contract=tr.contract,
                evidence=["mint on an incoming message id with no processed/consumed guard"],
                likely_invariant="CROSS_CHAIN_SUPPLY_CONSERVATION",
                poc_family="CROSS_CHAIN_SUPPLY_CONSERVATION",
                severity_hint="HIGH; replay mints again")
            add(family=DESTINATION_MINT_EXCEEDS_SOURCE_LOCK, transition=tr.function,
                contract=tr.contract,
                evidence=["destination mint not reconciled against source lock/burn"],
                likely_invariant="CROSS_CHAIN_SUPPLY_CONSERVATION",
                poc_family="CROSS_CHAIN_SUPPLY_CONSERVATION",
                severity_hint="HIGH; destination supply can exceed source")

        # Deposit consumed via external call before the flag is cleared.
        if tr.lifecycle in ("deposit_consume", "deposit") and "ext_before_write" in flags:
            consume = re.search(r"\.active\s*=\s*false|\bdelete\b|consumed\s*=\s*true|\.used\s*=\s*true", low)
            if consume:
                add(family=DEPOSIT_CONSUMED_STILL_WITHDRAWABLE, transition=tr.function,
                    contract=tr.contract,
                    evidence=["external transfer precedes clearing the active/consumed flag"],
                    likely_invariant="DEPOSIT_CONSUMPTION", poc_family="DEPOSIT_CONSUMPTION",
                    severity_hint="HIGH if double-use / reentrancy drains the deposit")
                add(family=STATUS_WRITE_AFTER_UNTRUSTED_EXTERNAL_CALL, transition=tr.function,
                    contract=tr.contract,
                    evidence=["status/flag write occurs after an untrusted external call"],
                    likely_invariant="EXTERNAL_CALL_ORDERING",
                    poc_family="DEPOSIT_CONSUMPTION",
                    severity_hint="depends on reentrancy reachability")

        # Vault: zero-share deposit possible (balance-based assets, no guard).
        if "balance_based_assets" in flags and tr.lifecycle in ("vault_deposit",):
            if not re.search(r"require\s*\([^;]*shares?[^;]*(>|!=)\s*0|deadshares|_decimalsoffset", low):
                add(family=ZERO_SHARES_FOR_NONZERO_ASSETS, transition=tr.function,
                    contract=tr.contract,
                    evidence=["balance-based totalAssets, no zero-share / dead-shares guard"],
                    likely_invariant="VAULT_SHARE_ASSET_RECONCILIATION",
                    poc_family="VAULT_SHARE_ASSET_RECONCILIATION",
                    severity_hint="HIGH if a later depositor is rounded to zero shares")

    return out
