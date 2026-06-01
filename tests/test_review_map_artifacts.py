"""Protocol Review Map artifact tests (no ANSI, parseable, complete)."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map, write_artifacts

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "arkheionx" / "demo" / "fixtures"
ANSI = re.compile(r"\x1b\[")

ARTIFACTS = [
    "review-map.json", "review-map.md", "value-paths.json", "test-gaps.json",
    "assumptions.json", "proof-plan.json", "evidence-links.json",
    "review-summary.md", "review-map.mmd",
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


if __name__ == "__main__":
    unittest.main()
