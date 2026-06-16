"""Tests for hunter lead ranking and the decision policy."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
PROXY = FX / "proxy_impl_changed"
SECRET = "k"
ENDPOINT = f"https://node.example.com/{SECRET}"


def mock(endpoint, payload):
    res = {"eth_chainId": "0x1", "eth_getCode": "0x60016000f3",
           "eth_getStorageAt": "0x" + "0" * 24 + "bb" * 20, "eth_call": "0x" + "0" * 64}.get(
        payload.get("method"), "0x")
    return {"jsonrpc": "2.0", "id": payload.get("id", 1), "result": res}


class LeadRankingTests(unittest.TestCase):
    def test_decisions_are_valid_vocabulary(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        for lead in res["pack"].leads:
            self.assertIn(lead.decision, M.DECISIONS, lead.lead_id)

    def test_pursueable_ranked_above_parked_and_killed(self) -> None:
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock, write=False)
        ranked = res["pack"].ranked_leads()
        # ranked_leads is ordered by descending score (a research-priority ordering).
        scores = [l.score for l in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(any(l.decision in M.PURSUEABLE for l in ranked))
        # The single top lead is pursueable (a verified deployment mismatch).
        self.assertIn(res["pack"].top_leads(1)[0].decision, M.PURSUEABLE)

    def test_top_leads_only_pursueable_or_parked(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        for lead in res["pack"].top_leads():
            self.assertIn(lead.decision, M.PURSUEABLE + M.PARK_DECISIONS)

    def test_scope_collision_caps_all_leads(self) -> None:
        b = FX / "scope_collision_versions"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        for lead in res["pack"].leads:
            self.assertEqual(lead.decision, M.PARK_SCOPE)

    def test_deployment_mismatch_is_clear_signal(self) -> None:
        # A verified mismatch bypasses the soft caps and is pursueable even with thin context.
        res = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                addresses_file=str(PROXY / "addresses.json"),
                                rpc_endpoint=ENDPOINT, rpc_transport=mock, write=False)
        dlead = [l for l in res["pack"].leads if l.lead_type == M.DEPLOYMENT_MISMATCH]
        self.assertTrue(dlead)
        self.assertTrue(any(l.decision in M.PURSUEABLE for l in dlead))

    def test_score_breakdown_and_reasons_present(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                known_path=str(b / "known"), audits_path=str(b / "audits"), write=False)
        for lead in res["pack"].leads:
            self.assertTrue(lead.score_breakdown)
            self.assertTrue(lead.decision_reasons)
            self.assertTrue(lead.kill_conditions)


if __name__ == "__main__":
    unittest.main()
