import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.evidence.builder import build_evidence
from arkheionx.evidence.render import render_evidence
from arkheionx.proof.payloads import target_slug
from arkheionx.protocol.detector import analyze

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"
SCHEMA = json.loads((REPO_ROOT / "schemas" / "evidence.schema.json").read_text(encoding="utf-8"))


def _match(name: str):
    analysis = analyze(FIXTURE)
    fr = next(f for f in analysis.all_functions if f.function_name == name)
    return fr, analysis


def _write_proof(writer: ArtifactWriter, slug: str, level: str, status: str, with_trace: bool) -> None:
    proof = {
        "evidence_level": level,
        "status": status,
        "foundry": {"test_command": "forge test --match-test (?i)stake -vvvv"},
        "test_result": {"tests_run": 1, "passed": 1, "failed": 0, "skipped": 0,
                        "failed_tests": [], "skipped_tests": [], "raw_output_path": "x.txt"},
        "generated_files": [f"proof/{slug}/generated-test.sol"],
    }
    writer.write_text(f"proof/{slug}/proof.json", json.dumps(proof))
    if with_trace:
        writer.write_text(f"proof/{slug}/trace.json", json.dumps({"reverts": [], "call_sequence": ["A::b()"], "assertion_failures": [], "logs": []}))


class EvidenceTests(unittest.TestCase):
    def test_no_proof_gives_next_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            match, analysis = _match("claimReward")
            pkg = build_evidence(match, FIXTURE, ArtifactWriter(Path(tmp)), analysis)
            self.assertEqual(pkg.status, "no_proof")
            self.assertEqual(pkg.evidence_level, "HEURISTIC")
            self.assertIn("prove", pkg.next_command)
            self.assertIn("--run", pkg.next_command)

    def test_evidence_ready_when_execution_and_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "EXECUTION_CONFIRMED", "tested_passed", with_trace=True)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            self.assertEqual(pkg.evidence_level, "EVIDENCE_READY")
            self.assertTrue(Path(pkg.json_path).exists())
            self.assertTrue(Path(pkg.text_path).exists())
            self.assertIn("report", pkg.next_command)

    def test_execution_without_trace_is_not_evidence_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "EXECUTION_CONFIRMED", "tested_passed", with_trace=False)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            self.assertEqual(pkg.evidence_level, "EXECUTION_CONFIRMED")

    def test_compiler_only_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "COMPILER_CONFIRMED", "no_tests_matched", with_trace=False)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            self.assertEqual(pkg.evidence_level, "COMPILER_CONFIRMED")
            self.assertEqual(pkg.status, "compiler_confirmed_only")

    def test_evidence_payload_schema_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "EXECUTION_CONFIRMED", "tested_passed", with_trace=True)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            for key in SCHEMA["required"]:
                self.assertIn(key, pkg.payload)
            self.assertIn("candidate_impact", pkg.payload["impact_notes"])

    def test_render_is_compact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "EXECUTION_CONFIRMED", "tested_passed", with_trace=True)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            text = render_evidence(pkg, ".")
            self.assertIn("ARKHEIONX EVIDENCE", text)
            self.assertIn("Severity is not final", text)
            self.assertLessEqual(len(text.splitlines()), 30)


if __name__ == "__main__":
    unittest.main()
