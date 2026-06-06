import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TEXT_SUFFIXES = {".astro", ".css", ".json", ".mjs", ".md"}


def site_text() -> str:
    chunks = []
    for path in sorted(SITE.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if "node_modules" in path.parts or "dist" in path.parts:
            continue
        chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


class SiteCopySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = site_text()
        cls.lower = cls.text.lower()

    def test_no_forbidden_product_or_application_language(self) -> None:
        forbidden = [
            "ai-powered",
            "revolutionary",
            "game-changing",
            "autonomous auditor",
            "guarantees security",
            "finds vulnerabilities automatically",
            "audit passed",
            "bounty eligible",
            "replace auditors",
            "investors",
            "founders",
            "pitch deck",
            "data room",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, self.lower, phrase)
        for term in ["yc", "a16z"]:
            self.assertIsNone(re.search(rf"\b{term}\b", self.lower), term)

    def test_no_positive_vulnerability_confirmation_claim(self) -> None:
        forbidden_patterns = [
            r"\bvulnerability confirmed\b",
            r"\bconfirmed vulnerabilit",
            r"\bconfirms? a vulnerabilit",
            r"\bwe confirm vulnerabilit",
        ]
        for line in self.lower.splitlines():
            if not any(re.search(pattern, line) for pattern in forbidden_patterns):
                continue
            self.assertTrue(
                any(marker in line for marker in ["does not", "cannot", "not ", "no "]),
                line,
            )

    def test_no_external_analytics_tracking_or_font_cdn(self) -> None:
        forbidden = [
            "google-analytics",
            "googletagmanager",
            "plausible.io",
            "posthog",
            "mixpanel",
            "segment.com",
            "fonts.googleapis.com",
            "fonts.gstatic.com",
            "use.typekit.net",
        ]
        for marker in forbidden:
            self.assertNotIn(marker, self.lower, marker)
        self.assertIsNone(re.search(r"<script[^>]+src=[\"']https?://", self.lower))
        self.assertIsNone(re.search(r"<link[^>]+href=[\"']https?://[^\"']+\.css", self.lower))

    def test_no_v390_tag_push_instruction(self) -> None:
        self.assertIsNone(re.search(r"git\s+push[^\n]*v3\.9\.0", self.lower))

    def test_required_safety_copy_is_present(self) -> None:
        for marker in [
            "does not confirm vulnerabilities",
            "assign final severity",
            "human review",
            "authorized",
            "no exploit automation",
        ]:
            self.assertIn(marker, self.lower)


if __name__ == "__main__":
    unittest.main()
