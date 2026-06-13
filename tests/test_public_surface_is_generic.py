"""Guard: the current public surface must stay generic and non-target-specific.

Fails if the current public surface (README, docs, site source, the CLI and
protocol-lens packages, schemas, the v8 release notes, and packaging metadata)
contains a forbidden target-specific name or a misleading positive marketing claim.

Negative boundary phrases are allowed: "not an AI auditor" is fine; "Arkheionx is
an AI auditor" is not. Historical changelog/release notes for older versions are
intentionally out of scope so history is not distorted.
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Forbidden target-specific names: must never appear on the current public surface.
HARD_FORBIDDEN = [
    re.compile(r"morpho", re.IGNORECASE),
    re.compile(r"midnight", re.IGNORECASE),
    re.compile(r"\bdre\b", re.IGNORECASE),
]

# Misleading positive claims. Allowed only in a negated/boundary phrasing.
MARKETING_PHRASES = [
    "ai auditor",
    "automatic auditor",
    "guaranteed bug",
    "exploit scanner",
    "exploit generator",
    "severity engine",
    "instant exploit",
    "auto-submit",
]
NEGATION_MARKERS = ("no ", "not ", "never", "n't", "without", "does not", "do not",
                    "cannot", "can't", "no auto", "isn't", "won't", "neither")


def _scanned_files() -> list[Path]:
    files: list[Path] = [REPO_ROOT / "README.md", REPO_ROOT / "pyproject.toml",
                         REPO_ROOT / "release-notes" / "v8.0.0.md"]
    files += sorted((REPO_ROOT / "docs").rglob("*.md"))
    files += sorted((REPO_ROOT / "site" / "src").rglob("*.astro"))
    files += sorted((REPO_ROOT / "site" / "src").rglob("*.ts"))
    for pkg in ("cli", "protocol_lens", "review_pack"):
        files += sorted((REPO_ROOT / "arkheionx" / pkg).rglob("*.py"))
    files += sorted((REPO_ROOT / "schemas").glob("*.json"))
    return [f for f in files if f.exists() and "__pycache__" not in f.parts]


def _non_negated_hit(text: str, phrase: str) -> bool:
    low = text.lower()
    start = 0
    while True:
        idx = low.find(phrase, start)
        if idx == -1:
            return False
        window = re.sub(r"[^a-z0-9]+", " ", low[max(0, idx - 48):idx])
        if not any(marker in window for marker in NEGATION_MARKERS):
            return True
        start = idx + len(phrase)


class PublicSurfaceIsGenericTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = _scanned_files()
        assert cls.files, "no public-surface files found to scan"

    def test_files_scanned(self) -> None:
        # Sanity: the scan actually covers the key current-surface files.
        names = {f.name for f in self.files}
        self.assertIn("README.md", names)
        self.assertIn("pyproject.toml", names)
        self.assertIn("v8.0.0.md", names)
        self.assertIn("fixed_credit_market.py", names)

    def test_no_target_specific_names(self) -> None:
        offenders: list[str] = []
        for path in self.files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in HARD_FORBIDDEN:
                for m in pattern.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{line} -> {m.group(0)!r}")
        self.assertEqual(offenders, [], "target-specific names on the public surface:\n" + "\n".join(offenders))

    def test_no_unnegated_marketing_claims(self) -> None:
        offenders: list[str] = []
        for path in self.files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in MARKETING_PHRASES:
                if _non_negated_hit(text, phrase):
                    offenders.append(f"{path.relative_to(REPO_ROOT)} -> {phrase!r}")
        self.assertEqual(offenders, [], "non-negated marketing claims on the public surface:\n" + "\n".join(offenders))

    def test_fixed_credit_market_is_the_lens_identity(self) -> None:
        # The generic lens identity must be the one present.
        lens = (REPO_ROOT / "arkheionx" / "protocol_lens" / "lenses" / "fixed_credit_market.py").read_text(encoding="utf-8")
        self.assertIn('LENS_ID = "fixed-credit-market"', lens)
        self.assertIn("FixedCreditMarketLens", lens)


if __name__ == "__main__":
    unittest.main()
