"""Engine tests for the v5 Blind Spot Intelligence layer.

Exercises the scoring engine, surface records, blind-spot map, criticality map,
and counterfactual plan directly (no CLI). Asserts the score is additive and
transparent, labels are valid and never called severity, and output is
deterministic and makes no unsafe claims.
"""
import json
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.research.surfaces import build_research_surfaces
from arkheionx.blind_spots import (
    build_blind_spot_map,
    build_criticality_map,
    build_counterfactual_plan,
)
from arkheionx.blind_spots import models as m
from arkheionx.blind_spots import scoring
from arkheionx.blind_spots.signals import build_surface_records

REPO_ROOT = Path(__file__).resolve().parents[1]
VAULT = REPO_ROOT / "examples" / "vault-strategy-oracle-fixture"
AUTH = REPO_ROOT / "examples" / "periphery-auth-fixture"
FIXTURES = [VAULT, AUTH]

# Output must never make these claims.
_FORBIDDEN = ("confirmed vulnerability", "vulnerability confirmed", "critical found",
              "high found", "exploit generated", "guaranteed", "exploit automation is",
              "drain", "severity:")


def _records(fixture: Path):
    rm = build_review_map(fixture)
    surfaces = build_research_surfaces(rm, fixture)
    return rm, surfaces, build_surface_records(rm, surfaces)


class ScoringTests(unittest.TestCase):
    def test_score_is_additive_sum_of_components(self) -> None:
        for fixture in FIXTURES:
            _, _, records = _records(fixture)
            self.assertTrue(records, fixture.name)
            for r in records:
                self.assertEqual(
                    r.blind_spot_score,
                    r.impact_score + r.review_gap_score + r.complexity_score + r.assumption_score,
                    f"{fixture.name}:{r.target}",
                )

    def test_labels_are_valid(self) -> None:
        for fixture in FIXTURES:
            _, _, records = _records(fixture)
            for r in records:
                self.assertIn(r.criticality_potential, m.CRITICALITY_LABELS, r.target)
                self.assertIn(r.review_density, m.DENSITY_LABELS, r.target)
                self.assertIn(r.blind_spot_priority, m.BLIND_SPOT_PRIORITIES, r.target)

    def test_criticality_thresholds(self) -> None:
        self.assertEqual(scoring.criticality_label(60, True), m.CRIT_VERY_HIGH)
        self.assertEqual(scoring.criticality_label(40, True), m.CRIT_HIGH)
        self.assertEqual(scoring.criticality_label(20, True), m.CRIT_MEDIUM)
        self.assertEqual(scoring.criticality_label(5, True), m.CRIT_LOW)
        self.assertEqual(scoring.criticality_label(0, False), m.CRIT_UNKNOWN)

    def test_blind_spot_priority_thresholds(self) -> None:
        self.assertEqual(scoring.blind_spot_priority(85), m.BSP_VERY_HIGH)
        self.assertEqual(scoring.blind_spot_priority(70), m.BSP_HIGH)
        self.assertEqual(scoring.blind_spot_priority(40), m.BSP_MEDIUM)
        self.assertEqual(scoring.blind_spot_priority(10), m.BSP_MONITOR)

    def test_every_record_has_score_reasons(self) -> None:
        for fixture in FIXTURES:
            _, _, records = _records(fixture)
            for r in records:
                self.assertTrue(r.score_reasons, f"{fixture.name}:{r.target} missing reasons")


