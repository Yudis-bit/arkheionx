import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ConfigLoaderTests(unittest.TestCase):
    def test_default_config_loads(self) -> None:
        from arkheionx.config.schema import normalize_config

        result = normalize_config({})
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.normalized_config["schema_version"], "1.7.0")
        self.assertEqual(result.normalized_config["protocol_type"], "auto")
        self.assertTrue(result.normalized_config["scan"]["ignore_generated_artifacts"])

    def test_example_config_validates(self) -> None:
        from arkheionx.config.loader import load_and_validate_config

        result = load_and_validate_config(REPO_ROOT / "examples/arkheionx.config.example.json", REPO_ROOT)
        self.assertTrue(result.valid, result.errors)
        self.assertIn("amm", result.normalized_config["rule_packs"])
        self.assertEqual(result.normalized_config["min_confidence"], "low")

    def test_all_example_configs_validate(self) -> None:
        from arkheionx.config.loader import load_and_validate_config

        for path in sorted((REPO_ROOT / "examples/configs").glob("*.config.json")):
            result = load_and_validate_config(path, REPO_ROOT)
            self.assertTrue(result.valid, f"{path}: {result.errors}")

    def test_dangerous_keys_fail_validation(self) -> None:
        from arkheionx.config.schema import normalize_config

        result = normalize_config({"schema_version": "1.7.0", "rpc_url": "https://example.invalid"})
        self.assertFalse(result.valid)
        self.assertTrue(any("Dangerous config key" in item for item in result.errors))

    def test_unknown_protocol_and_rule_pack_fail(self) -> None:
        from arkheionx.config.schema import normalize_config

        result = normalize_config({"protocol_type": "bridge", "rule_packs": ["vault", "unknown"]})
        self.assertFalse(result.valid)
        self.assertTrue(any("protocol_type" in item for item in result.errors))
        self.assertTrue(any("Unknown rule pack" in item for item in result.errors))

    def test_suppression_requires_reason(self) -> None:
        from arkheionx.config.schema import normalize_config

        result = normalize_config({"suppressions": [{"id": "ARK-VLT-001"}]})
        self.assertFalse(result.valid)
        self.assertTrue(any("reason" in item for item in result.errors))


if __name__ == "__main__":
    unittest.main()
