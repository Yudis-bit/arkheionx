"""Named taint / dataflow detectors (semantic core, Layer 1+).

Surfaces attacker-controlled or external-return data flows into value-affecting
sinks as first-class, named findings — e.g. calldata that reaches a value sink but
is not bound into the consent hash, an oracle return that sets a borrow limit, a
credit written from a nominal (not measured) amount, or a message id minted without
a consume guard.

Built on the fallback semantic map (function bodies + calldata->sink dataflow hints
+ external-call ordering), so findings are heuristic and carry a confidence. This is
review context, never a finding. No protocol/token name is encoded.
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field

from . import models as M

# Detector names.
CALLDATA_TO_SWAP_ROUTE = "CALLDATA_TO_SWAP_ROUTE"
CALLDATA_TO_REFUND_AFFECTING_ROUTE = "CALLDATA_TO_REFUND_AFFECTING_ROUTE"
CALLDATA_TO_TRANSFER_RECIPIENT = "CALLDATA_TO_TRANSFER_RECIPIENT"
CALLDATA_TO_TRANSFER_AMOUNT = "CALLDATA_TO_TRANSFER_AMOUNT"
CALLDATA_TO_HASH_INPUT = "CALLDATA_TO_HASH_INPUT"
CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK = "CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK"
ORACLE_RETURN_TO_BORROW_LIMIT = "ORACLE_RETURN_TO_BORROW_LIMIT"
ADAPTER_RETURN_TO_CREDIT = "ADAPTER_RETURN_TO_CREDIT"
CREDIT_WRITE_FROM_NOMINAL_AMOUNT = "CREDIT_WRITE_FROM_NOMINAL_AMOUNT"
MESSAGE_ID_TO_MINT_WITHOUT_CONSUME = "MESSAGE_ID_TO_MINT_WITHOUT_CONSUME"
MSG_SENDER_TO_COLLATERAL_OWNER = "MSG_SENDER_TO_COLLATERAL_OWNER"
STATUS_WRITE_AFTER_EXTERNAL_CALL = "STATUS_WRITE_AFTER_EXTERNAL_CALL"

_ROUTE_WORDS = re.compile(r"(swapdata|calldata|payload|route|path|\bdata\b|params|adapterdata|extradata)", re.I)
_REFUND_SINK = re.compile(r"(withdraw|swap|redeem|exactoutput|refund|unwrap)", re.I)
_ORACLE_READ = re.compile(r"latestrounddata|latestanswer|getprice|pricefeed|\.price\s*\(", re.I)
_STATUS_WRITE = re.compile(r"\bdelete\b|\.active\s*=|\bconsumed\s*=|\.status\s*=|status\s*=\s*(?!=)|\.used\s*=", re.I)
_CONSUME_GUARD = re.compile(r"processed|consumed|usedhash|replay|\bnonce\b|seen\b", re.I)


@dataclass
class TaintFinding:
    detector: str = ""
    function: str = ""
    source_expr: str = ""
    source_kind: str = ""
    sink_expr: str = ""
    sink_kind: str = ""
    invariant_family: str = ""
    attacker_role: str = ""
    confidence: str = M.MEDIUM
    evidence_lines: list = field(default_factory=list)
    missing_binding: str = ""
    note: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _bodies(smap):
    parse = getattr(smap, "_parse", None)
    return getattr(parse, "bodies", {}) if parse else {}


def _body_text(bodies, qn):
    fb = bodies.get(qn)
    return fb.body if fb is not None and fb.body else ""


def _evidence(smap, qn):
    fn = smap.function(qn)
    if not fn:
        return []
    c = smap.contract(fn.contract)
    return [f"{c.file}:{fn.line_start}"] if c else []


def _calldata_findings(smap, hints):
    """Findings derived from calldata->sink dataflow hints (incl. the consent gap)."""
    out = []
    route_hints = [h for h in hints if h.tag == M.TAG_CALLDATA_TO_SWAP_ROUTE]
    hash_hints = [h for h in hints if h.sink_kind == M.SINK_HASH_INPUT]
    transfer_hints = [h for h in hints if h.tag == M.TAG_CALLDATA_TO_TRANSFER]
    route_is_hashed = any(_ROUTE_WORDS.search(h.source_expr or "") for h in hash_hints)

    for h in route_hints:
        out.append(TaintFinding(
            detector=CALLDATA_TO_SWAP_ROUTE, function=h.function,
            source_expr=h.source_expr, source_kind=h.source_kind,
            sink_expr=h.sink_expr, sink_kind=h.sink_kind,
            invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
            attacker_role="counterparty supplying calldata",
            confidence=h.confidence, evidence_lines=[f"line {h.sink_line}"]))
        if _REFUND_SINK.search(h.sink_expr or ""):
            out.append(TaintFinding(
                detector=CALLDATA_TO_REFUND_AFFECTING_ROUTE, function=h.function,
                source_expr=h.source_expr, source_kind=h.source_kind,
                sink_expr=h.sink_expr, sink_kind=h.sink_kind,
                invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
                attacker_role="counterparty supplying calldata",
                note="Counterparty route reaches a refund/withdraw value path.",
                confidence=h.confidence, evidence_lines=[f"line {h.sink_line}"]))
        if hash_hints and not route_is_hashed:
            out.append(TaintFinding(
                detector=CALLDATA_NOT_IN_HASH_BUT_IN_VALUE_SINK, function=h.function,
                source_expr=h.source_expr, source_kind=h.source_kind,
                sink_expr=h.sink_expr, sink_kind=M.SINK_EXTERNAL_CALL,
                invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
                attacker_role="counterparty supplying calldata",
                missing_binding="value-affecting calldata is not bound into the consent/terms hash",
                note="A hash exists in this contract but does not bind the route field.",
                confidence=M.MEDIUM, evidence_lines=[f"line {h.sink_line}"]))

    for h in hash_hints:
        out.append(TaintFinding(
            detector=CALLDATA_TO_HASH_INPUT, function=h.function,
            source_expr=h.source_expr, source_kind=h.source_kind,
            sink_expr=h.sink_expr, sink_kind=h.sink_kind,
            attacker_role="signer/counterparty", confidence=h.confidence,
            evidence_lines=[f"line {h.sink_line}"]))

    for h in transfer_hints:
        out.append(TaintFinding(
            detector=CALLDATA_TO_TRANSFER_AMOUNT, function=h.function,
            source_expr=h.source_expr, source_kind=h.source_kind,
            sink_expr=h.sink_expr, sink_kind=h.sink_kind,
            attacker_role="caller", confidence=h.confidence,
            evidence_lines=[f"line {h.sink_line}"]))
    return out


def _body_findings(smap, emap):
    """Findings derived from function bodies (oracle/credit/mint/status shapes)."""
    out = []
    bodies = _bodies(smap)
    etypes = emap.types() if emap is not None else set()
    for c in smap.contracts:
        if c.kind == M.KIND_INTERFACE:
            continue
        for fn in c.functions:
            qn = fn.qualified_name
            body = _body_text(bodies, qn)
            if not body:
                continue
            low = body.lower()
            ev = _evidence(smap, qn)

            # Oracle return -> borrow/value limit.
            if _ORACLE_READ.search(low) and re.search(r"return\b|<=\s*max|>=\s*min|borrow", low) \
                    and re.search(r"price\s*\)*\s*[*/]|[*/]\s*1e\d|1e18|1e8", body):
                out.append(TaintFinding(
                    detector=ORACLE_RETURN_TO_BORROW_LIMIT, function=qn,
                    source_expr="oracle.latestRoundData()/price", source_kind=M.SRC_RETURN,
                    sink_expr="borrow limit / collateral value", sink_kind=M.SINK_STATE_WRITE,
                    invariant_family="ORACLE_DECIMAL_NORMALIZATION", attacker_role="borrower",
                    note="Oracle price feeds a borrow/value limit; check decimal normalization.",
                    evidence_lines=ev))

            # transferFrom-in then credit the nominal amount (no measured delta).
            tf = low.find("transferfrom")
            credit_m = re.search(r"\b(credit|credited|shares?|deposited|claimable|claim|owed|minted)\s*\[",
                                 body, re.I)
            if tf != -1 and credit_m and credit_m.start() > tf and "balanceof" not in low:
                out.append(TaintFinding(
                    detector=CREDIT_WRITE_FROM_NOMINAL_AMOUNT, function=qn,
                    source_expr="transferFrom amount (nominal)", source_kind=M.SRC_CALLDATA,
                    sink_expr=credit_m.group(0), sink_kind=M.SINK_STATE_WRITE,
                    invariant_family="SWAP_ACTUAL_RECEIVED_VS_CREDITED", attacker_role="depositor",
                    note="Credit ledger written from the nominal amount, not a measured balance delta.",
                    evidence_lines=ev))

            # External swap/adapter return value credited directly.
            m = re.search(r"(\w+)\s*=\s*\w+\.(swap|exactoutput|exactinput|exchange|convert|zap)\s*\(",
                          body, re.I)
            if m and re.search(r"(credit|shares?|deposited|claim)\s*\[[^\]]*\]\s*[+]?=\s*[^;]*\b"
                               + re.escape(m.group(1)) + r"\b", body, re.I):
                out.append(TaintFinding(
                    detector=ADAPTER_RETURN_TO_CREDIT, function=qn,
                    source_expr=f"{m.group(2)}() return", source_kind=M.SRC_RETURN,
                    sink_expr="credit ledger", sink_kind=M.SINK_STATE_WRITE,
                    invariant_family="SWAP_ACTUAL_RECEIVED_VS_CREDITED", attacker_role="depositor",
                    note="Adapter/swap return credited without measuring the received delta.",
                    evidence_lines=ev))

            # Mint against a message id with no consume guard.
            mints = bool(re.search(r"\.\s*mint\s*\(", body)) or "mint" in {t.lower() for t in fn.transfers}
            msgid = any("bytes32" in (p.type or "").lower() for p in fn.parameters) or \
                any(re.search(r"msg.?id|message|nonce", p.name or "", re.I) for p in fn.parameters)
            bridge_ctx = "CrossChainSupply" in etypes
            if mints and (msgid or bridge_ctx) and not _CONSUME_GUARD.search(low):
                out.append(TaintFinding(
                    detector=MESSAGE_ID_TO_MINT_WITHOUT_CONSUME, function=qn,
                    source_expr="message id (calldata)", source_kind=M.SRC_CALLDATA,
                    sink_expr="token.mint", sink_kind=M.SINK_EXTERNAL_CALL,
                    invariant_family="CROSS_CHAIN_SUPPLY_CONSERVATION",
                    attacker_role="cross-chain message sender",
                    missing_binding="no processed/consumed guard marks the message id",
                    note="The same message id can be replayed to mint again.", evidence_lines=ev))

            # Caller-controlled receiver of collateral/escrowed value.
            if re.search(r"collateral", low) and re.search(
                    r"(owner|receiver|to)\s*=\s*msg\.sender|transfer\s*\(\s*(receiver|to)\b", body, re.I):
                out.append(TaintFinding(
                    detector=MSG_SENDER_TO_COLLATERAL_OWNER, function=qn,
                    source_expr="msg.sender / caller-controlled receiver", source_kind=M.SRC_MSG_SENDER,
                    sink_expr="collateral owner / receiver", sink_kind=M.SINK_STATE_WRITE,
                    invariant_family="COLLATERAL_STATUS_RELEASE", attacker_role="caller",
                    note="Collateral owner/receiver is caller-controlled; verify authorization.",
                    evidence_lines=ev))

    # Status/flag write after an untrusted external call (CEI / reentrancy).
    for x in smap.external_calls:
        if not x.reentrancy_relevant:
            continue
        body = _body_text(bodies, x.function)
        if body and _STATUS_WRITE.search(body):
            out.append(TaintFinding(
                detector=STATUS_WRITE_AFTER_EXTERNAL_CALL, function=x.function,
                source_expr=x.selector or "external call", source_kind=M.SRC_RETURN,
                sink_expr="status/flag write (post-call)", sink_kind=M.SINK_STATE_WRITE,
                invariant_family="DEPOSIT_CONSUMPTION", attacker_role="reentrant caller",
                note="A status/consumed flag is written after an external call (CEI risk).",
                evidence_lines=[f"line {x.line}"]))
    return out


def build_taint_findings(smap, emap=None) -> list:
    """All named taint findings for a semantic map. Deduplicated, stable order."""
    findings = _calldata_findings(smap, smap.dataflow_hints) + _body_findings(smap, emap)
    seen, out = set(), []
    for f in findings:
        key = (f.detector, f.function, f.sink_expr)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    out.sort(key=lambda f: (f.function, f.detector))
    return out
