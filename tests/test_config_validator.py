import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ConfigValidatorCliTests(unittest.TestCase):
    def test_validate_config_cli_valid(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/validate_config.py", "--config", "examples/configs/minimal.config.json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("valid", result.stdout)

    def test_validate_config_cli_json(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/validate_config.py", "--config", "examples/configs/minimal.config.json", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["normalized_config"]["schema_version"], "1.7.0")

    def test_validate_config_cli_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"private_key": "do-not-use"}), encoding="utf-8")
            result = subprocess.run(
                ["python3", "scripts/validate_config.py", "--config", str(path)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Dangerous config key", result.stderr)


if __name__ == "__main__":
    unittest.main()
