"""Safety-wording tests for the v7 scope-orchestration artifacts.

Generated artifacts must never claim a vulnerability or a severity, must not name
any AI vendor, and must restate that human review is required.
"""
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
import arkheionx.scope_orchestration as so

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = str(FIXTURE / "scope-note.md")

UNSAFE_PHRASES = [
    "critical found", "high found", "guaranteed", "vulnerability confirmed",
    "exploit generated", "audit replacement", "we found a bug", "confirmed exploit",
]
VENDOR_NAMES = ["claude", "openai", "gpt-4", "gemini", "anthropic", "codex", "copilot", " kiro "]
PACKAGE_DIR = REPO_ROOT / "arkheionx" / "scope_orchestration"


def _all_pack_text() -> str:
    rm = build_review_map(FIXTURE)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pack"
        so.build_scope_pack(rm, FIXTURE, SCOPE, out, write=True)
        return "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                         for p in out.iterdir() if p.is_file())


class V7SafetyWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blob = _all_pack_text()
        cls.low = cls.blob.lower()

    def test_no_unsafe_claims(self) -> None:
        for phrase in UNSAFE_PHRASES:
            self.assertNotIn(phrase, self.low, f"unsafe phrase in pack: {phrase}")

    def test_no_severity_field_claim(self) -> None:
        self.assertNotIn('"severity"', self.low)

    def test_no_vendor_names_in_pack(self) -> None:
        for vendor in VENDOR_NAMES:
            self.assertNotIn(vendor, self.low, f"vendor name in pack: {vendor.strip()}")

    def test_no_absolute_repository_path_in_pack(self) -> None:
        self.assertNotIn(str(FIXTURE.resolve()).lower(), self.low)
        self.assertIn('"repo_path": "."', self.low)

    def test_required_disclaimers_present(self) -> None:
        self.assertIn("human review", self.low)
        self.assertIn("not a finding", self.low)
        self.assertIn("candidate-with-evidence is not a confirmed vulnerability", self.low)

    def test_package_source_has_no_vendor_names(self) -> None:
        for path in PACKAGE_DIR.rglob("*.py"):
            low = path.read_text(encoding="utf-8", errors="ignore").lower()
            for vendor in ("claude", "openai", "gemini", "anthropic", "codex", "copilot"):
                self.assertNotIn(vendor, low, f"{path.name} mentions {vendor}")


if __name__ == "__main__":
    unittest.main()
