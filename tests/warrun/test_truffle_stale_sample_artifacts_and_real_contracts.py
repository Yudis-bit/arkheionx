import unittest

from ._helpers import run_fixture


class TruffleStaleSampleArtifactsTest(unittest.TestCase):
    def test_stale_sample_artifacts_do_not_create_fake_clean_result(self):
        result = run_fixture("truffle_with_stale_sample_artifacts_and_real_contracts")
        summary = result["ingest_summary"]
        smap = result["smap"]
        self.assertEqual(summary.framework, "truffle_style")
        self.assertGreater(summary.solidity_files_indexed, 0)
        self.assertGreater(summary.contracts_indexed, 0)
        self.assertGreater(summary.real_contracts_indexed, 0)
        self.assertGreaterEqual(summary.sample_artifacts_ignored, 3)
        self.assertTrue(any("STALE_ARTIFACT_IGNORED" in w for w in summary.warnings))
        self.assertIsNotNone(smap.contract("GenericCoreWallet"))
        self.assertIsNone(smap.contract("Migrations"))
        self.assertIsNone(smap.contract("MetaCoin"))
        self.assertIsNone(smap.contract("ConvertLib"))


if __name__ == "__main__":
    unittest.main()
