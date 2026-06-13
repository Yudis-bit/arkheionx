"""End-to-end regression across all 16 generic hunter fixtures."""
import json
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"

FIXTURES = [
    "duplicate_public_test", "dedup_blind", "fresh_state_machine_value_flow", "proxy_impl_changed",
    "scope_collision_versions", "nested_addresses", "registry_live_not_listed", "source_recovery_mock",
    "call_graph_spurious", "fee_dispatch_value_flow", "queue_double_claim", "trusted_role_only",
    "oos_artifact", "adapter_withdrawability", "cross_pool_isolation", "bridge_domain_replay",
]

ARTIFACTS = (
    "00-run-context.md", "01-scope-map.md", "02-source-provenance.md", "03-known-issue-map.md",
    "04-freshness-map.md", "05-deployment-reality.md", "06-value-flow-map.md", "07-state-machine-map.md",
    "08-top-leads.md", "09-poc-plans.md", "10-submission-risk.md", "11-report-filter.md",
    "90-engine-evaluation.md",
)


def build(name):
    b = FX / name
    a = dict(write=False)
    if (b / "scope.md").is_file():
        a["scope_file"] = str(b / "scope.md")
    if (b / "known").is_dir():
        a["known_path"] = str(b / "known")
    if (b / "audits").is_dir():
        a["audits_path"] = str(b / "audits")
    if (b / "addresses.json").is_file():
        a["addresses_file"] = str(b / "addresses.json")
    return build_hunter_pack(b, **a)


class EndToEndFixtureTests(unittest.TestCase):
    def test_all_fixtures_build_with_all_artifacts(self) -> None:
        for name in FIXTURES:
            res = build(name)
            for art in ARTIFACTS:
                self.assertIn(art, res["contents"], f"{name}: missing {art}")
            self.assertEqual(res["triage"]["artifact_type"], "hunter_triage", name)

    def test_decisions_use_valid_vocabulary(self) -> None:
        for name in FIXTURES:
            res = build(name)
            for lead in res["pack"].leads:
                self.assertIn(lead.decision, M.DECISIONS, f"{name}:{lead.lead_id}")
                self.assertIn(lead.lead_type, M.LEAD_TYPES, f"{name}:{lead.lead_id}")

    def test_no_forbidden_outcome_terms(self) -> None:
        for name in FIXTURES:
            res = build(name)
            blob = "\n".join(res["contents"].values()) + json.dumps(res["triage"])
            for term in M.FORBIDDEN_OUTCOME_TERMS:
                self.assertNotIn(term, blob, f"{name}: forbidden term {term}")

    def test_specific_fixture_outcomes(self) -> None:
        # The key per-fixture regression assertions, in one place.
        dup = build("duplicate_public_test")["pack"]
        self.assertTrue(any(l.decision == M.KILL_PUBLIC_TEST_COVERED for l in dup.leads))

        blind = build("dedup_blind")
        self.assertEqual(blind["triage"]["dedup_status"], M.DEDUP_BLIND)
        self.assertTrue(all(l.decision == M.PARK_DEDUP for l in blind["pack"].leads))

        fresh = build("fresh_state_machine_value_flow")["pack"]
        self.assertTrue(any(l.lead_type == M.STATE_MACHINE_VALUE_FLOW and l.decision in M.PURSUEABLE
                            for l in fresh.leads))

        collide = build("scope_collision_versions")["pack"]
        self.assertEqual(collide.program_identity.scope_status, M.SCOPE_COLLISION)
        self.assertTrue(all(l.decision == M.PARK_SCOPE for l in collide.leads))

        trusted = build("trusted_role_only")["pack"]
        self.assertTrue(any(l.decision == M.KILL_TRUSTED_ROLE for l in trusted.leads))

        oos = build("oos_artifact")["pack"]
        self.assertTrue(any(l.decision == M.KILL_OOS for l in oos.leads))

        nested = build("nested_addresses")["triage"]
        self.assertEqual(nested["address_parse"]["status"], M.ADDRESS_OK)
        self.assertEqual(set(nested["address_parse"]["chain_ids"]), {"1", "8453"})

    def test_report_filter_defaults_submit_no(self) -> None:
        for name in FIXTURES:
            res = build(name)
            for row in res["pack"].report_filter:
                self.assertIn(row.submit, ("NO", "AFTER_POC_ASSERTION_PASSES"))
                self.assertNotEqual(row.submit, "YES")


if __name__ == "__main__":
    unittest.main()
