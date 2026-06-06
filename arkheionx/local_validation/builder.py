"""Local validation builder (v3.7, additive, internal-only).

Consumes a ``ParsedFoundryOutput`` (Agent 3) and builds deterministic
``LocalValidationRun`` / ``LocalTestResult`` records, optional explicit
``LocalTraceReceipt`` placeholders, and a ``LocalValidationSummary``, minting IDs
via ``arkheionx.local_validation.ids``. It can link test results to a Protocol
Intelligence Model by exact match only (function_id, selector, exact signature,
exact contract+function, or an explicit alias); ambiguous or unresolved matches
become warnings and never a fabricated link.

This module is a pure transform: it reads no files, writes nothing, runs no
subprocess, calls no ``forge``, requires no Foundry install, and performs no RPC
or network access. It mints no timestamps, mutates neither the parsed input nor
the protocol model, makes no confirmed-vulnerability / final-severity /
audit-passed / bounty claim, and never emits a human-reviewed status. A passing
local test supports only ``SUPPORT_TESTED``; failing/skipped/errored/unknown
tests stay ``SUPPORT_NONE``; ``manual_review_required`` stays true and
``ready_for_submission`` stays false.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from . import ids
from .model import (
    SUPPORT_NONE,
    SUPPORT_TESTED,
    SUPPORT_TRACE_BOUND,
    TEST_ERROR,
    TEST_FAILED,
    TEST_PASSED,
    TEST_SKIPPED,
    TEST_UNKNOWN,
    TRACE_AVAILABLE,
    TRACE_PARTIAL,
    LocalTestResult,
    LocalTraceReceipt,
    LocalValidationRun,
    LocalValidationSummary,
    local_validation_status_from_counts,
    to_dict,
)
from .parser import ParsedFoundryOutput

_DEFAULT_COMMAND = ["forge", "test", "--json"]


@dataclass
class LocalValidationBuildResult:
    run: LocalValidationRun
    test_results: list[LocalTestResult] = field(default_factory=list)
    trace_receipts: list[LocalTraceReceipt] = field(default_factory=list)
    summary: LocalValidationSummary | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


# --- run + test results ------------------------------------------------------

def build_local_validation_run(
    parsed: ParsedFoundryOutput, *, repo_fingerprint: str, command: list[str]
) -> LocalValidationRun:
    tool = parsed.tool or "foundry"
    run_id = ids.local_validation_run_id(tool, repo_fingerprint, command)
    return LocalValidationRun(
        run_id=run_id,
        tool=tool,
        repo_fingerprint=repo_fingerprint,
        command=list(command),
        warnings=list(parsed.warnings),
        metadata={"source_format": parsed.source_format},
    )


def _support_for(status: str) -> str:
    return SUPPORT_TESTED if status == TEST_PASSED else SUPPORT_NONE


def assign_test_result_ids(
    test_results: list[LocalTestResult], *, tool: str, run_id: str
) -> tuple[list[LocalTestResult], list[str]]:
    """Return deep-copied results with run_id, deterministic ids, and support set.

    The parsed source list is never mutated. Duplicate (tool, test_name, run_id)
    ids are disambiguated deterministically by contract name and occurrence index
    and a warning is recorded.
    """

    out: list[LocalTestResult] = []
    warnings: list[str] = []
    seen: dict[str, int] = {}
    for source in test_results:
        result = copy.deepcopy(source)
        result.run_id = run_id
        result.tool = tool
        base_id = ids.local_test_result_id(tool, result.test_name, run_id)
        occurrence = seen.get(base_id, 0)
        if occurrence:
            seed = f"{result.test_name}#{result.contract_name}#{occurrence}"
            result.test_result_id = ids.local_test_result_id(tool, seed, run_id)
            warnings.append(f"duplicate test name disambiguated: {result.test_name}")
        else:
            result.test_result_id = base_id
        seen[base_id] = occurrence + 1
        result.evidence_support = _support_for(result.status)
        out.append(result)
    return out, warnings


# --- protocol model linking (exact only) -------------------------------------

def _model_dict(protocol_model: object | None) -> dict | None:
    if protocol_model is None:
        return None
    if isinstance(protocol_model, dict):
        return protocol_model
    if hasattr(protocol_model, "to_dict"):
        data = protocol_model.to_dict()
        return data if isinstance(data, dict) else None
    return None


def _function_display_parts(function: dict, contract_names: dict[str, str]) -> tuple[str, str]:
    contract = contract_names.get(str(function.get("contract_id", "")), "")
    display = str(function.get("display_name", "") or "")
    if "." in display:
        d_contract, d_function = display.rsplit(".", 1)
        contract = contract or d_contract
        return contract, d_function
    signature = str(function.get("signature", "") or "")
    function_name = signature.split("(", 1)[0] if signature else display
    return contract, function_name


def extract_protocol_function_index(protocol_model: object | None) -> dict[str, object]:
    """Build exact-match lookup maps from a protocol model. Never mutates input."""

    index: dict[str, object] = {
        "by_function_id": set(), "by_selector": {}, "by_signature": {},
        "by_contract_function": {}, "by_alias": {}, "edges": {},
    }
    data = _model_dict(protocol_model)
    if data is None:
        return index

    contract_names: dict[str, str] = {}
    for contract in data.get("contracts", []) or []:
        if isinstance(contract, dict):
            name = str(contract.get("name", "") or (contract.get("aliases", {}) or {}).get("contract_name", ""))
            if contract.get("contract_id") and name:
                contract_names[str(contract["contract_id"])] = name

    def add(mapping: dict, key, fid: str) -> None:
        mapping.setdefault(key, [])
        if fid not in mapping[key]:
            mapping[key].append(fid)

    for function in data.get("functions", []) or []:
        if not isinstance(function, dict):
            continue
        fid = str(function.get("function_id", "") or "")
        if not fid:
            continue
        index["by_function_id"].add(fid)
        selector = str((function.get("metadata", {}) or {}).get("selector", "") or function.get("selector", "") or "")
        if selector:
            add(index["by_selector"], selector, fid)
        signature = str(function.get("signature", "") or "")
        if signature:
            add(index["by_signature"], signature, fid)
        contract, function_name = _function_display_parts(function, contract_names)
        if contract and function_name:
            add(index["by_contract_function"], (contract, function_name), fid)
        for alias in (function.get("aliases", {}) or {}).values():
            if isinstance(alias, str) and alias:
                add(index["by_alias"], alias, fid)

    edges: dict[str, dict[str, list[str]]] = {}

    def edge(fid: str) -> dict[str, list[str]]:
        return edges.setdefault(fid, {"value_path_ids": [], "assumption_ids": [], "test_gap_ids": []})

    for vp in data.get("value_paths", []) or []:
        if isinstance(vp, dict) and vp.get("value_path_id"):
            for fid in {str(vp.get("entry_function_id", "")), str(vp.get("exit_function_id", ""))} - {""}:
                edge(fid)["value_path_ids"].append(str(vp["value_path_id"]))
    for asm in data.get("assumptions", []) or []:
        if isinstance(asm, dict) and asm.get("assumption_id"):
            for fid in {str(f) for f in (asm.get("linked_function_ids", []) or [])} - {""}:
                edge(fid)["assumption_ids"].append(str(asm["assumption_id"]))
    for gap in data.get("test_gaps", []) or []:
        if isinstance(gap, dict) and gap.get("test_gap_id"):
            fid = str(gap.get("linked_function_id", "") or "")
            if fid:
                edge(fid)["test_gap_ids"].append(str(gap["test_gap_id"]))
    index["edges"] = edges
    return index


def _resolve_one(values: list[str]) -> tuple[str, bool]:
    """Return (function_id, ambiguous): a single hit, or ambiguity flag for >1."""

    distinct = list(dict.fromkeys(values))
    if len(distinct) == 1:
        return distinct[0], False
    return "", len(distinct) > 1


def link_test_result_to_protocol(
    test_result: LocalTestResult, protocol_index: dict[str, object]
) -> tuple[LocalTestResult, str]:
    """Return a copied result with exact links applied, plus an optional warning."""

    result = copy.deepcopy(test_result)
    meta_fid = str((result.metadata or {}).get("function_id", "") or "")
    candidates: list[list[str]] = []
    if meta_fid and meta_fid in protocol_index["by_function_id"]:
        candidates.append([meta_fid])
    if result.selector:
        candidates.append(protocol_index["by_selector"].get(result.selector, []))
    meta_sig = str((result.metadata or {}).get("signature", "") or "")
    if meta_sig:
        candidates.append(protocol_index["by_signature"].get(meta_sig, []))
    if result.contract_name and result.function_name:
        candidates.append(protocol_index["by_contract_function"].get((result.contract_name, result.function_name), []))
    alias_keys = [result.test_name]
    if result.contract_name and result.function_name:
        alias_keys.append(f"{result.contract_name}.{result.function_name}")
    for key in alias_keys:
        if key:
            candidates.append(protocol_index["by_alias"].get(key, []))

    for hits in candidates:
        if not hits:
            continue
        fid, ambiguous = _resolve_one(hits)
        if fid:
            result.linked_function_ids = [fid]
            edge = protocol_index["edges"].get(fid, {})
            result.linked_value_path_ids = list(edge.get("value_path_ids", []))
            result.linked_assumption_ids = list(edge.get("assumption_ids", []))
            result.linked_test_gap_ids = list(edge.get("test_gap_ids", []))
            return result, ""
        if ambiguous:
            return result, f"ambiguous protocol match for {result.test_name}; not linked"
    return result, f"unresolved protocol target for {result.test_name}; not linked"


def link_test_results_to_protocol(
    test_results: list[LocalTestResult], protocol_model: object | None
) -> tuple[list[LocalTestResult], list[str]]:
    if protocol_model is None:
        return [copy.deepcopy(t) for t in test_results], []
    index = extract_protocol_function_index(protocol_model)
    linked: list[LocalTestResult] = []
    warnings: list[str] = []
    for result in test_results:
        new_result, warning = link_test_result_to_protocol(result, index)
        linked.append(new_result)
        if warning:
            warnings.append(warning)
    return linked, warnings


# --- optional explicit trace receipts ----------------------------------------

def _build_trace_receipts(test_results: list[LocalTestResult], *, tool: str, run_id: str) -> list[LocalTraceReceipt]:
    receipts: list[LocalTraceReceipt] = []
    for result in test_results:
        trace = (result.metadata or {}).get("trace")
        if not isinstance(trace, dict) or not trace:
            continue
        status = TRACE_PARTIAL if trace.get("partial") else TRACE_AVAILABLE
        receipts.append(LocalTraceReceipt(
            trace_receipt_id=ids.local_trace_receipt_id(tool, result.test_result_id, trace),
            run_id=run_id,
            test_result_id=result.test_result_id,
            tool=tool,
            trace_kind=str(trace.get("kind", "") or ""),
            trace_status=status,
            linked_function_ids=list(result.linked_function_ids),
            call_count=int(trace.get("call_count", 0) or 0),
            external_call_count=int(trace.get("external_call_count", 0) or 0),
            value_transfer_count=int(trace.get("value_transfer_count", 0) or 0),
            delegatecall_count=int(trace.get("delegatecall_count", 0) or 0),
            staticcall_count=int(trace.get("staticcall_count", 0) or 0),
            events_count=int(trace.get("events_count", 0) or 0),
            evidence_support=SUPPORT_TRACE_BOUND,
        ))
    return receipts


# --- summary -----------------------------------------------------------------

def _count(results: list[LocalTestResult], status: str) -> int:
    return sum(1 for r in results if r.status == status)


def _unique_linked(results: list[LocalTestResult], attr: str) -> int:
    values: set[str] = set()
    for result in results:
        values.update(getattr(result, attr) or [])
    return len(values)


def build_local_validation_summary(
    run: LocalValidationRun,
    test_results: list[LocalTestResult],
    trace_receipts: list[LocalTraceReceipt] | None = None,
    *,
    warnings: list[str] | None = None,
) -> LocalValidationSummary:
    trace_receipts = trace_receipts or []
    passed = _count(test_results, TEST_PASSED)
    failed = _count(test_results, TEST_FAILED)
    skipped = _count(test_results, TEST_SKIPPED)
    errored = _count(test_results, TEST_ERROR)
    unknown = _count(test_results, TEST_UNKNOWN)
    test_result_ids = [t.test_result_id for t in test_results]
    return LocalValidationSummary(
        summary_id=ids.local_validation_summary_id(run.repo_fingerprint, run.tool, test_result_ids),
        repo_fingerprint=run.repo_fingerprint,
        tool=run.tool,
        run_ids=[run.run_id],
        test_result_ids=test_result_ids,
        trace_receipt_ids=[r.trace_receipt_id for r in trace_receipts],
        total_tests=len(test_results),
        passed_tests=passed,
        failed_tests=failed,
        skipped_tests=skipped,
        errored_tests=errored,
        unknown_tests=unknown,
        trace_receipts=len(trace_receipts),
        linked_function_count=_unique_linked(test_results, "linked_function_ids"),
        linked_value_path_count=_unique_linked(test_results, "linked_value_path_ids"),
        linked_assumption_count=_unique_linked(test_results, "linked_assumption_ids"),
        linked_test_gap_count=_unique_linked(test_results, "linked_test_gap_ids"),
        status=local_validation_status_from_counts(passed, failed, skipped, errored, unknown),
        warnings=list(warnings or []),
    )


# --- orchestration -----------------------------------------------------------

def build_local_validation_from_parsed(
    parsed: ParsedFoundryOutput,
    *,
    repo_fingerprint: str,
    command: list[str] | None = None,
    protocol_model: object | None = None,
) -> LocalValidationBuildResult:
    if not str(repo_fingerprint or "").strip():
        raise ValueError("repo_fingerprint is required for build_local_validation_from_parsed")
    command = list(command) if command else list(_DEFAULT_COMMAND)
    run = build_local_validation_run(parsed, repo_fingerprint=repo_fingerprint, command=command)

    results, id_warnings = assign_test_result_ids(parsed.test_results, tool=run.tool, run_id=run.run_id)
    results, link_warnings = link_test_results_to_protocol(results, protocol_model)
    trace_receipts = _build_trace_receipts(results, tool=run.tool, run_id=run.run_id)

    warnings = list(parsed.warnings) + id_warnings + link_warnings
    summary = build_local_validation_summary(run, results, trace_receipts, warnings=warnings)

    run.test_result_ids = [t.test_result_id for t in results]
    run.trace_receipt_ids = [r.trace_receipt_id for r in trace_receipts]
    run.artifact_ids = []
    run.status = summary.status
    return LocalValidationBuildResult(
        run=run,
        test_results=results,
        trace_receipts=trace_receipts,
        summary=summary,
        warnings=warnings,
        metadata={"source_format": parsed.source_format},
    )


def local_validation_build_result_to_dict(result: LocalValidationBuildResult) -> dict[str, object]:
    return to_dict(result)
