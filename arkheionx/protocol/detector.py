"""Analysis orchestrator: one pipeline reused by open/map/flow/hunt.

Tags every contract/function with a source kind, hides structural noise
(interfaces, libraries, tests, invariants, mocks, archives, generated, scripts)
by default, assigns fully-qualified target identities, and builds the
money-flow graph and hunter ranking from the visible production surface only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from arkheionx.flow.builder import build_money_flow
from arkheionx.flow.model import MoneyFlow
from arkheionx.hunt.model import HunterTarget, ValueHotspot
from arkheionx.hunt.ranker import rank_hotspots, rank_targets

from . import foundry as foundry_mod
from .foundry import FoundryStatus
from .model import (
    COMPILER_CONFIRMED,
    HEURISTIC,
    ContractRole,
    FunctionRole,
    ProtocolSnapshot,
    UserJourney,
)
from .roles import classify_contract, classify_function
from .semantic_adapter import load_semantic
from .source_kind import (
    SOFT_HIDDEN,
    STRUCTURAL_HIDDEN,
    contract_source_kind,
    file_source_kind,
    function_source_kind,
    hidden_category,
)
from .user_journey import detect_journeys


@dataclass
class Analysis:
    root: str
    snapshot: ProtocolSnapshot
    contracts: list[ContractRole] = field(default_factory=list)
    functions: list[FunctionRole] = field(default_factory=list)
    all_contracts: list[ContractRole] = field(default_factory=list)
    all_functions: list[FunctionRole] = field(default_factory=list)
    journeys: list[UserJourney] = field(default_factory=list)
    money_flow: MoneyFlow = field(default_factory=MoneyFlow)
    hotspots: list[ValueHotspot] = field(default_factory=list)
    hunter_targets: list[HunterTarget] = field(default_factory=list)
    foundry: FoundryStatus = field(default_factory=FoundryStatus)
    hidden_counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    build_output: str = ""


_PROTOCOL_SIGNATURES = (
    ("vault", ("deposit", "withdraw", "redeem"), ("totalassets", "shares", "assets")),
    ("staking", ("stake", "unstake"), ("staked", "rewardpertoken")),
    ("rewards", ("claim", "claimreward", "earned"), ("reward", "accumulator")),
    ("amm", ("swap", "addliquidity", "removeliquidity"), ("reserve", "klast", "liquidity")),
    ("lending", ("borrow", "repay", "liquidate"), ("collateral", "debt", "borrowindex")),
)


def _ids(file_path: str, contract: str, fr: FunctionRole) -> None:
    fr.file_path = file_path
    fr.display_id = f"{contract}.{fr.function_name}"
    sig = fr.signature or f"{fr.function_name}()"
    fr.qualified_id = f"{file_path}:{contract}.{sig}" if file_path else f"{contract}.{sig}"
    start, end = (fr.line_range + [0, 0])[:2]
    fr.stable_id = f"{fr.qualified_id}#L{start}-L{end}"


def _detect_protocol_types(function_roles: list[FunctionRole], contracts: list[dict]) -> list[str]:
    fnames = {fr.function_name.lower() for fr in function_roles}
    state = " ".join(v.lower() for c in contracts for v in c.get("state_variables", []))
    found: list[str] = []
    for label, fn_terms, state_terms in _PROTOCOL_SIGNATURES:
        if any(t in name for name in fnames for t in fn_terms) or any(t in state for t in state_terms):
            found.append(label)
    if any(fr.oracle_calls for fr in function_roles):
        found.append("oracle")
    return found or ["generic"]


def _summary(types: list[str], contracts: list[ContractRole], flow: MoneyFlow) -> str:
    holders = ", ".join(flow.value_holders[:3]) or "no clear value holder detected"
    return (
        f"{'/'.join(types)} protocol across {len(contracts)} active contract(s). "
        f"Value held in: {holders}. "
        f"{len(flow.entrypoints)} money entrypoint(s), {len(flow.exits)} exit(s)."
    )


def analyze(
    root: Path,
    *,
    from_report: Path | None = None,
    use_foundry: bool = False,
    run_build: bool = False,
    show_all: bool = False,
    top: int = 10,
) -> Analysis:
    semantic = load_semantic(root, from_report=from_report)
    contracts_raw = semantic.get("contracts", [])
    warnings = list(semantic.get("warnings", []))

    foundry_status = FoundryStatus()
    build_output = ""
    evidence_level = HEURISTIC
    if run_build:
        foundry_status, build_output = foundry_mod.build_and_confirm(root)
    else:
        foundry_status = foundry_mod.detect_foundry(root)
    if foundry_status.status == foundry_mod.BUILD_PASSED:
        evidence_level = COMPILER_CONFIRMED

    # 1) Classify source kinds.
    production_exists = False
    enriched: list[dict] = []
    for contract in contracts_raw:
        fkind = file_source_kind(str(contract.get("file", "")))
        ckind = contract_source_kind(contract, fkind)
        if ckind == "production":
            production_exists = True
        enriched.append({"contract": contract, "kind": ckind})

    # 2) Build role objects, tag kinds + identities, and partition active/hidden.
    all_contracts: list[ContractRole] = []
    all_functions: list[FunctionRole] = []
    active_contracts: list[ContractRole] = []
    visible_functions: list[FunctionRole] = []
    compiled = set(foundry_status.compiled_contracts)
    hidden_counts: dict[str, int] = {}

    for item in enriched:
        contract = item["contract"]
        ckind = item["kind"]
        cname = str(contract.get("name", ""))
        cfile = str(contract.get("file", ""))
        is_active = show_all or ckind == "production" or (ckind in SOFT_HIDDEN and not production_exists)

        fns: list[FunctionRole] = []
        for fn in contract.get("functions", []):
            fkind = function_source_kind(fn, ckind)
            fr = classify_function(fn, cname)
            fr.source_kind = fkind
            _ids(cfile, cname, fr)
            if evidence_level == COMPILER_CONFIRMED and cname in compiled:
                fr.evidence_level = COMPILER_CONFIRMED
            fns.append(fr)
            all_functions.append(fr)

        cr = classify_contract(contract, fns)
        cr.source_kind = ckind
        if evidence_level == COMPILER_CONFIRMED and cname in compiled:
            cr.evidence_level = COMPILER_CONFIRMED
        all_contracts.append(cr)

        if is_active:
            active_contracts.append(cr)
            for fr in fns:
                if show_all or fr.source_kind not in (STRUCTURAL_HIDDEN | {"test", "invariant"}):
                    visible_functions.append(fr)
        else:
            cat = hidden_category(ckind)
            hidden_counts[cat] = hidden_counts.get(cat, 0) + 1

    # Count test/invariant helper functions inside active contracts as hidden.
    hidden_fn = sum(1 for fr in all_functions if fr.source_kind in {"test", "invariant"})
    if hidden_fn:
        hidden_counts["tests_invariants"] = hidden_counts.get("tests_invariants", 0) + hidden_fn

    journeys = detect_journeys(visible_functions)
    flow = build_money_flow(active_contracts, visible_functions, evidence_level)
    hotspots = rank_hotspots(visible_functions, evidence_level)
    targets = rank_targets(visible_functions, evidence_level, top=top)
    protocol_types = _detect_protocol_types(visible_functions, [i["contract"] for i in enriched if i["kind"] == "production" or (i["kind"] in SOFT_HIDDEN and not production_exists)])

    limitations = ["Static heuristic analysis. Roles and edges are candidates, not proven behavior."]
    fstatus = foundry_status.status
    if fstatus == foundry_mod.BUILD_FAILED:
        limitations.append("forge build failed; results remain heuristic. See build output artifact.")
    elif evidence_level == HEURISTIC:
        limitations.append("No compiler confirmation: run with --build inside a Foundry project.")
    if not active_contracts:
        limitations.append("No production contracts detected at this path.")

    snapshot = ProtocolSnapshot(
        root=str(root),
        protocol_types=protocol_types,
        foundry_status=fstatus,
        contracts_analyzed=len(active_contracts),
        functions_analyzed=len(visible_functions),
        evidence_level=evidence_level,
        summary=_summary(protocol_types, active_contracts, flow),
        limitations=limitations,
    )

    return Analysis(
        root=str(root),
        snapshot=snapshot,
        contracts=active_contracts,
        functions=visible_functions,
        all_contracts=all_contracts,
        all_functions=all_functions,
        journeys=journeys,
        money_flow=flow,
        hotspots=hotspots,
        hunter_targets=targets,
        foundry=foundry_status,
        hidden_counts=hidden_counts,
        warnings=warnings,
        build_output=build_output,
    )
