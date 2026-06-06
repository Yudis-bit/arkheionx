import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ConfigIntegrationTests(unittest.TestCase):
    def run_scan(self, args: list[str]) -> tuple[dict, str]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report = tmp_path / "report.md"
            json_report = tmp_path / "report.json"
            command = [
                "python3",
                "scripts/pre_audit_scan.py",
                "--root",
                "examples/amm-lending-hybrid-fixture",
                "--output",
                str(report),
                "--json-output",
                str(json_report),
            ] + args
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(json_report.read_text(encoding="utf-8")), report.read_text(encoding="utf-8")

    def test_scanner_accepts_config_and_reports_summary(self) -> None:
        data, report = self.run_scan(["--config", "examples/configs/amm-lending.config.json"])
        self.assertIn("config_summary", data)
        self.assertEqual(data["config_summary"]["config_source"], "examples/configs/amm-lending.config.json")
        self.assertEqual(data["config_summary"]["protocol_type_effective"], "hybrid")
        self.assertIn("Config Summary", report)

    def test_cli_protocol_overrides_config(self) -> None:
        data, _ = self.run_scan(
            ["--protocol-type", "amm", "--config", "examples/configs/amm-lending.config.json"]
        )
        self.assertEqual(data["protocol_type"], "amm")
        self.assertEqual(data["config_summary"]["protocol_type_effective"], "amm")

    def test_disabled_rule_pack_reduces_corresponding_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "no-lending.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.7.0",
                        "protocol_type": "hybrid",
                        "rule_packs": ["amm", "oracle", "testing", "docs"],
                    }
                ),
                encoding="utf-8",
            )
            data, _ = self.run_scan(["--config", str(config_path)])
        ids = {item["id"] for item in data["findings"]}
        self.assertTrue(any(item.startswith("ARK-AMM-") for item in ids))
        self.assertFalse(any(item.startswith("ARK-LEND-") for item in ids))

    def test_prefix_suppression_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / "suppress-prefix.json"
            report = tmp_path / "report.md"
            json_report = tmp_path / "report.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema_version": "1.7.0",
                        "protocol_type": "vault",
                        "suppressions": [
                            {
                                "id": "ARK-VLT",
                                "reason": "Example prefix suppression for scoped remediation tracking.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "python3",
                    "scripts/pre_audit_scan.py",
                    "--root",
                    "examples/vault-risk-fixture",
                    "--protocol-type",
                    "vault",
                    "--config",
                    str(config_path),
                    "--output",
                    str(report),
                    "--json-output",
                    str(json_report),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(json_report.read_text(encoding="utf-8"))
        self.assertFalse(any(item["id"].startswith("ARK-VLT") for item in data["findings"]))
        self.assertTrue(any(item["id"].startswith("ARK-VLT") for item in data["suppressed_findings"]))

    def test_invalid_config_fails_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "bad.json"
            config_path.write_text('{"attack_mode": true}', encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    "scripts/pre_audit_scan.py",
                    "--root",
                    "examples/amm-fixture",
                    "--config",
                    str(config_path),
                    "--output",
                    str(Path(tmp) / "report.md"),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Dangerous config key", result.stderr)


if __name__ == "__main__":
    unittest.main()
