import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = "examples/oracle-staking-fixture"
ANSI = re.compile(r"\x1b\[")


class CliWorkbenchTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "arkheionx.cli.main", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def write_execution_proof(self, path: Path) -> Path:
        payload = {
            "target": "OracleRewardFixture.stake",
            "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
            "proof_receipt_id": "proof:OracleRewardFixture_stake",
            "review_map_target": "OracleRewardFixture.stake",
            "status": "tested_passed",
            "evidence_level": "EXECUTION_CONFIRMED",
            "foundry": {"test_command": "forge test --match-test (?i)stake -vvvv"},
            "test_result": {
                "tests_run": 1,
                "passed": 1,
                "failed": 0,
                "skipped": 0,
                "failed_tests": [],
                "skipped_tests": [],
                "raw_output_path": "foundry-test.txt",
            },
            "generated_files": [],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def write_execution_trace(self, path: Path) -> Path:
        payload = {
            "target": "OracleRewardFixture.stake",
            "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
            "trace_receipt_id": "trace:OracleRewardFixture_stake",
            "review_map_target": "OracleRewardFixture.stake",
            "status": "tested_passed",
            "evidence_level": "EXECUTION_CONFIRMED",
            "tests_run": 1,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "reverts": [],
            "assertion_failures": [],
            "call_sequence": ["OracleRewardFixture::stake(uint256)"],
            "logs": [],
            "limitations": [],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

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

    def test_prove_json_no_artifacts_is_pure_json_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(
                "prove",
                FIXTURE,
                "--target",
                "OracleRewardFixture.claimReward",
                "--json",
                "--no-artifacts",
                "--artifacts-dir",
                tmp,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertNotRegex(result.stdout, ANSI)
            self.assertNotIn("ARKHEIONX", result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["target"], "OracleRewardFixture.claimReward")
            self.assertEqual(payload["evidence_level"], "HEURISTIC")
            self.assertEqual(payload["generated_files"], [])
            self.assertIn("proof_receipt_id", payload)
            self.assertFalse((Path(tmp) / ".arkheionx" / "out").exists())

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

    # --- evidence -------------------------------------------------------
    def test_evidence_from_proof_missing_trace_is_not_evidence_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proof_path = self.write_execution_proof(Path(tmp) / "input" / "proof.json")
            result = self.run_cli(
                "evidence",
                FIXTURE,
                "--from-proof",
                str(proof_path),
                "--json",
                "--artifacts-dir",
                tmp,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertNotRegex(result.stdout, ANSI)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["evidence_level"], "EXECUTION_CONFIRMED")
            self.assertNotEqual(payload["evidence_level"], "EVIDENCE_READY")
            self.assertEqual(payload["source_artifacts"]["proof_json"], str(proof_path.resolve()))
            self.assertEqual(payload["source_artifacts"]["trace_json"], "")
            self.assertEqual(payload["source_artifacts"]["trace_status"], "missing")
            self.assertFalse(payload["trace_summary"]["summary_available"])
            self.assertEqual(payload["trace_summary"]["status"], "missing")
            self.assertIn("evidence_package_id", payload)
            self.assertEqual(payload["manifest"]["package_id"], payload["evidence_package_id"])
            self.assertFalse(payload["manifest"]["checks"]["trace_linked"])
            self.assertTrue(payload["manifest"]["checks"]["trace_required_for_evidence_ready"])
            self.assertEqual(payload["manifest"]["readiness"], "execution_confirmed")
            self.assertEqual(payload["manifest"]["sources"][0]["path"], str(proof_path.resolve()))
            self.assertIn("trace", " ".join(payload["recommended_next_steps"]))

            written = Path(tmp) / ".arkheionx" / "out" / "evidence" / "OracleRewardFixture_stake" / "evidence.json"
            self.assertEqual(json.loads(written.read_text(encoding="utf-8"))["source_artifacts"]["proof_json"], str(proof_path.resolve()))

    def test_evidence_from_proof_real_trace_can_be_evidence_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proof_path = self.write_execution_proof(Path(tmp) / "input" / "proof.json")
            trace_path = proof_path.parent / "trace.json"
            trace_path.write_text(
                json.dumps({
                    "target": "OracleRewardFixture.stake",
                    "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
                    "trace_receipt_id": "trace:OracleRewardFixture_stake",
                    "review_map_target": "OracleRewardFixture.stake",
                    "evidence_level": "EXECUTION_CONFIRMED",
                    "status": "tested_passed",
                    "reverts": [],
                    "assertion_failures": [],
                    "call_sequence": ["OracleRewardFixture::stake(uint256)"],
                    "logs": [],
                }),
                encoding="utf-8",
            )
            result = self.run_cli(
                "evidence",
                FIXTURE,
                "--from-proof",
                str(proof_path),
                "--json",
                "--artifacts-dir",
                tmp,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["evidence_level"], "EVIDENCE_READY")
            self.assertEqual(payload["source_artifacts"]["proof_json"], str(proof_path.resolve()))
            self.assertEqual(payload["source_artifacts"]["trace_json"], str(trace_path.resolve()))
            self.assertEqual(payload["source_artifacts"]["trace_status"], "linked")
            self.assertTrue(payload["trace_summary"]["summary_available"])
            self.assertEqual(payload["trace_summary"]["source"], str(trace_path.resolve()))
            self.assertIn("evidence_package_id", payload)
            self.assertTrue(payload["manifest"]["checks"]["trace_linked"])
            self.assertEqual(payload["manifest"]["readiness"], "evidence_ready")
            self.assertEqual(
                {source["kind"] for source in payload["manifest"]["sources"]},
                {"proof", "trace"},
            )
            self.assertEqual(payload["manifest"]["sources"][1]["path"], str(trace_path.resolve()))

    def test_report_from_evidence_links_receipts_and_stays_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proof_path = self.write_execution_proof(Path(tmp) / "input" / "proof.json")
            trace_path = self.write_execution_trace(proof_path.parent / "trace.json")
            evidence_result = self.run_cli(
                "evidence",
                FIXTURE,
                "--from-proof",
                str(proof_path),
                "--json",
                "--artifacts-dir",
                tmp,
            )
            self.assertEqual(evidence_result.returncode, 0, evidence_result.stdout + evidence_result.stderr)
            evidence_path = Path(tmp) / "evidence-input.json"
            evidence_path.write_text(evidence_result.stdout, encoding="utf-8")
            report_result = self.run_cli(
                "report",
                FIXTURE,
                "--from-evidence",
                str(evidence_path),
                "--json",
                "--artifacts-dir",
                tmp,
            )
            self.assertEqual(report_result.returncode, 0, report_result.stdout + report_result.stderr)
            payload = json.loads(report_result.stdout)
            self.assertEqual(payload["evidence_context"]["evidence_package_id"], json.loads(evidence_result.stdout)["evidence_package_id"])
            self.assertEqual(payload["evidence_context"]["source_artifacts"]["evidence_json"], str(evidence_path.resolve()))
            self.assertEqual(payload["receipt_references"]["proof_receipt_id"], "proof:OracleRewardFixture_stake")
            self.assertEqual(payload["receipt_references"]["trace_receipt_id"], "trace:OracleRewardFixture_stake")
            self.assertEqual(payload["receipt_references"]["proof_source"], str(proof_path.resolve()))
            self.assertEqual(payload["receipt_references"]["trace_source"], str(trace_path.resolve()))
            self.assertEqual(payload["report_readiness"]["status"], "draft")
            self.assertFalse(payload["report_readiness"]["ready_for_submission"])
            self.assertTrue(payload["report_readiness"]["requires_manual_review"])
            self.assertEqual(payload["review_status"], "NEEDS_HUMAN_REVIEW")
            self.assertNotIn("HUMAN_REVIEWED", json.dumps(payload))

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
