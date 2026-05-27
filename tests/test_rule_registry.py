import unittest


class RuleRegistryTests(unittest.TestCase):
    def test_registry_contains_stable_rule_packs(self) -> None:
        from arkheionx.rules.registry import RULE_PACKS, list_rule_packs

        expected = {
            "vault",
            "oracle",
            "access-control",
            "reentrancy-value-flow",
            "rewards",
            "testing",
            "docs",
            "amm",
            "lending",
        }
        self.assertTrue(expected.issubset(RULE_PACKS))
        infos = list_rule_packs()
        self.assertTrue(all(item.default_enabled for item in infos))
        self.assertTrue(all(item.docs.startswith("docs/") for item in infos))

    def test_finding_id_mapping(self) -> None:
        from arkheionx.rules.registry import finding_id_to_rule_pack, is_known_finding_prefix

        self.assertEqual(finding_id_to_rule_pack("ARK-ORC-001"), "oracle")
        self.assertEqual(finding_id_to_rule_pack("ARK-UPG-001"), "access-control")
        self.assertEqual(finding_id_to_rule_pack("ARK-AMM-005"), "amm")
        self.assertEqual(finding_id_to_rule_pack("ARK-LEND-002"), "lending")
        self.assertTrue(is_known_finding_prefix("ARK-VLT"))
        self.assertFalse(is_known_finding_prefix("ARK-NOPE-001"))

    def test_unknown_rule_pack_validation(self) -> None:
        from arkheionx.rules.registry import validate_rule_pack_keys

        self.assertEqual(validate_rule_pack_keys(["vault", "amm"]), [])
        self.assertEqual(validate_rule_pack_keys(["vault", "unknown"]), ["unknown"])


if __name__ == "__main__":
    unittest.main()
