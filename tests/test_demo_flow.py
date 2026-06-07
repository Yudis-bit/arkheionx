"""End-to-end demo journey tests: install -> version -> doctor -> review-map ->
scan -> test-plan should connect, each step pointing at the next, with artifact
paths surfaced and conservative, non-overclaiming language throughout.
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"
FIXTURE = "examples/amm-lending-hybrid-fixture"

FORBIDDEN = ("confirmed vulnerability", "vulnerability confirmed", "audit passed", "guaranteed", "ai auditor")


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    for key in ("ARKHEIONX_COLOR", "ARKHEIONX_NO_COLOR", "NO_COLOR", "CI"):
        env.pop(key, None)
    env["NO_COLOR"] = "1"
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True, env=env,
    )


class DemoFlowTests(unittest.TestCase):
    def test_version_points_to_doctor(self) -> None:
        out = cli("version").stdout
        self.assertIn("Next", out)
        self.assertIn("arkheionx doctor", out)

    def test_doctor_points_to_review_map(self) -> None:
        out = cli("doctor").stdout
        self.assertIn("Next", out)
        self.assertIn("arkheionx review-map", out)

    def test_review_map_explains_what_to_inspect_first(self) -> None:
        result = cli("review-map", FIXTURE)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("Inspect first", result.stdout)

    def test_scan_summarizes_artifacts_score_and_points_to_test_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "r.md"
            js = Path(tmp) / "r.json"
            result = subprocess.run(
                [
                    "python3", str(SCANNER), "--root", str(REPO_ROOT / FIXTURE),
                    "--protocol-type", "auto", "--output", str(md), "--json-output", str(js),
                ],
                cwd=REPO_ROOT, text=True, capture_output=True,
                env={**os.environ, "NO_COLOR": "1"},
            )
            out = result.stdout
            self.assertIn(str(md), out)
            self.assertIn(str(js), out)
            self.assertIn("Readiness score:", out)
            # The scan must hand the user to the next step in the journey.
            self.assertIn("test-plan --report", out)
            self.assertIn(str(js), out.split("test-plan --report", 1)[1][:200])

    def test_test_plan_lists_paths_and_gives_next_step_and_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "r.md"
            js = Path(tmp) / "r.json"
            subprocess.run(
                [
                    "python3", str(SCANNER), "--root", str(REPO_ROOT / FIXTURE),
                    "--protocol-type", "auto", "--output", str(md), "--json-output", str(js),
                ],
                cwd=REPO_ROOT, check=True, text=True, capture_output=True,
                env={**os.environ, "NO_COLOR": "1"},
            )
            plan_md = Path(tmp) / "plan.md"
            sol = Path(tmp) / "Inv.t.sol"
            tp = cli("test-plan", "--report", str(js), "--output", str(plan_md), "--foundry-output", str(sol))
            self.assertEqual(tp.returncode, 0, tp.stderr)
            self.assertIn(str(plan_md), tp.stdout)
            self.assertIn("Next:", tp.stdout)
            # Conservative boundary at the end of the journey.
            self.assertIn("not a formal audit", tp.stdout.lower())
            self.assertIn("human review required", tp.stdout.lower())

    def test_no_step_overclaims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "r.md"
            js = Path(tmp) / "r.json"
            scan = subprocess.run(
                [
                    "python3", str(SCANNER), "--root", str(REPO_ROOT / FIXTURE),
                    "--protocol-type", "auto", "--output", str(md), "--json-output", str(js),
                ],
                cwd=REPO_ROOT, text=True, capture_output=True,
                env={**os.environ, "NO_COLOR": "1"},
            )
            tp = cli("test-plan", "--report", str(js), "--output", str(Path(tmp) / "p.md"))
        blob = "\n".join(
            [cli("version").stdout, cli("doctor").stdout, cli("review-map", FIXTURE).stdout, scan.stdout, tp.stdout]
        ).lower()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, blob, f"demo flow contains overclaiming phrase: {phrase!r}")


if __name__ == "__main__":
    unittest.main()
