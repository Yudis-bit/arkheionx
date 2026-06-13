"""Mocked read-only RPC tests for senior triage. No real network is ever touched."""
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.senior_triage import deployment as deploy
from arkheionx.senior_triage import deployment_rpc as rpc
from arkheionx.senior_triage import models as M

IMPL_SLOT = rpc.EIP1967_IMPLEMENTATION_SLOT
EXPECTED = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
LIVE = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def make_transport(code="0x60016000f3", impl_word=None, fail=False, recorder=None):
    impl_word = impl_word if impl_word is not None else "0x" + "0" * 24 + LIVE[2:]

    def transport(endpoint, payload):
        if recorder is not None:
            recorder.append(payload.get("method"))
        if fail:
            raise OSError("simulated network failure")
        method = payload.get("method")
        result = {
            "eth_chainId": "0x1",
            "eth_getCode": code,
            "eth_getStorageAt": impl_word,
            "eth_call": "0x" + "0" * 64,
        }.get(method, "0x")
        return {"jsonrpc": "2.0", "id": payload.get("id", 1), "result": result}

    return transport


def addresses_file(tmp, expected=EXPECTED, address="0x1111111111111111111111111111111111111111"):
    p = Path(tmp) / "addresses.json"
    p.write_text(json.dumps({
        "chain": "ethereum",
        "contracts": [{"name": "Vault", "address": address, "kind": "proxy",
                       "expected_implementation": expected, "tags": ["value-out"]}],
    }), encoding="utf-8")
    return p


def ctx_for(path):
    return M.TriageContext(repo_path=".", addresses_file=str(path), rpc_mode="read_only",
                           rpc_endpoint_masked="https://***masked***")


class ReadOnlyRpcClientTests(unittest.TestCase):
    def test_allowlist_blocks_state_changing_methods(self) -> None:
        client = rpc.ReadOnlyRpc("https://x", transport=make_transport())
        for forbidden in ("eth_sendTransaction", "eth_sendRawTransaction", "eth_sign", "personal_unlockAccount"):
            with self.assertRaises(rpc.RpcError):
                client._call(forbidden, [])

    def test_chain_id_and_code_facts(self) -> None:
        client = rpc.ReadOnlyRpc("https://x", transport=make_transport())
        self.assertEqual(client.chain_id(), 1)
        facts = client.code_facts("0x1111111111111111111111111111111111111111")
        self.assertTrue(facts["has_code"])
        self.assertTrue(facts["code_hash"].startswith("sha256:"))

    def test_eip1967_implementation_decoded(self) -> None:
        client = rpc.ReadOnlyRpc("https://x", transport=make_transport())
        impl = client.implementation("0x1111111111111111111111111111111111111111")
        self.assertEqual(impl, LIVE)

    def test_no_code_returns_zero_implementation(self) -> None:
        client = rpc.ReadOnlyRpc("https://x", transport=make_transport(code="0x"))
        self.assertFalse(client.code_facts("0x1")["has_code"])

    def test_mask_endpoint_hides_api_key(self) -> None:
        masked = rpc.mask_endpoint("https://mainnet.example.com/v3/SECRETKEY123")
        self.assertNotIn("SECRETKEY123", masked)
        self.assertIn("***masked***", masked)

    def test_decode_return_types(self) -> None:
        self.assertEqual(rpc.decode_return("address", "0x" + "0" * 24 + LIVE[2:]), LIVE)
        self.assertTrue(rpc.decode_return("bool", "0x" + "0" * 63 + "1"))
        self.assertEqual(rpc.decode_return("uint256", "0x0a"), 10)
        self.assertEqual(rpc.decode_return("raw", "0xdead"), "0xdead")


class DeploymentAssessTests(unittest.TestCase):
    def test_no_rpc_means_no_transport_call(self) -> None:
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            sig = deploy.assess_deployment(ctx_for(addresses_file(tmp)), rpc_endpoint="",
                                           transport=make_transport(recorder=calls))
        self.assertEqual(calls, [])
        self.assertEqual(sig.status, M.DEPLOY_ADDRESSES_PROVIDED)

    def test_only_read_only_methods_are_issued(self) -> None:
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            deploy.assess_deployment(ctx_for(addresses_file(tmp)), rpc_endpoint="https://x/KEY",
                                     transport=make_transport(recorder=calls))
        self.assertTrue(calls)
        for method in calls:
            self.assertIn(method, rpc.ALLOWED_METHODS)
        self.assertNotIn("eth_sendTransaction", calls)

    def test_implementation_mismatch_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sig = deploy.assess_deployment(ctx_for(addresses_file(tmp)), rpc_endpoint="https://x/KEY",
                                           transport=make_transport())
        self.assertEqual(sig.status, M.DEPLOY_RPC_READ_ONLY_CHECKED)
        self.assertEqual(sig.chain_id, 1)
        self.assertTrue(any(m["type"] == M.DEPLOY_IMPLEMENTATION_CHANGED for m in sig.mismatches))

    def test_matching_implementation_is_not_a_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sig = deploy.assess_deployment(ctx_for(addresses_file(tmp, expected=LIVE)),
                                           rpc_endpoint="https://x/KEY", transport=make_transport())
        self.assertEqual(sig.mismatches, [])
        self.assertTrue(any(r["status"] == M.DEPLOY_LIVE_SOURCE_MATCH for r in sig.results))

    def test_no_code_address_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sig = deploy.assess_deployment(ctx_for(addresses_file(tmp)), rpc_endpoint="https://x/KEY",
                                           transport=make_transport(code="0x"))
        self.assertTrue(any(m["type"] == M.DEPLOY_ADDRESS_NO_CODE for m in sig.mismatches))

    def test_rpc_failure_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sig = deploy.assess_deployment(ctx_for(addresses_file(tmp)), rpc_endpoint="https://x/KEY",
                                           transport=make_transport(fail=True))
        self.assertEqual(sig.status, M.DEPLOY_RPC_CHECK_FAILED)

    def test_no_mutation_method_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sig = deploy.assess_deployment(ctx_for(addresses_file(tmp)), rpc_endpoint="https://x/KEY",
                                           transport=make_transport())
        blob = json.dumps(sig.to_dict()).lower()
        for forbidden in ("eth_sendtransaction", "eth_sendrawtransaction", "private_key", "mnemonic"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
