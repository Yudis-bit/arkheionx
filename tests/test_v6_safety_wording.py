"""Safety-wording tests for the v6 Evidence Graph outputs.

Asserts the v6 commands never claim a bug or a severity, always require human
review, and use the correct framing: evidence state is not a vulnerability claim,
interaction priority is not severity, confirmed-candidate is not a confirmed
vulnerability, and unresolved does not mean vulnerable.
"""
import json
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "blind-spot-fixture"

FORBIDDEN_CLAIMS = (
    "critical found", "high found", "vulnerability confirmed", "exploit generated",
    "guaranteed", "audit replacement", "proof of safety", "bug found", "bounty eligible",
    "protocol is safe",
)

V6_COMMANDS = ("evidence-graph", "interaction-matrix", "unresolved-map")


def run_cli(*args: str, color: str = "never"):
    import subprocess
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = color
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class V6HumanOutputSafetyTests(unittest.TestCase):
    def _human(self, cmd: str) -> str:
        result = run_cli(cmd, str(FIXTURE), "--no-write")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result.stdout

    def test_all_v6_commands_require_human_review(self) -> None:
        for cmd in V6_COMMANDS:
            self.assertIn("Human review required", self._human(cmd), cmd)
        # complete-review writes by default; use --no-write for human text.
        result = run_cli("complete-review", str(FIXTURE), "--no-write")
        self.assertIn("Human review required", result.stdout)

    def test_no_forbidden_claims(self) -> None:
        for cmd in V6_COMMANDS:
            out = self._human(cmd).lower()
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, out, f"{cmd}: {phrase}")

    def test_evidence_graph_framing(self) -> None:
        out = self._human("evidence-graph").lower()
        self.assertIn("evidence state is not a vulnerability claim", out)
        self.assertIn("unresolved does not mean vulnerable", out)

    def test_interaction_matrix_framing(self) -> None:
        out = self._human("interaction-matrix").lower()
        self.assertIn("interaction priority is not severity", out)
        self.assertNotIn('"severity"', out)

    def test_unresolved_map_framing(self) -> None:
        out = self._human("unresolved-map").lower()
        self.assertIn("unresolved does not mean vulnerable", out)


class V6JsonSafetyTests(unittest.TestCase):
    def test_json_outputs_carry_safety_and_no_severity(self) -> None:
        for cmd in V6_COMMANDS:
            payload = json.loads(run_cli(cmd, str(FIXTURE), "--json", "--no-write").stdout)
            self.assertTrue(payload["safety"]["human_review_required"], cmd)
            self.assertTrue(payload["human_review_required"], cmd)
            blob = json.dumps(payload).lower()
            self.assertNotIn('"severity"', blob, cmd)
            self.assertNotIn("severity:", blob, cmd)
            for phrase in FORBIDDEN_CLAIMS:
                self.assertNotIn(phrase, blob, f"{cmd}: {phrase}")

    def test_confirmed_candidate_is_not_confirmed_vulnerability(self) -> None:
        payload = json.loads(run_cli("evidence-graph", str(FIXTURE), "--json", "--no-write").stdout)
        # Boundary explicitly distinguishes confirmed-candidate from a confirmed bug.
        boundary = " ".join(payload["safety"]["boundary"]).lower()
        self.assertIn("confirmed-candidate is not a confirmed vulnerability", boundary)

    def test_no_rpc_or_live_chain_outside_boundary(self) -> None:
        for cmd in V6_COMMANDS:
            payload = json.loads(run_cli(cmd, str(FIXTURE), "--json", "--no-write").stdout)
            safety_blob = json.dumps(payload["safety"]).lower()
            self.assertIn("no rpc", safety_blob, cmd)
            body = dict(payload)
            body.pop("safety")
            body_blob = json.dumps(body).lower()
            for term in ("rpc", "live-chain", "private key"):
                self.assertNotIn(term, body_blob, f"{cmd}: {term} leaked outside the safety boundary")


if __name__ == "__main__":
    unittest.main()