class BlindSpotMapTests(unittest.TestCase):
    def test_candidates_are_high_impact_weak_coverage(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_blind_spot_map(rm, surfaces, source_files=4, test_files=1)
        self.assertTrue(data["candidates"], "expected blind spot candidates on the auth fixture")
        # Every candidate is weak density and at least medium criticality potential.
        for c in data["candidates"]:
            self.assertIn(c["review_density"], (m.DENSITY_WEAK, m.DENSITY_NONE, m.DENSITY_UNKNOWN))
            self.assertIn(c["criticality_potential"], (m.CRIT_VERY_HIGH, m.CRIT_HIGH, m.CRIT_MEDIUM))
            self.assertTrue(c["id"].startswith("BSP-"))
            self.assertEqual(c["status"], "open")
            self.assertTrue(c["manual_review_required"])
        # The untested Merkle authorization surface is a clear blind spot here.
        targets = {c["target"] for c in data["candidates"]}
        self.assertIn("OfferAuth.claimWithProof", targets, targets)
        # At least one very-high criticality candidate exists.
        self.assertTrue(any(c["criticality_potential"] == m.CRIT_VERY_HIGH for c in data["candidates"]))

    def test_candidate_score_components_match_total(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_blind_spot_map(rm, surfaces)
        for c in data["candidates"]:
            sc = c["score_components"]
            self.assertEqual(c["blind_spot_score"],
                             sc["impact"] + sc["review_gap"] + sc["complexity"] + sc["assumption"])

    def test_scoring_model_is_exposed(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_blind_spot_map(rm, surfaces)
        self.assertIn("formula", data["scoring"])
        self.assertIn("impact_points", data["scoring"])
        self.assertIn("not a severity", data["scoring"]["note"])

    def test_unknown_and_notable_sections_present(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_blind_spot_map(rm, surfaces)
        self.assertIn("unknown_surfaces", data)
        self.assertIn("notable_non_blind_spots", data)
        self.assertTrue(data["safety"]["human_review_required"])

    def test_vault_fixture_produces_candidates(self) -> None:
        rm = build_review_map(VAULT)
        surfaces = build_research_surfaces(rm, VAULT)
        data = build_blind_spot_map(rm, surfaces)
        self.assertTrue(data["candidates"])


class CriticalityMapTests(unittest.TestCase):
    def test_value_exit_surface_is_very_high(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_criticality_map(rm, surfaces)
        by_target = {s["target"]: s for s in data["surfaces"]}
        self.assertIn("LedgerCore.withdraw", by_target)
        self.assertEqual(by_target["LedgerCore.withdraw"]["criticality_potential"], m.CRIT_VERY_HIGH)
        self.assertTrue(data["highest_blast_radius"])

    def test_oracle_surface_ranked_on_vault_fixture(self) -> None:
        rm = build_review_map(VAULT)
        surfaces = build_research_surfaces(rm, VAULT)
        data = build_criticality_map(rm, surfaces)
        dims = {d["dimension"] for s in data["surfaces"] for d in s["dimensions"]}
        self.assertIn("oracle dependency", dims, "oracle dimension should appear on the vault fixture")

    def test_criticality_never_called_severity(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_criticality_map(rm, surfaces)
        blob = json.dumps(data).lower()
        # No field is named "severity" and no severity label is assigned.
        self.assertNotIn('"severity"', blob)
        self.assertNotIn("severity:", blob)
        # The output explicitly frames criticality as NOT severity.
        self.assertIn("not severity", blob)
        for s in data["surfaces"]:
            self.assertIn(s["criticality_potential"], m.CRITICALITY_LABELS)


class CounterfactualTests(unittest.TestCase):
    def test_counterfactuals_have_required_fields(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_counterfactual_plan(rm, surfaces)
        self.assertTrue(data["counterfactuals"])
        ids = [cf["id"] for cf in data["counterfactuals"]]
        self.assertEqual(ids, sorted(ids))
        self.assertTrue(all(cf_id.startswith("CF-") for cf_id in ids))
        for cf in data["counterfactuals"]:
            for field in ("assumption", "what_if_false", "why_it_could_matter",
                          "local_test_direction", "evidence_needed", "stop_condition", "do_not_claim"):
                self.assertTrue(cf[field], f"{cf['id']} missing {field}")
            self.assertEqual(cf["status"], "open")

    def test_auth_and_periphery_counterfactuals_on_auth_fixture(self) -> None:
        rm = build_review_map(AUTH)
        surfaces = build_research_surfaces(rm, AUTH)
        data = build_counterfactual_plan(rm, surfaces)
        topics = {cf["topic"] for cf in data["counterfactuals"]}
        self.assertTrue({"merkle-binds", "signature-binds"} & topics, topics)
        self.assertIn("periphery-equivalence", topics)
        self.assertIn("counterfactual_matrix", data)
        self.assertEqual(len(data["counterfactual_matrix"]), len(data["counterfactuals"]))

    def test_oracle_counterfactual_on_vault_fixture(self) -> None:
        rm = build_review_map(VAULT)
        surfaces = build_research_surfaces(rm, VAULT)
        data = build_counterfactual_plan(rm, surfaces)
        topics = {cf["topic"] for cf in data["counterfactuals"]}
        self.assertIn("oracle-fresh", topics, topics)


class BlindSpotFixtureTests(unittest.TestCase):
    """The dedicated blind-spot-fixture should exercise every detector category."""

    FIXTURE = REPO_ROOT / "examples" / "blind-spot-fixture"

    def test_fixture_exists(self) -> None:
        self.assertTrue(self.FIXTURE.is_dir(), "examples/blind-spot-fixture must exist")

    def test_exercises_all_counterfactual_families(self) -> None:
        rm = build_review_map(self.FIXTURE)
        surfaces = build_research_surfaces(rm, self.FIXTURE)
        topics = {cf["topic"] for cf in build_counterfactual_plan(rm, surfaces)["counterfactuals"]}
        # oracle, authorization (signature + Merkle), periphery, and liquidation
        # families should all be present in one repository.
        self.assertIn("oracle-fresh", topics, topics)
        self.assertIn("signature-binds", topics, topics)
        self.assertIn("merkle-binds", topics, topics)
        self.assertIn("periphery-equivalence", topics, topics)
        self.assertIn("liquidation-bounded", topics, topics)

    def test_has_blind_spot_candidates_and_unknown_surfaces(self) -> None:
        rm = build_review_map(self.FIXTURE)
        surfaces = build_research_surfaces(rm, self.FIXTURE)
        data = build_blind_spot_map(rm, surfaces)
        self.assertTrue(data["candidates"])
        self.assertTrue(data["unknown_surfaces"])
        self.assertTrue(any(c["criticality_potential"] == m.CRIT_VERY_HIGH for c in data["candidates"]))


class DeterminismAndSafetyTests(unittest.TestCase):
    def test_deterministic_ignoring_timestamp(self) -> None:
        for fixture in FIXTURES:
            rm1 = build_review_map(fixture)
            s1 = build_research_surfaces(rm1, fixture)
            rm2 = build_review_map(fixture)
            s2 = build_research_surfaces(rm2, fixture)
            for builder in (build_blind_spot_map, build_criticality_map, build_counterfactual_plan):
                a = builder(rm1, s1)
                b = builder(rm2, s2)
                a.pop("generated_at"); b.pop("generated_at")
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True),
                                 f"{fixture.name}:{builder.__name__}")

    def test_no_unsafe_claims(self) -> None:
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            surfaces = build_research_surfaces(rm, fixture)
            for data in (build_blind_spot_map(rm, surfaces),
                         build_criticality_map(rm, surfaces),
                         build_counterfactual_plan(rm, surfaces)):
                blob = json.dumps(data).lower()
                for phrase in _FORBIDDEN:
                    self.assertNotIn(phrase, blob, f"{fixture.name}: forbidden {phrase!r}")
                self.assertTrue(data["safety"]["human_review_required"])


if __name__ == "__main__":
    unittest.main()
