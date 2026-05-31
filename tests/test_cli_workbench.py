import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "examples/oracle-staking-fixture"


class CliWorkbenchTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "arkheionx.cli.main", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    # --- doctor ---------------------------------------------------------
    def test_doctor_is_usable_and_exit_zero(self) -> None:
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ARKHEIONX DOCTOR", result.stdout)
        self.assertIn("Foundry", result.stdout)
        self.assertIn("Rule packs:", result.stdout)
        self.assertIn("local/static", result.stdout)

    # --- open / map / flow / hunt: compact + heuristic exit 1 ----------
    def test_open_compact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("open", FIXTURE, "--artifacts-dir", tmp)
        self.assertEqual(result.returncode, 1)  # heuristic-only
        self.assertIn("ARKHEIONX OPEN", result.stdout)
        self.assertIn("Top Surfaces", result.stdout)

    def test_map_compact_bounded_and_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("map", FIXTURE, "--artifacts-dir", tmp)
            self.assertEqual(result.returncode, 1)
            for marker in ["ARKHEIONX MAP", "Foundry:", "Money", "Top Contracts", "Next"]:
                self.assertIn(marker, result.stdout)
            self.assertLessEqual(len(result.stdout.splitlines()), 60)
            self.assertIn("Hidden", result.stdout)
            self.assertTrue((Path(tmp) / ".arkheionx" / "out" / "map.json").exists())

    def test_show_all_includes_interfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = self.run_cli("map", FIXTURE, "--json", "--artifacts-dir", tmp)
            shown = self.run_cli("map", FIXTURE, "--json", "--show-all", "--artifacts-dir", tmp)
        base_contracts = {c["contract_name"] for c in json.loads(base.stdout)["contracts"]}
        shown_contracts = {c["contract_name"] for c in json.loads(shown.stdout)["contracts"]}
        self.assertNotIn("AggregatorV3Interface", base_contracts)
        self.assertIn("AggregatorV3Interface", shown_contracts)

    def test_flow_compact_and_mermaid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("flow", FIXTURE, "--artifacts-dir", tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Money Flow Summary", result.stdout)
            self.assertNotIn("vm.skip", result.stdout)
            self.assertTrue((Path(tmp) / ".arkheionx" / "out" / "money-flow.mmd").exists())
            mermaid = self.run_cli("flow", FIXTURE, "--mermaid", "--artifacts-dir", tmp)
            self.assertTrue(mermaid.stdout.strip().startswith("flowchart"))

    def test_hunt_targets_are_qualified_and_no_test_funcs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("hunt", FIXTURE, "--top", "5", "--artifacts-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("review targets found", result.stdout)
        # Every recommended prove target is fully qualified Contract.function.
        for m in re.findall(r"--target (\S+)", result.stdout):
            self.assertIn(".", m, f"target not qualified: {m}")
        # No bare ambiguous target and no test/invariant functions.
        self.assertNotIn("--target withdraw\n", result.stdout)
        self.assertNotIn("invariant_", result.stdout)
        self.assertNotIn("test_", result.stdout)

    # --- prove ----------------------------------------------------------
    def test_prove_qualified_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("prove", FIXTURE, "--target", "OracleRewardFixture.claimReward", "--artifacts-dir", tmp)
            self.assertEqual(result.returncode, 1)  # scaffolded, not proven
            self.assertIn("Status: scaffolded", result.stdout)
            scaffolds = list((Path(tmp) / ".arkheionx" / "out" / "proof").rglob("generated-test.sol"))
            self.assertTrue(scaffolds)
            self.assertIn("vm.skip(true)", scaffolds[0].read_text(encoding="utf-8"))

    def test_prove_requires_target(self) -> None:
        self.assertEqual(self.run_cli("prove", FIXTURE).returncode, 2)

    def test_prove_ambiguous_rejected_with_suggestions(self) -> None:
        result = self.run_cli("prove", ".", "--target", "withdraw", "--no-artifacts")
        self.assertEqual(result.returncode, 2)
        self.assertIn("ambiguous", result.stdout.lower())
        # Suggestions must be fully qualified.
        self.assertRegex(result.stdout, r"\d+\.\s+\w+\.withdraw")

    def test_bad_path_is_failure(self) -> None:
        self.assertEqual(self.run_cli("map", "no/such/dir").returncode, 2)

    # --- trace ----------------------------------------------------------
    def test_trace_no_proof_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("trace", FIXTURE, "--target", "OracleRewardFixture.claimReward", "--artifacts-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("No proof artifact found", result.stdout)
        self.assertIn("--run", result.stdout)

    def test_trace_requires_target(self) -> None:
        self.assertEqual(self.run_cli("trace", FIXTURE).returncode, 2)

    def test_trace_registered_in_help(self) -> None:
        result = self.run_cli("--help")
        self.assertIn("trace", result.stdout)
        self.assertIn("prove", result.stdout)
        self.assertIn("hunt", result.stdout)

    # --- evidence-status / validate-artifacts (v2.4.0) ------------------
    def test_evidence_status_no_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("evidence-status", FIXTURE, "--artifacts-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no-artifacts", result.stdout)
        self.assertIn("hunt", result.stdout)

    def test_validate_artifacts_empty_is_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("validate-artifacts", FIXTURE, "--artifacts-dir", tmp)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Status: ok", result.stdout)

    def test_status_and_validate_in_help(self) -> None:
        result = self.run_cli("--help")
        self.assertIn("evidence-status", result.stdout)
        self.assertIn("validate-artifacts", result.stdout)


if __name__ == "__main__":
    unittest.main()
