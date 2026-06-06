"""End-to-end local public-workflow smoke tests.

No network, no secrets, no RPC. Copies each bundled demo to a temp dir and runs
the first-use path (open -> hunt -> evidence-status -> validate-artifacts) with
artifacts redirected to a temp directory. Foundry-dependent prove/trace is only
exercised when `forge` is available.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMOS = ["oracle-staking", "amm-swap", "lending-vault"]
ANSI = re.compile(r"\x1b\[")


def run_cli(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        env=env,
    )


class PublicWorkflowTests(unittest.TestCase):
    def _copy_demo(self, demo: str, dest: Path) -> None:
        result = run_cli("demo", "--copy", demo, str(dest))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((dest / "foundry.toml").is_file())
        self.assertTrue(any(dest.joinpath("src").glob("*.sol")))

    def test_local_first_use_workflow(self) -> None:
        for demo in DEMOS:
            with self.subTest(demo=demo), tempfile.TemporaryDirectory() as tmp:
                proj = Path(tmp) / "proj"
                art = Path(tmp) / "art"
                self._copy_demo(demo, proj)

                steps = {
                    "open": run_cli("open", str(proj), "--artifacts-dir", str(art)),
                    "hunt": run_cli("hunt", str(proj), "--top", "5", "--artifacts-dir", str(art)),
                    "evidence-status": run_cli("evidence-status", str(proj), "--artifacts-dir", str(art)),
                    "validate-artifacts": run_cli("validate-artifacts", str(proj), "--artifacts-dir", str(art)),
                }
                headers = {
                    "open": "ARKHEIONX OPEN",
                    "hunt": "ARKHEIONX HUNT",
                    "evidence-status": "ARKHEIONX EVIDENCE STATUS",
                    "validate-artifacts": "ARKHEIONX VALIDATE ARTIFACTS",
                }
                for name, result in steps.items():
                    self.assertIn(result.returncode, (0, 1), f"{name}: {result.stderr}")
                    self.assertIn(headers[name], result.stdout, name)
                    self.assertNotRegex(result.stdout, ANSI, f"{name} stdout has ANSI")

                out_dir = art / ".arkheionx" / "out"
                self.assertTrue((out_dir / "hunt.json").is_file())
                for path in out_dir.rglob("*"):
                    if path.is_file():
                        self.assertNotRegex(path.read_text(encoding="utf-8", errors="ignore"), ANSI, str(path))

                # Artifacts are written only under the requested directory.
                self.assertFalse((proj / ".arkheionx").exists())

    def test_local_validate_saved_output_workflow(self) -> None:
        # Saved-output ingestion: never runs forge, writes only under the repo.
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            self._copy_demo("lending-vault", proj)
            saved = proj / "forge-output.json"
            saved.write_text(json.dumps({
                "test/Demo.t.sol:DemoTest": {
                    "duration": {"secs": 0, "nanos": 1000000},
                    "test_results": {"testOk()": {"status": "Success", "kind": {"Unit": {"gas": 100}}}},
                }
            }), encoding="utf-8")

            dry = run_cli("local-validate", str(proj), "--input", str(saved), "--no-write", "--json")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertNotRegex(dry.stdout, ANSI)
            payload = json.loads(dry.stdout)
            self.assertEqual(payload["command"], "local-validate")
            self.assertIs(payload["written"], False)
            self.assertIs(payload["manual_review_required"], True)
            self.assertIs(payload["ready_for_submission"], False)
            self.assertFalse((proj / ".arkheionx").exists())

            wrote = run_cli("local-validate", str(proj), "--input", str(saved), "--json")
            self.assertEqual(wrote.returncode, 0, wrote.stderr)
            self.assertTrue((proj / ".arkheionx" / "out" / "local-validation" / "summary.json").is_file())

    @unittest.skipUnless(shutil.which("forge"), "forge not available; skipping Foundry proof path")
    def test_foundry_proof_path_when_available(self) -> None:
        demo = "amm-swap"
        target = "AMMSwapFixture.swapAForB"
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            art = Path(tmp) / "art"
            self._copy_demo(demo, proj)
            prove = run_cli("prove", str(proj), "--target", target, "--run", "--artifacts-dir", str(art))
            self.assertIn(prove.returncode, (0, 1, 2), prove.stderr)
            self.assertIn("ARKHEIONX", prove.stdout)
            self.assertNotRegex(prove.stdout, ANSI)


if __name__ == "__main__":
    unittest.main()
