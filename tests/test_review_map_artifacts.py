"""Protocol Review Map artifact tests (no ANSI, parseable, complete)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import (
    build_review_map,
    build_test_gap_map,
    default_out_dir,
    render_test_gap_map_md,
    write_artifacts,
)
from arkheionx.review_map.model import priority_rank
from arkheionx.review_map.tests import _scenario_kind

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "arkheionx" / "demo" / "fixtures"
ANSI = re.compile(r"\x1b\[")

ARTIFACTS = [
    "review-map.json", "review-map.md", "value-paths.json", "test-gaps.json",
    "assumptions.json", "proof-plan.json", "evidence-links.json",
    "review-summary.md", "review-map.mmd",
    "test-gap-map.json", "test-gap-map.md",
]
JSON_ARTIFACTS = [a for a in ARTIFACTS if a.endswith(".json")]


class ReviewMapArtifactTests(unittest.TestCase):
    def _write(self, demo: str, out: Path) -> dict:
        rm = build_review_map(FIXTURES / demo, top=10)
        return write_artifacts(rm, out)

    def test_all_artifacts_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("oracle-staking", out)
            for name in ARTIFACTS:
                self.assertTrue((out / name).is_file(), name)

    def test_no_ansi_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("amm-swap", out)
            for name in ARTIFACTS:
                text = (out / name).read_text(encoding="utf-8")
                self.assertNotRegex(text, ANSI, name)

    def test_json_artifacts_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("lending-vault", out)
            for name in JSON_ARTIFACTS:
                json.loads((out / name).read_text(encoding="utf-8"))

    def test_subset_files_have_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("lending-vault", out)
            for name in ("value-paths.json", "test-gaps.json", "assumptions.json",
                         "proof-plan.json", "evidence-links.json"):
                data = json.loads((out / name).read_text(encoding="utf-8"))
                self.assertEqual(data["schema_version"], "1.0.0")
                self.assertIn("generated_at", data)

    def test_markdown_has_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("oracle-staking", out)
            md = (out / "review-map.md").read_text(encoding="utf-8")
            for section in ("# Protocol Review Map", "## Summary", "## Value Paths",
                            "## Assumptions", "## Test Gaps", "## Proof Suggestions",
                            "## Evidence Links", "## Safety Boundaries", "## Next Steps"):
                self.assertIn(section, md)
            # No overclaiming wording in the human artifact.
            lowered = md.lower()
            for forbidden in ("critical vulnerability", "bounty-ready", "guaranteed"):
                self.assertNotIn(forbidden, lowered)

    def test_function_paths_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("amm-swap", out)
            data = json.loads((out / "review-map.json").read_text(encoding="utf-8"))
            for fn in data["functions"]:
                self.assertFalse(Path(fn["path"]).is_absolute(), fn["path"])

    def test_mermaid_is_flowchart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("amm-swap", out)
            mmd = (out / "review-map.mmd").read_text(encoding="utf-8")
            self.assertTrue(mmd.strip().startswith("flowchart"))

    def test_exact_artifact_filename_set(self) -> None:
        # Locks the written file set: no missing and no unexpected artifacts.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            written = self._write("oracle-staking", out)
            self.assertEqual(set(written), set(ARTIFACTS))
            self.assertEqual({p.name for p in out.iterdir()}, set(ARTIFACTS))

    def test_default_out_dir_unchanged(self) -> None:
        repo = Path("/tmp/example-repo")
        self.assertEqual(default_out_dir(repo), repo / ".arkheionx" / "out" / "review-map")

    def test_no_carriage_returns_in_artifacts(self) -> None:
        # Spinner remnants (carriage returns) must never reach written files.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self._write("lending-vault", out)
            for name in ARTIFACTS:
                self.assertNotIn("\r", (out / name).read_text(encoding="utf-8"), name)


class TestGapMapTests(unittest.TestCase):
    """Test Gap Map is a deterministic, derived view of the existing ReviewMap."""

    def _map(self, demo: str):
        rm = build_review_map(FIXTURES / demo, top=10)
        return rm, build_test_gap_map(rm)

    def test_top_level_shape_and_mode(self) -> None:
        rm, data = self._map("lending-vault")
        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertEqual(data["mode"], rm.mode)
        self.assertIn("summary", data)
        self.assertIsInstance(data["items"], list)

    def test_summary_counts_match_items(self) -> None:
        _rm, data = self._map("lending-vault")
        s, items = data["summary"], data["items"]
        self.assertEqual(s["total_test_gaps"], len(items))
        self.assertEqual(s["high_priority"] + s["medium_priority"] + s["low_priority"], len(items))
        self.assertEqual(s["with_evidence"] + s["missing_evidence"], len(items))
        self.assertEqual(s["with_proof_suggestions"], sum(1 for it in items if it["proof_suggestion"]["available"]))

    def test_items_derive_from_review_map(self) -> None:
        rm, data = self._map("lending-vault")
        gap_ids = {g.id for g in rm.test_gaps}
        fs_by_id = {fs.display_id: fs for fs in rm.functions}
        vp_ids = {vp.id for vp in rm.value_paths}
        asm_ids = {a.id for a in rm.assumptions}
        proofs = {p.id: p for p in rm.proof_suggestions}
        for it in data["items"]:
            self.assertIn(it["id"], gap_ids)
            fs = fs_by_id[it["target"]]
            self.assertEqual(it["priority"], fs.review_priority)
            self.assertEqual(it["category"], _scenario_kind(fs) or "")
            self.assertLessEqual(set(it["related_value_paths"]), vp_ids)
            self.assertLessEqual(set(it["related_assumptions"]), asm_ids)
            if it["proof_suggestion"]["available"]:
                self.assertIn(it["proof_suggestion"]["id"], proofs)
                self.assertEqual(proofs[it["proof_suggestion"]["id"]].related_test_gap, it["id"])

    def test_priority_values_are_valid_and_not_severity(self) -> None:
        _rm, data = self._map("amm-swap")
        for it in data["items"]:
            self.assertIn(it["priority"], ("high", "medium", "low"))

    def test_fresh_demo_has_no_evidence(self) -> None:
        _rm, data = self._map("oracle-staking")
        for it in data["items"]:
            self.assertEqual(it["evidence_status"], "missing")
            self.assertEqual(it["evidence"]["links"], [])

    def test_deterministic(self) -> None:
        rm = build_review_map(FIXTURES / "lending-vault", top=10)
        self.assertEqual(build_test_gap_map(rm), build_test_gap_map(rm))
        a = build_test_gap_map(build_review_map(FIXTURES / "amm-swap", top=10))
        b = build_test_gap_map(build_review_map(FIXTURES / "amm-swap", top=10))
        self.assertEqual(a["items"], b["items"])

    def test_indexes_sequential_and_priority_sorted(self) -> None:
        _rm, data = self._map("lending-vault")
        self.assertEqual([it["index"] for it in data["items"]], list(range(1, len(data["items"]) + 1)))
        ranks = [priority_rank(it["priority"]) for it in data["items"]]
        self.assertEqual(ranks, sorted(ranks))

    def test_markdown_sections_and_wording(self) -> None:
        _rm, data = self._map("lending-vault")
        md = render_test_gap_map_md(data)
        for section in ("# Test Gap Map", "## Summary", "## Review First", "## Test Gap Details", "## Boundary"):
            self.assertIn(section, md)
        self.assertIn("Human review required", md)
        self.assertIn("- Source:", md)
        self.assertTrue(md.endswith("\n"))
        lowered = md.lower()
        for forbidden in ("severity", "exploitability", "confirmed vulnerability",
                          "bounty", "guaranteed", "critical vulnerability"):
            self.assertNotIn(forbidden, lowered)

    def test_items_carry_source_location(self) -> None:
        rm, data = self._map("lending-vault")
        fs_by_id = {fs.display_id: fs for fs in rm.functions}
        for it in data["items"]:
            source = it.get("source")
            self.assertIsInstance(source, dict)
            fs = fs_by_id[it["target"]]
            self.assertEqual(source.get("path"), fs.path)
            self.assertEqual(source.get("line"), fs.line)
            self.assertFalse(Path(source["path"]).is_absolute(), source["path"])


if __name__ == "__main__":
    unittest.main()
