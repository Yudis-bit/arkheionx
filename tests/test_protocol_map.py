import json
import unittest
from pathlib import Path

from arkheionx.protocol.detector import analyze
from arkheionx.protocol.render import build_json, render_map, render_open
from arkheionx.protocol.semantic_adapter import load_semantic, parse_contracts
from arkheionx.protocol.source_kind import contract_source_kind, file_source_kind, function_source_kind

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"


class SemanticAdapterTests(unittest.TestCase):
    def test_parse_contracts_extracts_functions_signatures_and_signals(self) -> None:
        text = (FIXTURE / "src" / "OracleRewardFixture.sol").read_text(encoding="utf-8")
        contracts = parse_contracts(text, "src/OracleRewardFixture.sol")
        main = next(c for c in contracts if c["name"] == "OracleRewardFixture")
        fn_names = {f["name"] for f in main["functions"]}
        self.assertTrue({"stake", "unstake", "claimReward", "getPrice"} <= fn_names)
        stake = next(f for f in main["functions"] if f["name"] == "stake")
        self.assertEqual(stake["signature"], "stake(uint256)")
        get_price = next(f for f in main["functions"] if f["name"] == "getPrice")
        self.assertIn("latestRoundData", get_price["oracle_calls"])

    def test_load_semantic_static(self) -> None:
        semantic = load_semantic(FIXTURE)
        self.assertEqual(semantic["source"], "static")
        self.assertTrue(semantic["contracts"])


class SourceKindTests(unittest.TestCase):
    def test_file_kinds(self) -> None:
        self.assertEqual(file_source_kind("test/Foo.t.sol"), "test")
        self.assertEqual(file_source_kind("src/Vault.t.sol"), "test")
        self.assertEqual(file_source_kind("EVM/test/2020-10/Exploit.t.sol"), "test")
        self.assertEqual(file_source_kind("out/Foo.json"), "generated")
        self.assertIsNone(file_source_kind("src/Vault.sol"))

    def test_contract_kind_interface_and_mock(self) -> None:
        self.assertEqual(contract_source_kind({"name": "IERC20", "kind": "interface", "functions": []}, None), "interface")
        self.assertEqual(contract_source_kind({"name": "MockToken", "kind": "contract", "functions": [{}]}, None), "mock")
        self.assertEqual(contract_source_kind({"name": "Vault", "kind": "contract", "functions": [{}]}, None), "production")

    def test_function_kind_test_and_invariant(self) -> None:
        self.assertEqual(function_source_kind({"name": "test_withdraw"}, "production"), "test")
        self.assertEqual(function_source_kind({"name": "invariant_totalSupply"}, "production"), "invariant")
        self.assertEqual(function_source_kind({"name": "withdraw"}, "production"), "production")


class ClassificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analysis = analyze(FIXTURE)

    def test_protocol_types_detected(self) -> None:
        self.assertIn("oracle", self.analysis.snapshot.protocol_types)

    def test_function_roles_and_ids(self) -> None:
        by_name = {fr.function_name: fr for fr in self.analysis.functions}
        self.assertEqual(by_name["stake"].role, "Money Entry")
        self.assertEqual(by_name["claimReward"].role, "Reward Claim")
        self.assertEqual(by_name["getPrice"].role, "Oracle Read")
        self.assertTrue(by_name["setOracle"].privileged)
        self.assertEqual(by_name["claimReward"].display_id, "OracleRewardFixture.claimReward")
        self.assertTrue(by_name["claimReward"].qualified_id.endswith("OracleRewardFixture.claimReward()"))
        self.assertIn("#L", by_name["claimReward"].stable_id)

    def test_interfaces_hidden_by_default(self) -> None:
        active = {c.contract_name for c in self.analysis.contracts}
        all_names = {c.contract_name for c in self.analysis.all_contracts}
        self.assertIn("OracleRewardFixture", active)
        self.assertNotIn("AggregatorV3Interface", active)  # interface hidden
        self.assertIn("AggregatorV3Interface", all_names)
        self.assertGreater(self.analysis.hidden_counts.get("interfaces", 0), 0)

    def test_show_all_restores_interfaces(self) -> None:
        shown = analyze(FIXTURE, show_all=True)
        active = {c.contract_name for c in shown.contracts}
        self.assertIn("AggregatorV3Interface", active)


class OutputCompactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analysis = analyze(FIXTURE)

    def test_map_compact_header_and_sections(self) -> None:
        text = render_map(self.analysis, ".", {"JSON": "x.json"})
        for marker in ["ARKHEIONX MAP", "Project: .", "Status:", "Mode:", "Foundry:", "Money", "Top Contracts", "Top Functions", "Next", "Limits"]:
            self.assertIn(marker, text)

    def test_map_is_bounded_by_default(self) -> None:
        text = render_map(self.analysis, ".", {})
        self.assertLessEqual(len(text.splitlines()), 60)

    def test_open_orientation(self) -> None:
        text = render_open(self.analysis, ".")
        self.assertIn("ARKHEIONX OPEN", text)
        self.assertIn("Top Surfaces", text)

    def test_json_stable_keys(self) -> None:
        payload = build_json(self.analysis, {}, [])
        for key in ["meta", "protocol_snapshot", "money_flow", "functions", "hunter_targets", "hidden_counts", "foundry"]:
            self.assertIn(key, payload)
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
