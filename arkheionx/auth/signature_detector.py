"""Authorization engine orchestration and candidate derivation."""
from __future__ import annotations

from pathlib import Path

from arkheionx.ingest import discover_solidity

from . import models as M
from .delegatecall_analyzer import analyze_delegatecall
from .factory_init_analyzer import analyze_factories
from .operation_hash import analyze_operation
from .replay_analyzer import analyze_replay
from .threshold_analyzer import analyze_threshold

_SIGNALS = (
    "ecrecover",
    "ecdsa",
    "signaturechecker",
    "signer",
    "owner",
    "threshold",
    "nonce",
    "sequence",
    "execute",
    "operationhash",
    "transactionhash",
    "multisig",
    "wallet",
    "recovery",
    "delegatecall",
    "factory",
    "create2",
    "initializer",
)

_SIGNED_OPERATION_CONTEXT_SIGNALS = {
    "ecrecover",
    "ecdsa",
    "signaturechecker",
    "signer",
    "threshold",
    "nonce",
    "sequence",
    "execute",
    "operationhash",
    "transactionhash",
    "multisig",
    "wallet",
}


def _source_text(smap) -> str:
    if hasattr(smap, "_source_text"):
        return getattr(smap, "_source_text")
    discovery = discover_solidity(smap.root, include_tests=True, include_scripts=True)
    return "\n".join(source.text for source in discovery.sources)


def _candidate(family, operation, title, severity, evidence, *, key_reuse=False):
    return M.AuthCandidate(
        family=family,
        contract=operation.contract,
        function=operation.function,
        title=title,
        severity_hint=severity,
        requires_key_reuse=key_reuse,
        evidence=list(evidence),
        confidence="HIGH",
    )


def analyze_authorization(smap) -> M.AuthorizationAnalysis:
    source_text = _source_text(smap)
    lowered = source_text.lower()
    signals = [signal for signal in _SIGNALS if signal in lowered]
    analysis = M.AuthorizationAnalysis(active=bool(signals), activation_signals=signals)
    if not analysis.active:
        return analysis

    parse = getattr(smap, "_parse", None)
    bodies = getattr(parse, "bodies", {}) if parse is not None else {}
    for qualified, function_body in bodies.items():
        body = function_body.body
        lowered_body = body.lower()
        if "ecrecover" not in lowered_body and "signaturechecker" not in lowered_body:
            continue
        operation = analyze_operation(function_body.contract, function_body.name, body)
        if operation is None:
            continue
        analysis.signed_operations.append(operation)

        threshold = analyze_threshold(
            operation.contract,
            operation.function,
            body,
            source_text,
        )
        if threshold:
            analysis.threshold_analyses.append(threshold)
            if threshold.verdict == "DUPLICATE_SIGNER_THRESHOLD_BYPASS":
                analysis.candidates.append(_candidate(
                    "THRESHOLD_AUTHORIZATION_BYPASS",
                    operation,
                    "Duplicate signer can satisfy the authorization threshold",
                    "SUBMIT_CRITICAL_CANDIDATE",
                    threshold.evidence,
                ))

        replay = analyze_replay(operation, body)
        analysis.replay_analyses.append(replay)
        if replay.verdict == "NONCE_SEQUENCE_REPLAY":
            analysis.candidates.append(_candidate(
                "NONCE_SEQUENCE_REPLAY",
                operation,
                "Signed operation can be replayed in the same authorization domain",
                "SUBMIT_HIGH_CANDIDATE",
                replay.evidence,
            ))
        elif replay.verdict == "KEY_REUSE_REPLAY":
            analysis.candidates.append(_candidate(
                "KEY_REUSE_REPLAY",
                operation,
                "Signed operation lacks complete replay-domain binding",
                "HUMAN_REVIEW_REQUIRED",
                replay.evidence,
                key_reuse=True,
            ))

        delegate = analyze_delegatecall(operation, body)
        if delegate:
            analysis.delegatecall_analyses.append(delegate)
            if delegate.storage_control_risk:
                analysis.candidates.append(_candidate(
                    "DELEGATECALL_STORAGE_CONTROL",
                    operation,
                    "Delegated execution control is not fully signed",
                    "SUBMIT_CRITICAL_CANDIDATE",
                    delegate.evidence,
                ))

        dangerous_fields = [
            name for name, field in operation.binding_matrix.fields.items()
            if field.verdict in (
                M.UNBOUND_CRITICAL,
                M.UNBOUND_VALUE_FIELD,
                M.UNBOUND_CONTROL_FIELD,
            )
            and name not in ("chain_id", "wallet_address", "nonce_or_sequence", "operation_type")
        ]
        if dangerous_fields:
            analysis.candidates.append(_candidate(
                "SIGNATURE_OPERATION_BINDING",
                operation,
                "Executed operation fields are not bound by the signature",
                "SUBMIT_CRITICAL_CANDIDATE" if "destination" in dangerous_fields else "SUBMIT_HIGH_CANDIDATE",
                operation.evidence + ["unbound fields: " + ", ".join(dangerous_fields)],
            ))

    factories = analyze_factories(source_text, [contract.name for contract in smap.contracts])
    analysis.factory_init_analyses.extend(factories)
    for factory in factories:
        if factory.takeover_risk:
            operation = M.SignedOperation(contract=factory.contract, function=factory.function)
            analysis.candidates.append(_candidate(
                "FACTORY_INITIALIZATION_TAKEOVER",
                operation,
                "Externally callable initialization permits ownership takeover",
                "SUBMIT_HIGH_CANDIDATE",
                factory.evidence,
            ))

    unique = {}
    for candidate in analysis.candidates:
        key = (candidate.family, candidate.contract, candidate.function)
        unique.setdefault(key, candidate)
    analysis.candidates = list(unique.values())
    signed_context_signal_count = len(
        set(analysis.activation_signals) & _SIGNED_OPERATION_CONTEXT_SIGNALS
    )
    if analysis.activation_signals and not analysis.signed_operations \
            and signed_context_signal_count >= 2:
        analysis.warnings.append(
            "AUTH_KEYWORDS_ONLY_NO_SIGNED_OPERATION: authorization keywords were present but no signed operation was detected."
        )
    return analysis
