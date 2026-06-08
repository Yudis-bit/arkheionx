"""Engine tests for the v6 Evidence Graph + Interaction Matrix layer."""
import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.research.surfaces import build_research_surfaces
from arkheionx.evidence_graph import (
    build_complete_review,
    build_evidence_graph,
    build_interaction_matrix,
    build_unresolved_map,
)
from arkheionx.evidence_graph import models as m
from arkheionx.version import PACKAGE_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = [
    REPO_ROOT / "examples" / "blind-spot-fixture",
    REPO_ROOT / "examples" / "vault-strategy-oracle-fixture",
    REPO_ROOT / "examples" / "periphery-auth-fixture",
]
PRIMARY = REPO_ROOT / "examples" / "blind-spot-fixture"

FORBIDDEN = (
    "critical found", "high found", "vulnerability confirmed", "exploit generated",
    "guaranteed", "audit replacement", "proof of safety", "protocol is safe", "bug found",
)


def surfaces(fixture):
    rm = build_review_map(fixture)
    return rm, build_research_surfaces(rm, fixture)


class EvidenceGraphTests(unittest.TestCase):
    def test_nodes_have_valid_states_and_ids(self) -> None:
        for fixture in FIXTURES:
            rm, surf = surfaces(fixture)
            data = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION)
            self.assertEqual(data["kind"], "evidence-graph")
            self.assertEqual(data["command"], "evidence-graph")
            self.assertTrue(data["human_review_required"])
            self.assertTrue(data["nodes"], fixture.name)
            for n in data["nodes"]:
                self.assertRegex(n["node_id"], r"^EV-\d{3}$")
                self.assertIn(n["evidence_state"], m.EVIDENCE_STATES)
                self.assertIn(n["evidence_strength"], m.EVIDENCE_STRENGTHS)
                self.assertIn(n["surface_type"], m.SURFACE_TYPES)
                self.assertIn(n["criticality_potential"], m.CRITICALITY_LABELS)
                self.assertTrue(n["human_review_required"])

    def test_state_summary_counts_all_nodes(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION)
        self.assertEqual(sum(data["evidence_state_summary"].values()), len(data["nodes"]))
        # The fixture deliberately leaves high-impact surfaces unresolved.
        self.assertGreater(data["evidence_state_summary"]["unresolved"], 0)

    def test_high_impact_unresolved_surfaces_present(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION)
        self.assertTrue(data["unresolved_surfaces"])
        for s in data["unresolved_surfaces"]:
            self.assertIn(s["criticality_potential"], (m.CRIT_VERY_HIGH, m.CRIT_HIGH))
            self.assertIn(s["evidence_state"], m.OPEN_STATES)

    def test_default_static_has_no_confirmed_or_rejected(self) -> None:
        # Without explicit local research memory, the two strongest states are
        # never inferred from scoring.
        rm, surf = surfaces(PRIMARY)
        data = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION)
        self.assertEqual(data["evidence_state_summary"]["confirmed-candidate"], 0)
        self.assertEqual(data["evidence_state_summary"]["rejected-with-evidence"], 0)

    def test_memory_upgrades_states_with_human_review(self) -> None:
        rm, surf = surfaces(PRIMARY)
        target = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION)["nodes"][0]["surface_id"]
        memory = {target: "confirmed"}
        data = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION, memory=memory)
        node = next(n for n in data["nodes"] if n["surface_id"] == target)
        self.assertEqual(node["evidence_state"], "confirmed-candidate")
        self.assertTrue(node["human_review_required"])
        # confirmed-candidate must be explicitly framed as NOT a confirmed vulnerability.
        self.assertIn("not a confirmed vulnerability", node["why_state"].lower())


