"""Read-only deployment RPC client for senior triage.

Strictly read-only. This module only ever issues an allowlisted set of read JSON-RPC
methods (eth_chainId, eth_getCode, eth_getStorageAt, eth_call). It never sends a
transaction, never signs, never needs a private key, never mutates chain state, and
makes no call at all unless an endpoint is explicitly supplied. The endpoint is
masked in every output. A transport function can be injected so tests never touch the
network.

Note: ``code_hash`` is a local sha256 digest of the returned bytecode (a stable
comparison key), not the on-chain keccak code hash.
"""
from __future__ import annotations

import hashlib
import json
from urllib import request as _urlrequest

# The only JSON-RPC methods this client is ever allowed to issue. Anything else
# (notably any state-changing or signing method) raises before a request is built.
ALLOWED_METHODS = ("eth_chainId", "eth_getCode", "eth_getStorageAt", "eth_call")

# EIP-1967 storage slots.
EIP1967_IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
EIP1967_ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
EIP1967_BEACON_SLOT = "0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50"

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class RpcError(Exception):
    """Raised on a disallowed method or a failed read-only call."""


def mask_endpoint(raw: str) -> str:
    """Mask an endpoint so it never appears verbatim (host kept, path/key hidden)."""
    if not raw:
        return ""
    raw = raw.strip()
    scheme = raw.split("://", 1)[0] if "://" in raw else "endpoint"
    rest = raw.split("://", 1)[1] if "://" in raw else raw
    host = rest.split("/", 1)[0].split("?", 1)[0]
    return f"{scheme}://{host}/***masked***" if host else f"{scheme}://***masked***"


def _urllib_transport(endpoint: str, payload: dict, timeout: float = 10.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = _urlrequest.Request(endpoint, data=data, headers={"Content-Type": "application/json"})
    with _urlrequest.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (read-only POST)
        return json.loads(resp.read().decode("utf-8"))


def _normalize_addr(word: str) -> str:
    if not word:
        return ""
    h = word[2:] if word.startswith("0x") else word
    h = h.rjust(64, "0")[-40:]
    return "0x" + h.lower()


def _code_hash(code_hex: str) -> str:
    raw = code_hex[2:] if code_hex.startswith("0x") else code_hex
    try:
        blob = bytes.fromhex(raw)
    except ValueError:
        blob = raw.encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


class ReadOnlyRpc:
    """Minimal read-only JSON-RPC client (allowlisted methods only)."""

    def __init__(self, endpoint: str, *, transport=None, timeout: float = 10.0):
        self.endpoint = endpoint
        self._transport = transport or (lambda ep, pl: _urllib_transport(ep, pl, timeout))
        self._id = 0

    def _call(self, method: str, params: list):
        if method not in ALLOWED_METHODS:
            raise RpcError(f"method not allowed (read-only client): {method}")
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params}
        try:
            response = self._transport(self.endpoint, payload)
        except RpcError:
            raise
        except Exception as exc:  # network / parse / transport error
            raise RpcError(f"transport error: {type(exc).__name__}") from exc
        if not isinstance(response, dict):
            raise RpcError("malformed RPC response")
        if response.get("error"):
            raise RpcError(f"rpc error: {response['error']}")
        return response.get("result")

    def chain_id(self) -> int:
        result = self._call("eth_chainId", [])
        try:
            return int(result, 16) if isinstance(result, str) else int(result)
        except (TypeError, ValueError):
            return 0

    def get_code(self, address: str) -> str:
        return self._call("eth_getCode", [address, "latest"]) or "0x"

    def storage_at(self, address: str, slot: str) -> str:
        return self._call("eth_getStorageAt", [address, slot, "latest"]) or "0x"

    def eth_call(self, to: str, data: str) -> str:
        return self._call("eth_call", [{"to": to, "data": data}, "latest"]) or "0x"

    # --- higher-level read-only helpers ---------------------------------------
    def code_facts(self, address: str) -> dict:
        code = self.get_code(address)
        has_code = isinstance(code, str) and len(code) > 2 and code != "0x"
        size = (len(code) - 2) // 2 if has_code else 0
        return {"has_code": has_code, "code_size": size, "code_hash": _code_hash(code) if has_code else ""}

    def implementation(self, address: str) -> str:
        word = self.storage_at(address, EIP1967_IMPLEMENTATION_SLOT)
        addr = _normalize_addr(word) if isinstance(word, str) else ""
        return "" if addr in ("", ZERO_ADDRESS) else addr

    def admin(self, address: str) -> str:
        word = self.storage_at(address, EIP1967_ADMIN_SLOT)
        addr = _normalize_addr(word) if isinstance(word, str) else ""
        return "" if addr in ("", ZERO_ADDRESS) else addr


def decode_return(decode: str, raw: str):
    raw = raw or "0x"
    if decode == "address":
        return _normalize_addr(raw)
    if decode == "bool":
        try:
            return int(raw, 16) != 0
        except (TypeError, ValueError):
            return None
    if decode == "uint256":
        try:
            return int(raw, 16)
        except (TypeError, ValueError):
            return None
    if decode == "bytes32":
        h = raw[2:] if raw.startswith("0x") else raw
        return "0x" + h.rjust(64, "0")[-64:]
    return raw  # raw / unknown
