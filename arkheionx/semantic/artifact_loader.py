"""Safe artifact enrichment layered on top of fallback source parsing."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from arkheionx.ingest.artifact_discovery import ArtifactDiscovery, discover_artifacts
from arkheionx.ingest.solidity_discovery import SourceFile

from . import models as M


@dataclass
class ArtifactFacts:
    discovery: ArtifactDiscovery
    virtual_sources: list = field(default_factory=list)
    contracts: list = field(default_factory=list)
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


def load_artifacts(root: Path | str, build_artifacts: Path | str | None = None,
                   discovery: ArtifactDiscovery | None = None) -> ArtifactFacts:
    root = Path(root)
    discovery = discovery or discover_artifacts(root, build_artifacts)
    facts = ArtifactFacts(discovery=discovery, warnings=list(discovery.warnings))
    seen_sources: set[str] = set()
    seen_contracts: set[tuple[str, str]] = set()
    for record in discovery.records:
        data = record.data
        if record.style == "build_info":
            for source_name, source in data.get("input", {}).get("sources", {}).items():
                if not isinstance(source, dict) or not isinstance(source.get("content"), str):
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
                        key = (source_name, contract_name)
                        if key in seen_contracts:
                            continue
                        contract = _contract_from_artifact(contract_name, source_name, contract_data)
                        if contract:
                            facts.contracts.append(contract)
                            seen_contracts.add(key)
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
        contract_name = data.get("contractName") or Path(record.path).stem
        source_name = data.get("sourceName") or data.get("sourcePath") or ""
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
