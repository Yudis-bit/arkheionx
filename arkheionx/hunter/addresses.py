"""Address Parser v2 for hunter mode.

Accepts the common ``addresses.json`` shapes seen across real bounty programs and
normalizes every entry to a single ``ContractAddress`` shape. It is strict about
failure so an address surface is never silently skipped:

- Missing file              -> ADDRESS_FILE_MISSING
- Empty file                -> ADDRESS_FILE_EMPTY
- Non-empty but unparseable -> ADDRESS_PARSE_ERROR (with the offending path)
- Non-empty, valid JSON, but zero usable addresses -> ADDRESS_PARSE_ERROR
- Explicit empty ``contracts: []`` -> ADDRESS_EMPTY_CONTRACTS (valid, no addresses)
- No file requested at all   -> ADDRESS_NONE_PROVIDED

Supported formats: flat map, contracts array, program+chain+contracts, environment
map, chains map, and list of objects. Everything is local/static; no network.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import models as M

_ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
# Well-known network names -> a conventional chain id (best-effort, generic only).
_NETWORK_CHAIN = {
    "mainnet": "1", "ethereum": "1", "eth": "1",
    "goerli": "5", "sepolia": "11155111", "holesky": "17000",
    "optimism": "10", "base": "8453", "arbitrum": "42161", "arbitrum-one": "42161",
    "polygon": "137", "bsc": "56", "avalanche": "43114", "gnosis": "100",
}


def is_address(value) -> bool:
    return isinstance(value, str) and bool(_ADDR_RE.match(value.strip()))


def _normalize_address(value: str) -> str:
    return value.strip().lower()


def _chain_for_network(network: str) -> str:
    return _NETWORK_CHAIN.get(network.strip().lower(), "")


def _network_for_chain(chain_id: str) -> str:
    for name, cid in _NETWORK_CHAIN.items():
        if cid == str(chain_id) and name in ("mainnet", "optimism", "base", "arbitrum", "polygon", "bsc", "gnosis", "avalanche", "sepolia"):
            return name
    return ""


def _make_entry(
    name,
    address,
    *,
    chain_id="",
    network="",
    category="",
    proxy_expected=None,
    expected_implementation=None,
    source_reference="",
    metadata=None,
    errors=None,
    path="",
) -> M.ContractAddress | None:
    """Build one normalized entry, recording an error for an invalid address."""
    addr = (address or "")
    if not is_address(addr):
        if errors is not None:
            errors.append({
                "path": path,
                "name": str(name)[:64],
                "value": str(address)[:80],
                "error": "invalid_address",
            })
        return None
    network = network or (_network_for_chain(chain_id) if chain_id else "")
    chain_id = str(chain_id or (_chain_for_network(network) if network else ""))
    return M.ContractAddress(
        name=str(name or "")[:64],
        address=_normalize_address(addr),
        chain_id=chain_id,
        network=network,
        category=str(category or ""),
        proxy_expected=proxy_expected,
        expected_implementation=(_normalize_address(expected_implementation)
                                 if is_address(expected_implementation) else
                                 (expected_implementation or None)),
        source_reference=str(source_reference or ""),
        metadata=dict(metadata or {}),
    )


def _entry_from_obj(obj: dict, *, chain_id="", network="", errors=None, path="") -> M.ContractAddress | None:
    return _make_entry(
        obj.get("name", obj.get("symbol", "contract")),
        obj.get("address"),
        chain_id=obj.get("chain_id", obj.get("chainId", chain_id)),
        network=obj.get("network", network),
        category=obj.get("category", obj.get("kind", "")),
        proxy_expected=obj.get("proxy_expected", None),
        expected_implementation=obj.get("expected_implementation"),
        source_reference=obj.get("source_reference", ""),
        metadata={k: v for k, v in obj.items() if k not in (
            "name", "symbol", "address", "chain_id", "chainId", "network", "category",
            "kind", "proxy_expected", "expected_implementation", "source_reference")},
        errors=errors,
        path=path,
    )


def _looks_like_network_bucket(value) -> bool:
    """A network bucket is a dict that holds addresses or a contracts list."""
    if not isinstance(value, dict):
        return False
    if isinstance(value.get("contracts"), list):
        return True
    if "address" in value:  # this is a single entry, not a network bucket
        return False
    return any(is_address(v) or (isinstance(v, dict) and "address" in v) for v in value.values())


def _parse_contracts_list(items, *, program="", chain="", errors=None, path="", entries=None, saw_contracts_key=False):
    for obj in items:
        if isinstance(obj, dict) and ("address" in obj or "name" in obj):
            entry = _entry_from_obj(obj, chain_id="", network=chain, errors=errors, path=path)
            if entry is not None:
                entries.append(entry)


def parse_addresses(addresses_file: str) -> M.AddressParseResult:
    """Parse an addresses file into a normalized AddressParseResult (parser v2)."""
    raw = (addresses_file or "").strip()
    if not raw:
        return M.AddressParseResult(status=M.ADDRESS_NONE_PROVIDED, path="",
                                    notes=["No --addresses file provided."])

    path = str(Path(addresses_file).expanduser())
    p = Path(path)
    if not p.is_file():
        return M.AddressParseResult(status=M.ADDRESS_FILE_MISSING, path=path,
                                    errors=[{"path": path, "error": "file_missing"}],
                                    notes=["Addresses file does not exist."])
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return M.AddressParseResult(status=M.ADDRESS_PARSE_ERROR, path=path,
                                    errors=[{"path": path, "error": type(exc).__name__}])
    if not text.strip():
        return M.AddressParseResult(status=M.ADDRESS_FILE_EMPTY, path=path,
                                    errors=[{"path": path, "error": "file_empty"}],
                                    notes=["Addresses file is empty."])
    try:
        data = json.loads(text)
    except ValueError as exc:
        return M.AddressParseResult(status=M.ADDRESS_PARSE_ERROR, path=path,
                                    errors=[{"path": path, "error": f"invalid_json: {type(exc).__name__}"}],
                                    notes=["Addresses file is not valid JSON."])

    entries: list = []
    errors: list = []
    detected = ""
    saw_explicit_empty_contracts = False

    if isinstance(data, dict) and isinstance(data.get("chains"), dict):
        detected = "chains_map"
        for chain_key, bucket in data["chains"].items():
            if isinstance(bucket, dict) and isinstance(bucket.get("contracts"), list):
                if not bucket["contracts"]:
                    saw_explicit_empty_contracts = True
                for obj in bucket["contracts"]:
                    if isinstance(obj, dict):
                        e = _entry_from_obj(obj, chain_id=str(chain_key), errors=errors, path=path)
                        if e is not None:
                            entries.append(e)
            elif isinstance(bucket, dict):
                for name, val in bucket.items():
                    if is_address(val):
                        e = _make_entry(name, val, chain_id=str(chain_key), errors=errors, path=path)
                        if e is not None:
                            entries.append(e)

    elif isinstance(data, dict) and isinstance(data.get("contracts"), list):
        detected = "program_contracts" if ("program" in data or "chain" in data) else "contracts_array"
        chain = str(data.get("chain", ""))
        if not data["contracts"]:
            saw_explicit_empty_contracts = True
        for obj in data["contracts"]:
            if isinstance(obj, dict):
                e = _entry_from_obj(obj, network=chain, errors=errors, path=path)
                if e is not None:
                    entries.append(e)

    elif isinstance(data, list):
        detected = "list_of_objects"
        for obj in data:
            if isinstance(obj, dict):
                e = _entry_from_obj(obj, errors=errors, path=path)
                if e is not None:
                    entries.append(e)
            elif is_address(obj):
                e = _make_entry("contract", obj, errors=errors, path=path)
                if e is not None:
                    entries.append(e)

    elif isinstance(data, dict):
        # Either an environment map (network -> {name: addr}) or a flat map
        # (name -> addr | name -> {address,...}).
        bucket_values = [v for v in data.values() if _looks_like_network_bucket(v)]
        if bucket_values and len(bucket_values) == len([v for v in data.values() if isinstance(v, dict)]):
            detected = "environment_map"
            for network, bucket in data.items():
                if isinstance(bucket, dict) and isinstance(bucket.get("contracts"), list):
                    for obj in bucket["contracts"]:
                        if isinstance(obj, dict):
                            e = _entry_from_obj(obj, network=str(network), errors=errors, path=path)
                            if e is not None:
                                entries.append(e)
                elif isinstance(bucket, dict):
                    for name, val in bucket.items():
                        if is_address(val):
                            e = _make_entry(name, val, network=str(network), errors=errors, path=path)
                            if e is not None:
                                entries.append(e)
                        elif isinstance(val, dict) and "address" in val:
                            e = _entry_from_obj({"name": name, **val}, network=str(network), errors=errors, path=path)
                            if e is not None:
                                entries.append(e)
        else:
            detected = "flat_map"
            for name, val in data.items():
                if is_address(val):
                    e = _make_entry(name, val, errors=errors, path=path)
                    if e is not None:
                        entries.append(e)
                elif isinstance(val, dict) and ("address" in val):
                    e = _entry_from_obj({"name": name, **val}, errors=errors, path=path)
                    if e is not None:
                        entries.append(e)
                elif isinstance(val, str):
                    # A non-address string value in a flat map is an invalid address.
                    _make_entry(name, val, errors=errors, path=path)
    else:
        return M.AddressParseResult(status=M.ADDRESS_PARSE_ERROR, path=path,
                                    errors=[{"path": path, "error": "unsupported_top_level_type"}])

    chain_ids = sorted({e.chain_id for e in entries if e.chain_id})
    networks = sorted({e.network for e in entries if e.network})
    addr_dicts = [e.to_dict() for e in entries]

    # Status resolution: be strict, never silently skip.
    if entries:
        status = M.ADDRESS_PARSE_ERROR if errors else M.ADDRESS_OK
        notes = [f"Detected format: {detected}.", f"Parsed {len(entries)} address(es)."]
        if errors:
            notes.append(f"{len(errors)} entry(ies) had invalid addresses; see errors.")
        return M.AddressParseResult(status=status, path=path, detected_format=detected,
                                    addresses=addr_dicts, chain_ids=chain_ids, networks=networks,
                                    errors=errors, notes=notes)
    if errors:
        return M.AddressParseResult(status=M.ADDRESS_PARSE_ERROR, path=path, detected_format=detected,
                                    addresses=[], chain_ids=[], networks=[], errors=errors,
                                    notes=["Non-empty addresses file produced no valid addresses."])
    if saw_explicit_empty_contracts:
        return M.AddressParseResult(status=M.ADDRESS_EMPTY_CONTRACTS, path=path, detected_format=detected,
                                    addresses=[], chain_ids=[], networks=[],
                                    notes=["Explicit empty contracts array: valid, but no addresses to verify."])
    return M.AddressParseResult(status=M.ADDRESS_PARSE_ERROR, path=path, detected_format=detected,
                                errors=[{"path": path, "error": "no_addresses_parsed"}],
                                notes=["Non-empty addresses file but zero parseable addresses."])
