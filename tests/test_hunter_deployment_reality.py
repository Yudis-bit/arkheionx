"""Tests for the hunter deployment-reality engine (read-only, mock transport)."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
PROXY = FX / "proxy_impl_changed"
SECRET = "APIKEY_SUPER_SECRET_999"
ENDPOINT = f"https://node.example.com/v3/{SECRET}"

DIFF_IMPL = "0x000000000000000000000000bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
MATCH_IMPL = "0x000000000000000000000000aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def mock(storage_value, code="0x60016000f3"):
    def _t(endpoint, payload):
        res = {"eth_chainId": "0x1", "eth_getCode": code,
               "eth_getStorageAt": storage_value, "eth_call": "0x" + "0" * 64}.get(payload.get("method"), "0x")
        return {"jsonrpc": "2.0", "id": payload.get("id", 1), "result": res}
    return _t


class DeploymentRealityTests(unittest.TestCase):
    def test_rpc_not_provided_without_endpoint(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"), write=False)
        self.assertEqual(res["pack"].deployment_reality.status, M.RPC_NOT_PROVIDED)

    def test_implementation_changed_detected(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock(DIFF_IMPL), write=False)
        d = res["pack"].deployment_reality
        self.assertEqual(d.status, M.READ_ONLY_RPC_ENABLED)
        self.assertTrue(any(m["type"] == M.DEPLOY_IMPLEMENTATION_CHANGED for m in d.mismatches))
        dlead = [l for l in res["pack"].leads if l.lead_type == M.DEPLOYMENT_MISMATCH]
        self.assertTrue(dlead, "implementation change must produce a DEPLOYMENT_MISMATCH lead")

    def test_implementation_match(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock(MATCH_IMPL), write=False)
        statuses = {r["status"] for r in res["pack"].deployment_reality.results}
        self.assertIn(M.IMPLEMENTATION_MATCH, statuses)
        self.assertFalse(res["pack"].deployment_reality.mismatches)

    def test_address_no_code(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock("0x" + "0" * 64, code="0x"),
                                write=False)
        statuses = {r["status"] for r in res["pack"].deployment_reality.results}
        self.assertIn(M.ADDRESS_NO_CODE, statuses)
        # A no-code address kills the dependent lead.
        nocode_leads = [l for l in res["pack"].leads if l.deployment_status == M.ADDRESS_NO_CODE]
        for lead in nocode_leads:
            self.assertIn(lead.decision, M.KILL_DECISIONS)

    def test_priority_higher_with_verified_mismatch(self) -> None:
        with_rpc = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                     addresses_file=str(PROXY / "addresses.json"),
                                     rpc_endpoint=ENDPOINT, rpc_transport=mock(DIFF_IMPL), write=False)
        no_rpc = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                   addresses_file=str(PROXY / "addresses.json"), write=False)
        top_with = with_rpc["pack"].top_leads(1)
        self.assertTrue(top_with)
        self.assertEqual(top_with[0].lead_type, M.DEPLOYMENT_MISMATCH)
        self.assertIn(top_with[0].decision, M.PURSUEABLE)


if __name__ == "__main__":
    unittest.main()
