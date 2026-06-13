"""Tests for the hunter program-identity / scope-map engine and scope collisions."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def build(name, **kw):
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
    a.update(kw)
    return build_hunter_pack(b, **a)


class ScopeIdentityTests(unittest.TestCase):
    def test_identity_fields_inferred(self) -> None:
        pi = build("fresh_state_machine_value_flow")["pack"].program_identity
        self.assertIn(pi.scope_status, (M.SCOPE_OK, M.SCOPE_PARTIAL))
        self.assertTrue(pi.reward_severities)
        self.assertTrue(pi.poc_required)

    def test_scope_missing(self) -> None:
        res = build_hunter_pack(FX / "dedup_blind", write=False)  # no scope file
        self.assertEqual(res["pack"].program_identity.scope_status, M.SCOPE_MISSING)

    def test_version_collision_warns_and_caps(self) -> None:
        res = build("scope_collision_versions")
        pi = res["pack"].program_identity
        self.assertIn(M.VERSION_COLLISION_WARNING, pi.scope_warnings)
        self.assertIn(M.SCOPE_COLLISION_WARNING, pi.scope_warnings)
        self.assertEqual(pi.scope_status, M.SCOPE_COLLISION)
        # Every lead is capped to PARK_SCOPE under an unresolved scope collision.
        self.assertTrue(res["pack"].leads)
        for lead in res["pack"].leads:
            self.assertEqual(lead.decision, M.PARK_SCOPE, lead.lead_id)

    def test_scope_warning_in_triage_json(self) -> None:
        t = build("scope_collision_versions")["triage"]
        self.assertEqual(t["scope_status"], M.SCOPE_COLLISION)
        self.assertTrue(t["scope_warnings"])


if __name__ == "__main__":
    unittest.main()
