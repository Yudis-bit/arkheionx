"""Reachability evidence propagation into hunter JSON and markdown artifacts."""
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "hunter" / "reachability_inline_assembly_role"


class ReachabilityArtifactTests(unittest.TestCase):
    def test_json_and_markdown_explain_reachability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hunter"
            result = build_hunter_pack(
                FIXTURE,
                scope_file=str(FIXTURE / "scope.md"),
                out_dir=out,
                strict_context=True,
                write=True,
            )
            triage = json.loads((out / "triage.json").read_text(encoding="utf-8"))
            blob = json.dumps(triage)
            self.assertIn("ORACLE_GATED_EXTERNAL", blob)
            self.assertIn("ROLE_GETTER_ASSEMBLY_SLOAD", blob)
            self.assertIn("updateRate", blob)

            value_flow = (out / "06-value-flow-map.md").read_text(encoding="utf-8")
            top_leads = (out / "08-top-leads.md").read_text(encoding="utf-8")
            poc_plans = (out / "09-poc-plans.md").read_text(encoding="utf-8")
            submission = (out / "10-submission-risk.md").read_text(encoding="utf-8")
            report_filter = (out / "11-report-filter.md").read_text(encoding="utf-8")

            self.assertIn("ORACLE_GATED_EXTERNAL", value_flow)
            self.assertIn("ROLE_GETTER_ASSEMBLY_SLOAD", value_flow)
            self.assertIn("Reachability-suppressed leads", top_leads)
            self.assertIn("PoC plan: none", top_leads)
            self.assertIn("trusted-role-only lead", poc_plans)
            self.assertIn("separate authorization-bypass hypothesis", submission)
            self.assertIn("POC_BLOCKED_TRUSTED_ROLE", report_filter)
            self.assertIn("NO", report_filter)
            self.assertEqual(result["triage"]["reachability_summary"]["trusted_role_gated"], 1)


if __name__ == "__main__":
    unittest.main()
