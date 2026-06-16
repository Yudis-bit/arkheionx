import unittest

from arkheionx.warrun import quality_gates as Q
from arkheionx.warrun import run_war_run

from ._helpers import ROOT


class ArtifactOnlyNoSourceQualityGateTest(unittest.TestCase):
    def test_artifact_only_with_no_source_warns(self):
        result = run_war_run(ROOT / "artifact_only_with_no_source_warning", write=False)
        summary = result["ingest_summary"]
        self.assertEqual(summary.solidity_files_indexed, 0)
        self.assertGreater(summary.contracts_indexed, 0)
        artifact_gate = next(g for g in result["gates"] if g.id == Q.ARTIFACT_ONLY_WITH_NO_SOURCE_WARNING)
        zero_real_gate = next(g for g in result["gates"] if g.id == Q.ZERO_REAL_CONTRACTS_INDEXED)
        self.assertEqual(artifact_gate.status, Q.WARN)
        self.assertEqual(zero_real_gate.status, Q.WARN)


if __name__ == "__main__":
    unittest.main()
