"""Protocol Review Map CLI tests (subprocess; no network, no Foundry).

Exit-code note: review-map runs static/heuristic by default (no Foundry build),
so ``status_of`` is never "ok" and the command returns 1 (heuristic review
guidance) by design — not a failure. Tests assert ``returncode in (0, 1)``: 0 is
reserved for compiler-confirmed runs, 1 is the normal static case, and 2 is a
real usage/input error. Neither ``make validate`` nor the release-readiness gate
invokes review-map, so this expected rc=1 never blocks the build.
"""
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "arkheionx" / "demo" / "fixtures" / "oracle-staking"
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, color: str = "never", env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class ReviewMapCliTests(unittest.TestCase):
    def test_help_lists_review_map(self) -> None:
        result = run_cli("--help")
        self.assertIn("review-map", result.stdout)

    def test_review_map_help(self) -> None:
        result = run_cli("review-map", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for opt in ("--out", "--top", "--json", "--no-write", "--include-low-confidence", "--target"):
            self.assertIn(opt, result.stdout)

    def test_nonexistent_path_clean_error(self) -> None:
        result = run_cli("review-map", "no/such/dir")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a directory", result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_solidity_files_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("no Solidity files", result.stdout)
        self.assertIn("demo --copy", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_top_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", str(FIXTURE), "--top", "0", "--out", tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--top", result.stdout)

    def test_writes_artifacts_to_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", str(FIXTURE), "--out", tmp)
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertIn("ARKHEIONX REVIEW MAP", result.stdout)
            self.assertTrue((Path(tmp) / "review-map.json").is_file())
            self.assertTrue((Path(tmp) / "review-map.md").is_file())

    def test_json_is_valid_and_only_json(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--json", color="always")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)  # raises if not pure JSON
        self.assertIn("schema_version", payload)
        self.assertIn("generated_at", payload)
        self.assertNotRegex(result.stdout, ANSI)

    def test_no_write_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            copy = run_cli("demo", "--copy", "lending-vault", str(repo))
            self.assertEqual(copy.returncode, 0, copy.stderr)
            result = run_cli("review-map", str(repo), "--no-write")
            self.assertIn(result.returncode, (0, 1))
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())

    def test_human_output_color_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plain = run_cli("review-map", str(FIXTURE), "--no-write", color="never")
            self.assertNotRegex(plain.stdout, ANSI)
            forced = run_cli("review-map", str(FIXTURE), "--no-write", color="always")
            self.assertRegex(forced.stdout, ANSI)  # color utility forces ANSI

    def test_target_filter_and_bad_target(self) -> None:
        ok = run_cli("review-map", str(FIXTURE), "--target", "OracleRewardFixture.claimReward", "--no-write")
        self.assertIn(ok.returncode, (0, 1))
        bad = run_cli("review-map", str(FIXTURE), "--target", "Nope.nope", "--no-write")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("could not resolve target", bad.stdout)
        self.assertNotIn("Traceback", bad.stderr)


class ReviewMapEdgeCaseTests(unittest.TestCase):
    def _src_repo(self, base: Path, body: str) -> Path:
        repo = base / "repo"
        (repo / "src").mkdir(parents=True)
        (repo / "src" / "C.sol").write_text(body, encoding="utf-8")
        return repo

    def test_empty_solidity_file_no_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._src_repo(Path(tmp), "")
            result = run_cli("review-map", str(repo), "--no-write")
            self.assertIn(result.returncode, (0, 1))
            self.assertIn("ARKHEIONX REVIEW MAP", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_contract_without_functions_no_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._src_repo(
                Path(tmp),
                "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\ncontract C { uint256 public x; }\n",
            )
            result = run_cli("review-map", str(repo), "--no-write")
            self.assertIn(result.returncode, (0, 1))
            self.assertNotIn("Traceback", result.stderr)

    def test_only_test_files_clean_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "test").mkdir(parents=True)
            (repo / "test" / "X.t.sol").write_text("contract T { function test_x() public {} }\n", encoding="utf-8")
            result = run_cli("review-map", str(repo), "--no-write")
            self.assertEqual(result.returncode, 2)
            self.assertIn("no Solidity files", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_negative_top_clean_error(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--top", "-3", "--no-write")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--top", result.stdout)

    def test_json_with_no_write_emits_json_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            self.assertEqual(run_cli("demo", "--copy", "amm-swap", str(repo)).returncode, 0)
            result = run_cli("review-map", str(repo), "--json", "--no-write")
            json.loads(result.stdout)  # valid JSON
            self.assertFalse((repo / ".arkheionx" / "out" / "review-map").exists())


class ReviewMapDemoIntegrationTests(unittest.TestCase):
    def test_review_map_on_each_demo(self) -> None:
        for demo in ("oracle-staking", "amm-swap", "lending-vault"):
            with self.subTest(demo=demo), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp) / "demo"
                out = Path(tmp) / "out"
                self.assertEqual(run_cli("demo", "--copy", demo, str(repo)).returncode, 0)
                result = run_cli("review-map", str(repo), "--out", str(out))
                self.assertIn(result.returncode, (0, 1), result.stderr)
                data = json.loads((out / "review-map.json").read_text(encoding="utf-8"))
                self.assertGreater(data["summary"]["functions_mapped"], 0)
                self.assertGreater(data["summary"]["value_paths"], 0)


class ReviewMapUxTests(unittest.TestCase):
    """Developer-experience presentation safety for `review-map`."""

    def _num(self, text: str, label: str) -> int | None:
        match = re.search(rf"^\s*{re.escape(label)}\s+(\d+)", text, re.M)
        return int(match.group(1)) if match else None

    def test_banner_and_boundary_present(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--no-write")
        self.assertIn("ARKHEIONX REVIEW MAP", result.stdout)
        self.assertIn("Boundary", result.stdout)
        self.assertIn("Human review required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_ci_disables_animation_no_cr_artifacts(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--no-write", env_extra={"CI": "true"})
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("\r", result.stdout)
        self.assertIn("ARKHEIONX REVIEW MAP", result.stdout)

    def test_no_animation_env_no_cr_artifacts(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--no-write", env_extra={"ARKHEIONX_NO_ANIMATION": "1"})
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("\r", result.stdout)

    def test_summary_counts_match_json(self) -> None:
        human = run_cli("review-map", str(FIXTURE), "--no-write")
        payload = json.loads(run_cli("review-map", str(FIXTURE), "--json", "--no-write").stdout)
        summary = payload["summary"]
        self.assertEqual(self._num(human.stdout, "Contracts"), summary["contracts_analyzed"])
        self.assertEqual(self._num(human.stdout, "Functions"), summary["functions_mapped"])
        self.assertEqual(self._num(human.stdout, "Value paths"), summary["value_paths"])
        self.assertEqual(self._num(human.stdout, "Test gaps"), summary["test_gaps"])

    def test_no_write_claims_memory_only_and_no_write_claim(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--no-write")
        self.assertIn("in-memory only", result.stdout)
        self.assertIn("no-write mode", result.stdout)
        # Must not claim files were written.
        self.assertNotIn("files ->", result.stdout)
        self.assertNotIn("review-map.md", result.stdout)

    def test_json_has_no_human_chrome(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--json", "--no-write", color="always")
        for chrome in ("ARKHEIONX REVIEW MAP", "[1/3]", "[2/3]", "Boundary", "Review Priorities"):
            self.assertNotIn(chrome, result.stdout)
        self.assertNotRegex(result.stdout, ANSI)
        json.loads(result.stdout)


class ReviewMapRegressionTests(unittest.TestCase):
    """Lock the pre-DX-layer contract: JSON keys, exit semantics, human sections."""

    # Exact top-level keys of the --json payload. Adding a key is an additive
    # change that must update this list deliberately; removing/renaming one is a
    # breaking regression this test is meant to catch.
    JSON_TOP_LEVEL_KEYS = {
        "schema_version", "generated_at", "repo_path", "mode", "summary",
        "contracts", "functions", "value_paths", "assumptions", "test_gaps",
        "proof_suggestions", "evidence_links", "reviewer_notes", "safety",
    }

    def test_json_top_level_keys_locked(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--json", "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload.keys()), self.JSON_TOP_LEVEL_KEYS)

    def test_status_line_explains_by_design_nonzero_exit(self) -> None:
        result = run_cli("review-map", str(FIXTURE), "--no-write")
        # Static fixture -> heuristic -> exit 1 by design, and the human output
        # must say so (so a developer does not read it as a crash).
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("exit code 1 by design", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_human_output_has_all_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", str(FIXTURE), "--out", tmp)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        for section in (
            "ARKHEIONX REVIEW MAP", "local/static", "Review Priorities",
            "Summary", "Artifacts", "Next", "Boundary",
        ):
            self.assertIn(section, result.stdout, section)

    def test_writes_test_gap_map_artifacts(self) -> None:
        # review-map writes the two additive Test Gap Map artifacts and points to them.
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("review-map", str(FIXTURE), "--out", tmp)
            self.assertIn(result.returncode, (0, 1), result.stderr)
            out = Path(tmp)
            self.assertTrue((out / "test-gap-map.json").is_file())
            self.assertTrue((out / "test-gap-map.md").is_file())
            payload = json.loads((out / "test-gap-map.json").read_text(encoding="utf-8"))
            self.assertIn("summary", payload)
            self.assertIn("items", payload)
            self.assertNotRegex((out / "test-gap-map.md").read_text(encoding="utf-8"), ANSI)
        self.assertIn("test-gap-map.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
