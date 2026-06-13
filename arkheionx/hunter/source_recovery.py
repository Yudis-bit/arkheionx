"""Source recovery engine for hunter mode.

Real bounty targets often have private, removed, or non-compiling repos, verified
explorer source only, ABI-only deployments, or one implementation shared by many
addresses. Hunter mode must not fall over in any of those cases — it recovers the
most authoritative source it can and records exactly how authoritative it is.

Recovery priority:
    local repo -> local artifacts -> provided source dir -> Sourcify exact ->
    Sourcify partial -> explorer verified -> ABI-only -> source missing.

Network recovery (Sourcify / explorer) is *opt-in* and goes through an injectable
``fetcher`` so tests never touch the network and default ``auto`` runs stay local.
When source is missing, source-level leads are capped (PARK_SOURCE) by the scorer.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import models as M

_ARTIFACT_DIRS = ("out", "artifacts", "build", "forge-out")
_SOL_DECL_RE = re.compile(r"\b(?:contract|library|interface)\s+([A-Za-z_][A-Za-z0-9_]*)")


def _index_local_sources(root: Path) -> dict:
    """Map contract name -> source path by scanning local .sol files (capped)."""
    index: dict[str, str] = {}
    count = 0
    for path in sorted(root.rglob("*.sol")):
        if count > 4000:
            break
        if any(part in ("node_modules", ".git", "lib", "__pycache__") for part in path.parts):
            continue
        try:
            if path.stat().st_size > 600_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        count += 1
        for m in _SOL_DECL_RE.finditer(text):
            index.setdefault(m.group(1), str(path))
        index.setdefault(path.stem, str(path))
    return index


def _has_artifacts(root: Path) -> str:
    for name in _ARTIFACT_DIRS:
        d = root / name
        if d.is_dir():
            try:
                if any(d.rglob("*.json")):
                    return str(d)
            except OSError:
                continue
    return ""


def _metadata_hash(*parts: str) -> str:
    blob = "|".join(p for p in parts if p).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()[:32] if blob else ""


def _record_for_name(name: str, address: str, chain_id: str, local_index: dict,
                     provided_index: dict, artifacts_dir: str) -> M.SourceRecord:
    """Resolve the most authoritative *local* source for one contract/address."""
    if name and name in local_index:
        path = local_index[name]
        return M.SourceRecord(
            address=address, chain_id=chain_id, contract_name=name,
            source_origin=M.SOURCE_LOCAL, match_type="local_repo", file_count=1,
            source_path=path, metadata_hash=_metadata_hash(name, path),
            deduped_source_set_id=_metadata_hash(name),
        )
    if name and name in provided_index:
        path = provided_index[name]
        return M.SourceRecord(
            address=address, chain_id=chain_id, contract_name=name,
            source_origin=M.SOURCE_PROVIDED, match_type="provided_source_dir", file_count=1,
            source_path=path, metadata_hash=_metadata_hash(name, path),
            deduped_source_set_id=_metadata_hash(name),
        )
    if artifacts_dir:
        return M.SourceRecord(
            address=address, chain_id=chain_id, contract_name=name,
            source_origin=M.SOURCE_ARTIFACT, match_type="local_artifact", file_count=1,
            source_path=artifacts_dir, metadata_hash=_metadata_hash(name, artifacts_dir),
            deduped_source_set_id=_metadata_hash(name or artifacts_dir),
            limitations=["Recovered from build artifacts, not original source files."],
        )
    return M.SourceRecord(
        address=address, chain_id=chain_id, contract_name=name,
        source_origin=M.SOURCE_MISSING, match_type="",
        limitations=["No local, provided, or artifact source found for this contract."],
    )


_FETCH_ORIGIN = {
    "sourcify_exact": M.SOURCE_SOURCIFY_EXACT,
    "sourcify_partial": M.SOURCE_SOURCIFY_PARTIAL,
    "etherscan": M.SOURCE_ETHERSCAN_VERIFIED,
    "explorer": M.SOURCE_ETHERSCAN_VERIFIED,
    "abi": M.SOURCE_ABI_ONLY,
}


def _apply_fetched(record: M.SourceRecord, fetched: dict) -> M.SourceRecord:
    origin = _FETCH_ORIGIN.get(str(fetched.get("origin", "")).lower(), M.SOURCE_RECOVERY_FAILED)
    record.source_origin = origin
    record.match_type = str(fetched.get("match_type", fetched.get("origin", "")))
    record.compiler_version = str(fetched.get("compiler_version", ""))
    record.file_count = int(fetched.get("file_count", 0) or 0)
    record.source_path = str(fetched.get("source_path", ""))
    record.metadata_hash = str(fetched.get("metadata_hash", "")) or _metadata_hash(
        record.contract_name, record.address, origin)
    record.deduped_source_set_id = str(fetched.get("deduped_source_set_id", "")) or record.metadata_hash
    if origin == M.SOURCE_ABI_ONLY:
        record.limitations.append("ABI-only: no Solidity source; behavior must be inferred from ABI + bytecode.")
    elif origin == M.SOURCE_SOURCIFY_PARTIAL:
        record.limitations.append("Sourcify partial match: metadata hash differs; treat source as approximate.")
    return record


def _rank(origin: str) -> int:
    order = [
        M.SOURCE_MISSING, M.SOURCE_RECOVERY_FAILED, M.SOURCE_ABI_ONLY,
        M.SOURCE_SOURCIFY_PARTIAL, M.SOURCE_ETHERSCAN_VERIFIED, M.SOURCE_SOURCIFY_EXACT,
        M.SOURCE_ARTIFACT, M.SOURCE_PROVIDED, M.SOURCE_LOCAL,
    ]
    return order.index(origin) if origin in order else 0


def recover_sources(
    ctx: M.HunterContext,
    root: Path,
    address_parse: M.AddressParseResult,
    contract_names: list,
    *,
    fetcher=None,
) -> M.SourceProvenance:
    """Recover source provenance for the in-scope contracts / deployed addresses.

    ``fetcher(address, chain_id, contract_name) -> dict | None`` is an optional,
    injectable network recovery hook. It is only consulted when local recovery fails
    and ``source_recovery_mode`` permits network recovery (``auto`` consults it only
    if a fetcher is actually injected; ``none`` never does).
    """
    mode = (ctx.source_recovery_mode or "auto").lower()
    local_index = _index_local_sources(root)
    provided_index: dict = {}
    if ctx.source_dir:
        provided_index = _index_local_sources(Path(ctx.source_dir).expanduser())
    artifacts_dir = _has_artifacts(root)
    network_allowed = mode in ("auto", "sourcify", "etherscan") and fetcher is not None
    attempted_network = False

    records: list = []
    address_dicts = list(address_parse.addresses or [])

    targets: list = []
    if address_dicts:
        for a in address_dicts:
            targets.append((a.get("name", ""), a.get("address", ""), a.get("chain_id", "")))
    else:
        for name in (contract_names or []):
            targets.append((name, "", ""))

    if not targets:
        # No addresses and no contracts: judge purely on local repo presence.
        overall = M.SOURCE_LOCAL if local_index else (
            M.SOURCE_PROVIDED if provided_index else (
                M.SOURCE_ARTIFACT if artifacts_dir else M.SOURCE_MISSING))
        notes = ["No addresses or contract names to resolve; judged on local repo presence."]
        return M.SourceProvenance(overall_status=overall, records=[], recovery_mode=mode,
                                  network_recovery_attempted=False, notes=notes)

    for name, address, chain_id in targets:
        rec = _record_for_name(name, address, chain_id, local_index, provided_index, artifacts_dir)
        if rec.source_origin == M.SOURCE_MISSING and network_allowed and address:
            attempted_network = True
            try:
                fetched = fetcher(address, chain_id, name)
            except Exception:  # a recovery hook must never crash the run
                fetched = None
            if isinstance(fetched, dict) and fetched:
                rec = _apply_fetched(rec, fetched)
            else:
                rec.source_origin = M.SOURCE_RECOVERY_FAILED
                rec.limitations.append("Network source recovery returned nothing.")
        records.append(rec)

    best = max((r.source_origin for r in records), key=_rank) if records else M.SOURCE_MISSING
    notes = [f"Recovery mode: {mode}.",
             f"Local source files indexed: {len(local_index)}." if local_index else "No local .sol source found."]
    if network_allowed:
        notes.append("Network recovery hook available (read-only verified-source fetch).")
    elif mode == "none":
        notes.append("Network recovery disabled (--no-source-recovery / mode none).")
    if any(r.source_origin in M.SOURCE_INADEQUATE for r in records):
        notes.append("Some contracts have inadequate source (ABI-only / missing); source-level leads are capped.")
    return M.SourceProvenance(overall_status=best, records=[r.to_dict() for r in records],
                              recovery_mode=mode, network_recovery_attempted=attempted_network,
                              notes=notes)


def source_status_for_contract(provenance: M.SourceProvenance, contract: str) -> str:
    """Best source status for a given contract name (used by the lead builder)."""
    statuses = [r["source_origin"] for r in provenance.records
                if r.get("contract_name", "").lower() == (contract or "").lower()]
    if statuses:
        return max(statuses, key=_rank)
    return provenance.overall_status
