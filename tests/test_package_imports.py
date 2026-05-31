import unittest


class PackageImportTests(unittest.TestCase):
    def test_package_imports_and_version_metadata(self) -> None:
        import arkheionx
        from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, STABLE_RELEASE, __version__

        self.assertEqual(arkheionx.__version__, "2.5.0")
        self.assertEqual(__version__, "2.5.0")
        self.assertEqual(STABLE_RELEASE, "v2.5.0")
        self.assertEqual(CURRENT_MILESTONE, "v2.5.0")
        self.assertEqual(NEXT_MILESTONE, "v2.6.0")

    def test_rule_registry_exposes_amm_and_lending(self) -> None:
        from arkheionx.rules.registry import RULE_PACKS

        self.assertIn("amm", RULE_PACKS)
        self.assertIn("lending", RULE_PACKS)
        self.assertEqual(RULE_PACKS["amm"]["prefix"], "ARK-AMM")
        self.assertEqual(RULE_PACKS["lending"]["prefix"], "ARK-LEND")


if __name__ == "__main__":
    unittest.main()
