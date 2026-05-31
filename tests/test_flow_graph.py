import unittest
from pathlib import Path

from arkheionx.flow.mermaid import render_mermaid
from arkheionx.protocol.detector import analyze

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"


class MoneyFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.flow = analyze(FIXTURE).money_flow

    def test_entrypoints_exits_holders(self) -> None:
        entry_names = {e.split(".")[-1].split("#")[0] for e in self.flow.entrypoints}
        exit_names = {e.split(".")[-1].split("#")[0] for e in self.flow.exits}
        self.assertIn("stake", entry_names)
        self.assertTrue({"claimReward", "unstake"} & exit_names)
        self.assertIn("OracleRewardFixture", self.flow.value_holders)

    def test_pricing_and_privileged(self) -> None:
        pricing = {e.split(".")[-1].split("#")[0] for e in self.flow.pricing_dependencies}
        movers = {e.split(".")[-1].split("#")[0] for e in self.flow.privileged_movers}
        self.assertIn("getPrice", pricing)
        self.assertTrue({"setOracle", "setTreasury"} <= movers)

    def test_edges_have_confidence_and_kind(self) -> None:
        self.assertTrue(self.flow.edges)
        for edge in self.flow.edges:
            self.assertIn(edge.confidence, {"low", "medium", "high"})
            self.assertTrue(edge.kind)


class MermaidTests(unittest.TestCase):
    def test_mermaid_is_well_formed(self) -> None:
        flow = analyze(FIXTURE).money_flow
        mermaid = render_mermaid(flow)
        self.assertTrue(mermaid.startswith("flowchart LR"))
        # Balanced quotes; no characters that break Mermaid labels.
        self.assertEqual(mermaid.count('"') % 2, 0)
        for ch in ["[unescaped", "}|{"]:
            self.assertNotIn(ch, mermaid)

    def test_mermaid_handles_empty_flow(self) -> None:
        from arkheionx.flow.model import MoneyFlow

        mermaid = render_mermaid(MoneyFlow())
        self.assertIn("flowchart LR", mermaid)
        self.assertIn("No value-flow edges", mermaid)


if __name__ == "__main__":
    unittest.main()
