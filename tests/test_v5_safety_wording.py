"""Safety-wording tests for the v5 Blind Spot Intelligence outputs.

Asserts the v5 commands never claim a bug or a severity, always require human
review, and use the correct heuristic framing ("likely blind spots", "criticality
potential", "review priority", "research prompts").
"""
import json
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTH = REPO_ROOT / "examples" / "periphery-auth-fixture"

# Claims that must never appear in any v5 output.
FORBIDDEN_CLAIMS = (
    "critical found", "high found", "vulnerability confirmed", "confirmed vulnerability",
    "exploit generated", "guaranteed", "audit replacement", "proof of safety",
    "bug found", "bounty eligible",
)


def run_cli(*args: str, color: str = "never"):
    import subprocess
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class V5HumanOutputSafetyTests(unittest.TestCase):
    def _human(self, cmd: str) -> str:
        result = run_cli(cmd, str(AUTH), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result.stdout

    def test_all_v5_commands_require_human_review(self) -> None:
        for cmd in ("blind-spots", "criticality-map", "counterfactuals"):
            self.assertIn("Human review required", self._human(cmd), cmd)

    def test_no_forbidden_claims(self) -> None:
        for cmd in ("blind-spots", "criticality-map", "counterfactuals"):
            out = self._human(cmd).lower()
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, out, f"{cmd}: {phrase}")

    def test_blind_spots_uses_heuristic_framing(self) -> None:
        out = self._human("blind-spots").lower()
        self.assertIn("blind spot", out)
        self.assertIn("criticality potential is not severity", out)

    def test_criticality_is_not_severity(self) -> None:
        out = self._human("criticality-map").lower()
        self.assertIn("criticality potential", out)
        self.assertIn("not severity", out)
        self.assertNotIn('"severity"', out)

    def test_counterfactuals_are_research_prompts(self) -> None:
        out = self._human("counterfactuals").lower()
        self.assertIn("research prompts", out)
        self.assertIn("not findings", out)


class V5JsonSafetyTests(unittest.TestCase):
    def test_json_outputs_carry_safety_and_no_severity(self) -> None:
        for cmd in ("blind-spots", "criticality-map", "counterfactuals"):
            payload = json.loads(run_cli(cmd, str(AUTH), "--json", "--no-write").stdout)
            self.assertTrue(payload["safety"]["human_review_required"], cmd)
            blob = json.dumps(payload).lower()
            self.assertNotIn('"severity"', blob, cmd)
            self.assertNotIn("severity:", blob, cmd)
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, blob, f"{cmd}: {phrase}")

    def test_blind_spot_score_not_labelled_severity_or_probability(self) -> None:
        payload = json.loads(run_cli("blind-spots", str(AUTH), "--json", "--no-write").stdout)
        note = payload["scoring"]["note"].lower()
        self.assertIn("not a severity", note)
        self.assertIn("not a probability", note)

    def test_no_rpc_or_live_chain_outside_boundary(self) -> None:
        # RPC / live-chain words may only appear inside the safety boundary/disclaimer.
        payload = json.loads(run_cli("blind-spots", str(AUTH), "--json", "--no-write").stdout)
        safety_blob = json.dumps(payload["safety"]).lower()
        self.assertIn("no rpc", safety_blob)
        body = dict(payload)
        body.pop("safety")
        body_blob = json.dumps(body).lower()
        for term in ("rpc", "live-chain", "private key"):
            self.assertNotIn(term, body_blob, f"{term} leaked outside the safety boundary")


if __name__ == "__main__":
    unittest.main()
