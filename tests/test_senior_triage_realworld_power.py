"""End-to-end real-world-power regression tests across the senior_realworld fixtures."""
import json
import unittest
from pathlib import Path

from arkheionx.senior_triage import models as M
from arkheionx.senior_triage.pack import build_senior_triage_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures"

SECRET = "APIKEY_SUPER_SECRET_999"
ENDPOINT = f"https://node.example.com/v3/{SECRET}"


def mock_transport(endpoint, payload):
    method = payload.get("method")
    result = {
        "eth_chainId": "0x1",
        "eth_getCode": "0x60016000f3",
        # EIP-1967 implementation slot returns an address different from expected.
        "eth_getStorageAt": "0x000000000000000000000000bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "eth_call": "0x" + "0" * 64,
    }.get(method, "0x")
    return {"jsonrpc": "2.0", "id": payload.get("id", 1), "result": result}


def by_surface(result, needle):
    for lead in result["pack"].leads:
        if needle in lead.surface:
            return lead
    raise AssertionError(f"no lead for {needle}: {[l.surface for l in result['pack'].leads]}")


class RealworldPowerTests(unittest.TestCase):
    def test_duplicate_is_killed_and_in_do_not_touch(self) -> None:
        b = FX / "senior_realworld_duplicate"
        res = build_senior_triage_pack(b, scope_file=str(b / "scope.md"),
                                       known_path=str(b / "known"), write=False)
        lead = by_surface(res, "RoundingVault.withdraw")
        self.assertEqual(lead.dedup_status, M.KNOWN_LIKELY_DUP)
        self.assertEqual(lead.decision, M.LEAD_KILL)
        self.assertTrue(any(d["id"] == lead.id for d in res["pack"].do_not_touch))
        self.assertEqual(res["triage"]["target_decision"], M.TARGET_SKIP)
        self.assertEqual(res["triage"]["top_3_leads"], [])

    def test_public_test_is_killed_before_poc(self) -> None:
        b = FX / "senior_realworld_public_test"
        res = build_senior_triage_pack(b, scope_file=str(b / "scope.md"), write=False)
        lead = by_surface(res, "ShareVault.deposit")
        self.assertEqual(lead.dedup_status, M.KNOWN_PUBLIC_TEST)
        self.assertEqual(lead.decision, M.LEAD_KILL)

    def test_fresh_adapter_is_top_pursue(self) -> None:
        b = FX / "senior_realworld_fresh_adapter"
        res = build_senior_triage_pack(b, scope_file=str(b / "scope.md"),
                                       audits_path=str(b / "audits"), write=False)
        lead = by_surface(res, "NewAdapter.withdrawTo")
        self.assertEqual(lead.decision, M.LEAD_PURSUE)
        self.assertEqual(lead.dedup_status, M.KNOWN_NO_MATCH)
        self.assertEqual(lead.freshness_status, M.NEW_ADAPTER)
        self.assertEqual(res["triage"]["target_decision"], M.TARGET_TOUCH)
        self.assertEqual(res["triage"]["top_3_leads"][0]["id"], lead.id)

    def test_proxy_diff_mismatch_boosts_priority_with_mock_rpc(self) -> None:
        b = FX / "senior_realworld_proxy_diff"
        with_rpc = build_senior_triage_pack(
            b, scope_file=str(b / "scope.md"), addresses_file=str(b / "addresses.json"),
            rpc_endpoint=ENDPOINT, rpc_transport=mock_transport, write=False)
        without_rpc = build_senior_triage_pack(
            b, scope_file=str(b / "scope.md"), addresses_file=str(b / "addresses.json"), write=False)
        lead_rpc = by_surface(with_rpc, "Vault.withdraw")
        lead_norpc = by_surface(without_rpc, "Vault.withdraw")
        self.assertEqual(lead_rpc.deployment_status, M.DEPLOY_IMPLEMENTATION_CHANGED)
        self.assertTrue(any(m["type"] == M.DEPLOY_IMPLEMENTATION_CHANGED
                            for m in with_rpc["triage"]["deployment_mismatches"]))
        # Verified mismatch raises priority above the unverified (capped) case.
        self.assertGreater(lead_rpc.research_priority_score, lead_norpc.research_priority_score)
        # It is a priority signal, never a confirmed bug.
        self.assertNotEqual(lead_rpc.submit_readiness, M.READY_FOR_REVIEW)

    def test_proxy_diff_masks_secret(self) -> None:
        b = FX / "senior_realworld_proxy_diff"
        res = build_senior_triage_pack(
            b, scope_file=str(b / "scope.md"), addresses_file=str(b / "addresses.json"),
            rpc_endpoint=ENDPOINT, rpc_transport=mock_transport, write=False)
        blob = "\n".join(res["contents"].values()) + json.dumps(res["triage"]) + json.dumps(res["manifest"])
        self.assertNotIn(SECRET, blob)
        self.assertNotIn(ENDPOINT, blob)
        self.assertIn("***masked***", res["triage"]["rpc_endpoint_masked"])
        self.assertEqual(res["triage"]["rpc_mode"], "read_only")

    def test_no_scope_has_no_pursue(self) -> None:
        b = FX / "senior_realworld_no_scope"
        res = build_senior_triage_pack(b, write=False)
        self.assertEqual(res["triage"]["target_decision"], M.TARGET_NEEDS_CONTEXT)
        self.assertEqual(res["counts"]["pursue"], 0)
        for lead in res["pack"].leads:
            self.assertNotEqual(lead.decision, M.LEAD_PURSUE)

    def test_no_mutation_method_anywhere(self) -> None:
        b = FX / "senior_realworld_proxy_diff"
        res = build_senior_triage_pack(
            b, scope_file=str(b / "scope.md"), addresses_file=str(b / "addresses.json"),
            rpc_endpoint=ENDPOINT, rpc_transport=mock_transport, write=False)
        blob = (json.dumps(res["triage"]) + "\n".join(res["contents"].values())).lower()
        for forbidden in ("eth_sendtransaction", "eth_sendrawtransaction", "eth_sign"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
