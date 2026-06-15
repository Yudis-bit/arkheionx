"""Safe artifact enrichment layered on top of fallback source parsing."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from arkheionx.ingest.artifact_discovery import ArtifactDiscovery, discover_artifacts
from arkheionx.ingest.solidity_discovery import SourceFile

from . import models as M


@dataclass
class ArtifactFacts:
    discovery: ArtifactDiscovery
    virtual_sources: list = field(default_factory=list)
    contracts: list = field(default_factory=list)
    stale_artifacts_ignored: int = 0
    sample_artifacts_ignored: int = 0
    warnings: list = field(default_factory=list)

    @property
    def mode(self) -> str:
        return self.discovery.mode


def _abi_functions(contract_name: str, abi) -> list:
    functions = []
    if not isinstance(abi, list):
        return functions
    for item in abi:
        if not isinstance(item, dict) or item.get("type") != "function":
            continue
        params = [
            M.Parameter(
                name=value.get("name", ""),
                type=value.get("type", ""),
                location=value.get("internalType", ""),
            )
            for value in item.get("inputs", [])
            if isinstance(value, dict)
        ]
        returns = [
            M.Parameter(name=value.get("name", ""), type=value.get("type", ""))
            for value in item.get("outputs", [])
            if isinstance(value, dict)
        ]
        functions.append(M.FunctionSemantic(
            contract=contract_name,
            name=item.get("name", ""),
            visibility="external",
            mutability=item.get("stateMutability", ""),
            parameters=params,
            returns=returns,
            confidence=M.HIGH,
            warnings=["function signature enriched from compiler artifact"],
        ))
    return functions


def _contract_from_artifact(name: str, source_name: str, data: dict):
    if not name:
        return None
    contract = M.ContractSemantic(
        name=name,
        file=source_name,
        functions=_abi_functions(name, data.get("abi")),
        confidence=M.HIGH,
        warnings=["contract facts enriched from compiler artifact"],
    )
    layout = data.get("storageLayout", {})
    if isinstance(layout, dict):
        for slot in layout.get("storage", []) or []:
            if not isinstance(slot, dict) or not slot.get("label"):
                continue
            contract.state_variables.append(M.StateVariable(
                name=slot.get("label", ""),
                type=slot.get("type", ""),
                visibility="internal",
            ))
    return contract


_SAMPLE_ARTIFACT_CONTRACTS = {
    "Migrations",
    "MetaCoin",
    "ConvertLib",
    "SimpleStorage",
    "Greeter",
    "Storage",
}


def _source_name(data: dict) -> str:
    return str(data.get("sourceName") or data.get("sourcePath") or "").strip()


def _contract_name(path: str, data: dict) -> str:
    return str(data.get("contractName") or Path(path).stem or "").strip()


def _normalize_source_name(value: str) -> str:
    source = str(value or "").replace("\\", "/").strip()
    source = re.sub(r"^[A-Za-z0-9_.-]+:/+", "", source)
    while source.startswith("./"):
        source = source[2:]
    return source.strip("/")


def _source_exists(root: Path, source_name: str, source_rels: set[str]) -> bool:
    if not source_name:
        return False
    normalized = _normalize_source_name(source_name)
    if normalized in source_rels:
        return True
    raw = Path(source_name)
    if raw.is_absolute():
        try:
            rel = raw.resolve().relative_to(root.resolve()).as_posix()
        except (OSError, ValueError):
            return False
        return rel in source_rels or raw.is_file()
    candidate = root / normalized
    try:
        candidate.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    if candidate.is_file():
        return True
    return any(rel.endswith("/" + normalized) for rel in source_rels)


def _is_sample_artifact(contract_name: str, source_exists: bool) -> bool:
    if contract_name in _SAMPLE_ARTIFACT_CONTRACTS and not source_exists:
        return True
    return contract_name == "Token" and not source_exists


def _accept_artifact(record, root: Path, source_rels: set[str], facts: ArtifactFacts) -> bool:
    data = record.data
    contract_name = _contract_name(record.path, data)
    source_name = _source_name(data)
    source_exists = _source_exists(root, source_name, source_rels)
    sample = _is_sample_artifact(contract_name, source_exists)
    if sample:
        facts.sample_artifacts_ignored += 1
        facts.warnings.append(
            f"STALE_ARTIFACT_IGNORED: sample artifact ignored for {contract_name}"
        )
        return False
    if source_name and not source_exists:
        facts.stale_artifacts_ignored += 1
        facts.warnings.append(
            f"STALE_ARTIFACT_IGNORED: artifact source missing for {contract_name}"
        )
        return False
    return True


def load_artifacts(root: Path | str, build_artifacts: Path | str | None = None,
                   discovery: ArtifactDiscovery | None = None,
                   source_rels: set[str] | None = None) -> ArtifactFacts:
    root = Path(root)
    discovery = discovery or discover_artifacts(root, build_artifacts)
    facts = ArtifactFacts(discovery=discovery, warnings=list(discovery.warnings))
    source_rels = set(source_rels or set())
    seen_sources: set[str] = set()
    seen_contracts: set[tuple[str, str]] = set()
    for record in discovery.records:
        data = record.data
        if record.style == "build_info":
            for source_name, source in data.get("input", {}).get("sources", {}).items():
                if not isinstance(source, dict) or not isinstance(source.get("content"), str):
                    continue
                if not _source_exists(root, str(source_name), source_rels):
                    facts.stale_artifacts_ignored += 1
                    facts.warnings.append(
                        f"STALE_ARTIFACT_IGNORED: build-info source missing for {source_name}"
                    )
                    continue
                if source_name not in seen_sources:
                    facts.virtual_sources.append(SourceFile(
                        f"{record.path}:{source_name}",
                        source_name,
                        source["content"],
                    ))
                    seen_sources.add(source_name)
            contracts = data.get("output", {}).get("contracts", {})
            if isinstance(contracts, dict):
                for source_name, by_name in contracts.items():
                    if not isinstance(by_name, dict):
                        continue
                    for contract_name, contract_data in by_name.items():
                        if not isinstance(contract_data, dict):
                            continue
                        if not _source_exists(root, str(source_name), source_rels):
                            continue
                        if _is_sample_artifact(str(contract_name), True):
                            continue
                        key = (source_name, contract_name)
                        if key in seen_contracts:
                            continue
                        contract = _contract_from_artifact(contract_name, source_name, contract_data)
                        if contract:
                            facts.contracts.append(contract)
                            seen_contracts.add(key)
            continue
        if not _accept_artifact(record, root, source_rels, facts):
            continue
        if record.style == "legacy" and isinstance(data.get("source"), str):
            source_name = data.get("sourcePath") or Path(record.path).with_suffix(".sol").name
            if source_name not in seen_sources:
                facts.virtual_sources.append(SourceFile(
                    f"{record.path}:{source_name}",
                    source_name,
                    data["source"],
                ))
                seen_sources.add(source_name)
        contract_name = _contract_name(record.path, data)
        source_name = _source_name(data)
        key = (source_name, contract_name)
        if key not in seen_contracts:
            contract = _contract_from_artifact(contract_name, source_name, data)
            if contract:
                facts.contracts.append(contract)
                seen_contracts.add(key)
    return facts


def merge_contracts(parsed_contracts: list, artifact_contracts: list) -> list:
    by_name = {contract.name: contract for contract in parsed_contracts}
    for artifact_contract in artifact_contracts:
        current = by_name.get(artifact_contract.name)
        if current is None:
            parsed_contracts.append(artifact_contract)
            by_name[artifact_contract.name] = artifact_contract
            continue
        current.confidence = M.HIGH
        known_functions = {function.name for function in current.functions}
        current.functions.extend(
            function for function in artifact_contract.functions
            if function.name not in known_functions
        )
        known_storage = {value.name for value in current.state_variables}
        current.state_variables.extend(
            value for value in artifact_contract.state_variables
            if value.name not in known_storage
        )
        if "compiler artifact facts merged with fallback source" not in current.warnings:
            current.warnings.append("compiler artifact facts merged with fallback source")
    return parsed_contracts