class InteractionMatrixTests(unittest.TestCase):
    def test_detects_high_impact_interaction(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_interaction_matrix(rm, surf, package_version=PACKAGE_VERSION)
        self.assertEqual(data["kind"], "interaction-matrix")
        self.assertTrue(data["interactions"])
        self.assertGreaterEqual(data["matrix_summary"]["high_impact_interactions"], 1)
        for ix in data["interactions"]:
            self.assertRegex(ix["interaction_id"], r"^IX-\d{3}$")
            self.assertIn(ix["interaction_priority"], m.INTERACTION_PRIORITIES)
            self.assertIn(ix["evidence_state"], m.EVIDENCE_STATES)
            self.assertTrue(ix["human_review_required"])

    def test_priority_is_not_severity(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_interaction_matrix(rm, surf, package_version=PACKAGE_VERSION)
        blob = json.dumps(data).lower()
        self.assertNotIn('"severity"', blob)
        self.assertNotIn("severity:", blob)
        self.assertIn("not a severity", data["scoring"]["note"].lower())

    def test_interaction_classes_are_meaningful(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_interaction_matrix(rm, surf, package_version=PACKAGE_VERSION)
        classes = set(data["matrix_summary"]["interaction_classes"])
        # The extended fixture should surface a broad spread of classes.
        self.assertGreaterEqual(len(classes), 8)
        self.assertTrue(any("oracle" in c for c in classes))
        self.assertTrue(any("value-exit" in c for c in classes))


class UnresolvedMapTests(unittest.TestCase):
    def test_structure(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_unresolved_map(rm, surf, package_version=PACKAGE_VERSION)
        self.assertEqual(data["kind"], "unresolved-map")
        for key in ("unresolved_surfaces", "unresolved_interactions", "unclassified_surfaces", "final_checklist"):
            self.assertIn(key, data)
        self.assertTrue(data["unresolved_surfaces"])
        self.assertTrue(data["final_checklist"])


class CompleteReviewTests(unittest.TestCase):
    def test_writes_required_files(self) -> None:
        rm = build_review_map(PRIMARY)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "cr"
            result = build_complete_review(rm, PRIMARY, out, package_version=PACKAGE_VERSION)
            required = [
                "00-README.md", "01-review-map-summary.md", "02-blind-spots-summary.md",
                "03-criticality-summary.md", "04-counterfactuals-summary.md", "05-evidence-graph.md",
                "06-interaction-matrix.md", "07-unresolved-surfaces.md", "08-agent-input.md",
                "09-human-review-checklist.md", "10-case-study-template.md", "manifest.json",
            ]
            for name in required:
                self.assertTrue((out / name).is_file(), name)
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["kind"], "complete-review-manifest")
            self.assertTrue(manifest["human_review_required"])
            self.assertGreater(manifest["evidence_node_count"], 0)
            self.assertGreater(manifest["interaction_count"], 0)

    def test_agent_input_is_model_agnostic(self) -> None:
        rm = build_review_map(PRIMARY)
        with tempfile.TemporaryDirectory() as tmp:
            build_complete_review(rm, PRIMARY, Path(tmp) / "cr", package_version=PACKAGE_VERSION)
            text = (Path(tmp) / "cr" / "08-agent-input.md").read_text().lower()
        for vendor in ("openai", "gpt", "claude", "anthropic", "gemini", "copilot"):
            self.assertNotIn(vendor, text, vendor)
        self.assertIn("review agent", text)


class DeterminismAndSafetyTests(unittest.TestCase):
    def test_deterministic_ignoring_timestamp(self) -> None:
        for fixture in FIXTURES:
            rm1, s1 = surfaces(fixture)
            rm2, s2 = surfaces(fixture)
            for builder in (build_evidence_graph, build_interaction_matrix, build_unresolved_map):
                a = builder(rm1, s1, package_version=PACKAGE_VERSION)
                b = builder(rm2, s2, package_version=PACKAGE_VERSION)
                a.pop("generated_at", None)
                b.pop("generated_at", None)
                self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True),
                                 f"{fixture.name}:{builder.__name__}")

    def test_no_unsafe_claims(self) -> None:
        for fixture in FIXTURES:
            rm, surf = surfaces(fixture)
            for data in (build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION),
                         build_interaction_matrix(rm, surf, package_version=PACKAGE_VERSION),
                         build_unresolved_map(rm, surf, package_version=PACKAGE_VERSION)):
                blob = json.dumps(data).lower()
                for phrase in FORBIDDEN:
                    self.assertNotIn(phrase, blob, f"{fixture.name}: forbidden {phrase!r}")
                self.assertTrue(data["safety"]["human_review_required"])

    def test_no_rpc_or_live_chain_outside_boundary(self) -> None:
        rm, surf = surfaces(PRIMARY)
        data = build_evidence_graph(rm, surf, package_version=PACKAGE_VERSION)
        body = dict(data)
        body.pop("safety")
        blob = json.dumps(body).lower()
        for term in ("rpc", "live-chain", "private key"):
            self.assertNotIn(term, blob, f"{term} leaked outside the safety boundary")


if __name__ == "__main__":
    unittest.main()
