"""RPC safety tests for hunter mode: masking, allowlist, no mutation."""
import json
import unittest
from pathlib import Path

from arkheionx.hunter.pack import build_hunter_pack
from arkheionx.senior_triage.deployment_rpc import ALLOWED_METHODS, ReadOnlyRpc, RpcError

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
PROXY = FX / "proxy_impl_changed"
SECRET = "APIKEY_SUPER_SECRET_999"
ENDPOINT = f"https://node.example.com/v3/{SECRET}"

FORBIDDEN = (
    "eth_sendTransaction", "eth_sendRawTransaction", "personal_sign", "eth_sign",
    "eth_signTypedData", "wallet_switchEthereumChain", "debug_traceTransaction",
    "trace_call", "admin_addPeer", "miner_start", "evm_increaseTime", "anvil_setBalance",
    "hardhat_setBalance",
)


def mock(endpoint, payload):
    res = {"eth_chainId": "0x1", "eth_getCode": "0x60016000f3",
           "eth_getStorageAt": "0x" + "0" * 24 + "bb" * 20, "eth_call": "0x" + "0" * 64}.get(
        payload.get("method"), "0x")
    return {"jsonrpc": "2.0", "id": payload.get("id", 1), "result": res}


class RpcSafetyTests(unittest.TestCase):
    def test_allowlist_only(self) -> None:
        self.assertEqual(set(ALLOWED_METHODS), {"eth_chainId", "eth_getCode", "eth_getStorageAt", "eth_call"})

    def test_unsupported_method_blocked_before_request(self) -> None:
        calls = []
        rpc = ReadOnlyRpc(ENDPOINT, transport=lambda ep, pl: calls.append(pl) or {"result": "0x"})
        for method in FORBIDDEN:
            with self.assertRaises(RpcError):
                rpc._call(method, [])
        self.assertEqual(calls, [], "no request may be built for a disallowed method")

    def test_endpoint_masked_everywhere(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock, write=False)
        blob = "\n".join(res["contents"].values()) + json.dumps(res["triage"]) + json.dumps(res["manifest"])
        self.assertNotIn(SECRET, blob)
        self.assertNotIn(ENDPOINT, blob)
        self.assertIn("***masked***", res["triage"]["rpc_endpoint_masked"])
        self.assertFalse(res["triage"]["rpc_enabled"])

    def test_no_mutation_method_in_output(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock, write=False)
        blob = (json.dumps(res["triage"]) + "\n".join(res["contents"].values())).lower()
        for forbidden in ("eth_sendtransaction", "eth_sendrawtransaction", "eth_sign", "delegatecall_send"):
            self.assertNotIn(forbidden, blob)

    def test_safety_flags_present(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"), write=False)
        flags = res["triage"]["safety_flags"]
        self.assertTrue(flags["no_live_chain_mutation"])
        self.assertTrue(flags["read_only_rpc_only"])
        self.assertTrue(flags["no_auto_submit"])
        self.assertTrue(res["triage"]["human_review_required"])


if __name__ == "__main__":
    unittest.main()
