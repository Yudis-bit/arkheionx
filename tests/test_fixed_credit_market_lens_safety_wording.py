"""Safety-wording tests for the v7.5 protocol-lens artifacts.

Generated artifacts must never claim a vulnerability or a severity, must not name
any AI vendor, and must restate that human review is required. The package source
must not name any AI vendor either.
"""
import tempfile
import unittest
from pathlib import Path

import arkheionx.protocol_lens as pl
from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "fixed_credit_market_toy"
SCOPE = str(FIXTURE / "scope.md")
PACKAGE_DIR = REPO_ROOT / "arkheionx" / "protocol_lens"

UNSAFE_PHRASES = [
    "critical found", "high found", "guaranteed", "vulnerability confirmed",
    "exploit generated", "audit replacement", "we found a bug", "confirmed exploit",
]
VENDOR_NAMES = ["claude", "openai", "gpt-4", "gemini", "anthropic", "codex", "copilot", " kiro "]


def _all_pack_text() -> str:
    lens = pl.get_lens("fixed-credit-market")
    rm = build_review_map(FIXTURE)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pack"
        res = pl.build_lens_pack(lens, rm, FIXTURE, SCOPE, out, write=True)
        pack = Path(res["out_dir"])
        return "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                         for p in pack.iterdir() if p.is_file())


class LensSafetyWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blob = _all_pack_text()
        cls.low = cls.blob.lower()

    def test_no_unsafe_claims(self) -> None:
        for phrase in UNSAFE_PHRASES:
            self.assertNotIn(phrase, self.low, f"unsafe phrase in pack: {phrase}")

    def test_no_severity_field_claim(self) -> None:
        self.assertNotIn('"severity":', self.low)

    def test_no_vendor_names_in_pack(self) -> None:
        for vendor in VENDOR_NAMES:
            self.assertNotIn(vendor, self.low, f"vendor name in pack: {vendor.strip()}")

    def test_no_absolute_repository_path_in_pack(self) -> None:
        self.assertNotIn(str(FIXTURE.resolve()).lower(), self.low)
        self.assertIn('"repo_path": "."', self.low)

    def test_required_disclaimers_present(self) -> None:
        self.assertIn("human review required", self.low)
        self.assertIn("planning artifact, not a finding", self.low)
        self.assertIn("evidence quality is not vulnerability validity", self.low)

    def test_package_source_has_no_vendor_names(self) -> None:
        for path in PACKAGE_DIR.rglob("*.py"):
            low = path.read_text(encoding="utf-8", errors="ignore").lower()
            for vendor in ("claude", "openai", "gemini", "anthropic", "codex", "copilot"):
                self.assertNotIn(vendor, low, f"{path.name} mentions {vendor}")


if __name__ == "__main__":
    unittest.main()
