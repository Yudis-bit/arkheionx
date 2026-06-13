"""Safety-boundary tests for `arkheionx triage`."""
import json
import unittest
from pathlib import Path

from arkheionx.senior_triage import models as M
from arkheionx.senior_triage.pack import build_senior_triage_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "senior_triage_toy"

# Uppercase outcome-status tokens senior triage must never emit.
FORBIDDEN_TOKENS = [
    "VALID_BUG", "CONFIRMED_VULNERABILITY", "SUBMIT_NOW",
    "GUARANTEED_HIGH", "GUARANTEED_CRITICAL", "EXPLOIT_READY",
]
# Affirmative claim phrases that must never appear, even in prose. (The negated
# safety disclaimer "not a confirmed vulnerability" is allowed and expected.)
FORBIDDEN_PHRASES = [
    "submit now", "guaranteed payout", "guaranteed severity",
    "guaranteed high", "guaranteed critical",
]

SECRET = "KEYabc123SUPERSECRET"
ENDPOINT = f"https://node.example.com/v3/{SECRET}"


def build(**kw):
    defaults = dict(
        scope_file=str(FIXTURE / "scope.md"),
        known_path=str(FIXTURE / "known"),
        audits_path=str(FIXTURE / "audits"),
        addresses_file=str(FIXTURE / "addresses.json"),
        write=False,
    )
    defaults.update(kw)
    return build_senior_triage_pack(FIXTURE, **defaults)


def all_text(result) -> str:
    return "\n".join(result["contents"].values()) + json.dumps(result["triage"]) + json.dumps(result["manifest"])


class SafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()
        cls.blob = all_text(cls.result)
        cls.low = cls.blob.lower()

    def test_no_forbidden_outcome_terms(self) -> None:
        # Uppercase status tokens must never appear at all.
        for token in FORBIDDEN_TOKENS:
            self.assertNotIn(token, self.blob, f"forbidden token leaked: {token}")
        # Affirmative claim phrases must never appear.
        for phrase in FORBIDDEN_PHRASES:
            self.assertNotIn(phrase, self.low, f"forbidden claim leaked: {phrase}")

    def test_confirmed_vulnerability_only_appears_negated(self) -> None:
        # "confirmed vulnerability" may appear only inside the negated boundary line.
        sanitized = self.low.replace("not a confirmed vulnerability", "")
        self.assertNotIn("confirmed vulnerability", sanitized)

    def test_agent_brief_has_required_lines(self) -> None:
        brief = self.result["contents"]["09-agent-brief.md"]
        self.assertIn("Do not claim vulnerabilities.", brief)
        self.assertIn("Do not submit", brief)
        self.assertIn("NO_CLEAN_CANDIDATE", brief)

    def test_no_rpc_by_default(self) -> None:
        triage = self.result["triage"]
        self.assertEqual(triage["rpc_mode"], "not_provided")
        self.assertFalse(triage["rpc_enabled"])
        # No addresses-less RPC check; deployment is a static plan at most.
        self.assertNotEqual(triage["deployment_reality"]["status"], M.DEPLOY_RPC_READ_ONLY_CHECKED)

    def test_safety_flags_and_human_review(self) -> None:
        flags = self.result["triage"]["safety_flags"]
        for flag in ("no_rpc_by_default", "no_live_chain", "no_exploit_automation",
                     "no_auto_submit", "no_vulnerability_claims", "no_severity_claims",
                     "human_review_required"):
            self.assertTrue(flags[flag], flag)
        self.assertTrue(self.result["triage"]["human_review_required"])
        self.assertTrue(self.result["manifest"]["no_remote_write"])

    def test_rpc_url_is_masked_and_secret_not_leaked(self) -> None:
        result = build(rpc_endpoint=ENDPOINT)
        blob = all_text(result)
        self.assertNotIn(SECRET, blob)
        self.assertNotIn(ENDPOINT, blob)
        self.assertIn("***masked***", result["triage"]["rpc_endpoint_masked"])
        self.assertEqual(result["triage"]["rpc_mode"], "provided_not_run")
        self.assertFalse(result["triage"]["rpc_enabled"])
        # An endpoint was supplied but no live read was performed.
        self.assertEqual(
            result["triage"]["deployment_reality"]["status"], M.DEPLOY_NOT_IMPLEMENTED
        )

    def test_no_live_source_match_claimed_without_rpc(self) -> None:
        # Without a live read, triage never claims the deployed source matches.
        for status in (M.DEPLOY_LIVE_SOURCE_MATCH, M.DEPLOY_LIVE_SOURCE_MISMATCH):
            self.assertNotEqual(self.result["triage"]["deployment_reality"]["status"], status)

    def test_top_leads_never_ready_for_review_from_triage(self) -> None:
        # Triage alone cannot mark a lead READY_FOR_REVIEW (needs independent proof).
        for lead in self.result["triage"]["lead_scoreboard"]:
            self.assertNotEqual(lead["submit_readiness"], M.READY_FOR_REVIEW)


if __name__ == "__main__":
    unittest.main()
