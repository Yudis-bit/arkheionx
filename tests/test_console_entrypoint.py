import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _pip_env(tmp: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        PIP_CACHE_DIR=str(tmp / "pip-cache"),
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        PIP_NO_INDEX="1",
    )
    return env


def _install_editable_console(tmp: Path) -> Path:
    venv = tmp / "venv"
    create = subprocess.run(
        [sys.executable, "-m", "venv", "--system-site-packages", str(venv)],
        text=True,
        capture_output=True,
    )
    if create.returncode != 0:
        raise unittest.SkipTest(f"venv unavailable: {create.stdout + create.stderr}")
    install = subprocess.run(
        [
            str(venv / "bin" / "python"),
            "-m",
            "pip",
            "install",
            "-e",
            str(REPO_ROOT),
            "--no-build-isolation",
        ],
        cwd=tmp,
        text=True,
        capture_output=True,
        env=_pip_env(tmp),
    )
    if install.returncode != 0:
        raise AssertionError(install.stdout + install.stderr)
    return venv / "bin" / "arkheionx"


class ConsoleEntrypointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmpdir = tempfile.TemporaryDirectory()
        try:
            cls._arkheionx = _install_editable_console(Path(cls._tmpdir.name))
        except Exception:
            cls._tmpdir.cleanup()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmpdir.cleanup()

    def run_console(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self._arkheionx), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def test_console_help_doctor_validate_and_search(self) -> None:
        for args in [
            ("--help",),
            ("doctor",),
            ("validate-config", "--config", "examples/arkheionx.config.example.json"),
            ("search", "oracle stale price", "--limit", "2"),
        ]:
            result = self.run_console(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_console_scan_and_test_plan_outputs_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = out / "package-cli-amm-report.md"
            json_report = out / "package-cli-amm-report.json"
            sarif = out / "package-cli-amm.sarif.json"
            issue_plan = out / "package-cli-amm-issue-plan.json"
            scan = self.run_console(
                "scan",
                "examples/amm-fixture",
                "--protocol-type",
                "amm",
                "--output",
                str(report),
                "--json-output",
                str(json_report),
                "--sarif-output",
                str(sarif),
                "--issue-plan-output",
                str(issue_plan),
            )
            self.assertEqual(scan.returncode, 0, scan.stdout + scan.stderr)
            self.assertIn("Fix First:", scan.stdout)
            for path in [json_report, sarif, issue_plan]:
                self.assertTrue(path.exists(), str(path))
                json.loads(path.read_text(encoding="utf-8"))

            test_plan_json = out / "package-cli-test-plan.json"
            test_plan = self.run_console(
                "test-plan",
                "--report",
                str(json_report),
                "--output",
                str(out / "package-cli-test-plan.md"),
                "--json-output",
                str(test_plan_json),
                "--foundry-output",
                str(out / "ArkheionxPackageCLIInvariants.t.sol"),
            )
            self.assertEqual(test_plan.returncode, 0, test_plan.stdout + test_plan.stderr)
            payload = json.loads(test_plan_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["suggested_tests"])


if __name__ == "__main__":
    unittest.main()
