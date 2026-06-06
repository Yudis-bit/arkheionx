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
        "proof_receipt_id": f"proof:{slug}",
        "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
        "review_map_target": "OracleRewardFixture.stake",
        "evidence_level": level,
        "status": status,
        "foundry": {"test_command": "forge test --match-test (?i)stake -vvvv"},
        "test_result": {"tests_run": 1, "passed": 1, "failed": 0, "skipped": 0,
                        "failed_tests": [], "skipped_tests": [], "raw_output_path": "x.txt"},
        "generated_files": [f"proof/{slug}/generated-test.sol"],
    }
    writer.write_text(f"proof/{slug}/proof.json", json.dumps(proof))
    if with_trace:
        writer.write_text(f"proof/{slug}/trace.json", json.dumps({
            "trace_receipt_id": f"trace:{slug}",
            "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
            "review_map_target": "OracleRewardFixture.stake",
            "evidence_level": level,
            "status": status,
            "reverts": [],
            "call_sequence": ["A::b()"],
            "assertion_failures": [],
            "logs": [],
        }))


def _proof_payload(level: str = "EXECUTION_CONFIRMED", status: str = "tested_passed") -> dict:
    return {
        "proof_receipt_id": "proof:OracleRewardFixture_stake",
        "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
        "review_map_target": "OracleRewardFixture.stake",
        "evidence_level": level,
        "status": status,
        "foundry": {"test_command": "forge test --match-test (?i)stake -vvvv"},
        "test_result": {
            "tests_run": 1,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "failed_tests": [],
            "skipped_tests": [],
            "raw_output_path": "x.txt",
        },
        "generated_files": ["proof/OracleRewardFixture_stake/generated-test.sol"],
    }


def _trace_payload(level: str = "EXECUTION_CONFIRMED", status: str = "tested_passed") -> dict:
    return {
        "trace_receipt_id": "trace:OracleRewardFixture_stake",
        "target_id": "src/OracleRewardFixture.sol:OracleRewardFixture.stake(uint256)#L86-L92",
        "review_map_target": "OracleRewardFixture.stake",
        "evidence_level": level,
        "status": status,
        "source_proof_json": "",
        "reverts": [],
        "assertion_failures": [],
        "call_sequence": ["OracleRewardFixture::stake(uint256)"],
        "logs": [],
    }


def _source(manifest: dict, kind: str) -> dict:
    return next(item for item in manifest["sources"] if item["kind"] == kind)


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

    def test_evidence_package_id_is_deterministic_for_same_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "EXECUTION_CONFIRMED", "tested_passed", with_trace=True)
            first = build_evidence(match, FIXTURE, writer, analysis)
            second = build_evidence(match, FIXTURE, writer, analysis)
            self.assertEqual(first.payload["evidence_package_id"], second.payload["evidence_package_id"])
            self.assertEqual(first.payload["manifest"]["package_id"], first.payload["evidence_package_id"])
            self.assertTrue(first.payload["evidence_package_id"].startswith(f"evidence:{target_slug(match.display_id)}:"))
            self.assertNotIn(first.payload["generated_at"], first.payload["evidence_package_id"])

    def test_manifest_shape_for_evidence_ready_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            slug = target_slug(match.display_id)
            _write_proof(writer, slug, "EXECUTION_CONFIRMED", "tested_passed", with_trace=True)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            manifest = pkg.payload["manifest"]
            self.assertEqual(manifest["readiness"], "evidence_ready")
            self.assertEqual(manifest["source_count"], 2)
            self.assertTrue(manifest["checks"]["proof_linked"])
            self.assertTrue(manifest["checks"]["trace_linked"])
            self.assertTrue(manifest["checks"]["trace_required_for_evidence_ready"])
            self.assertTrue(manifest["checks"]["human_review_required"])
            proof_source = _source(manifest, "proof")
            trace_source = _source(manifest, "trace")
            self.assertEqual(proof_source["path"], str(writer.path_for(f"proof/{slug}/proof.json")))
            self.assertEqual(trace_source["path"], str(writer.path_for(f"proof/{slug}/trace.json")))
            self.assertTrue(proof_source["exists"])
            self.assertTrue(trace_source["exists"])
            self.assertEqual(proof_source["receipt_id"], f"proof:{slug}")
            self.assertEqual(trace_source["receipt_id"], f"trace:{slug}")

    def test_execution_without_trace_is_not_evidence_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            _write_proof(writer, target_slug(match.display_id), "EXECUTION_CONFIRMED", "tested_passed", with_trace=False)
            pkg = build_evidence(match, FIXTURE, writer, analysis)
            self.assertEqual(pkg.evidence_level, "EXECUTION_CONFIRMED")
            self.assertFalse(pkg.trace_found)
            self.assertEqual(pkg.payload["source_artifacts"]["trace_json"], "")
            self.assertEqual(pkg.payload["source_artifacts"]["trace_status"], "missing")
            self.assertEqual(pkg.payload["trace_summary"]["status"], "missing")
            manifest = pkg.payload["manifest"]
            self.assertEqual(manifest["readiness"], "execution_confirmed")
            self.assertFalse(manifest["checks"]["trace_linked"])
            self.assertTrue(manifest["checks"]["trace_required_for_evidence_ready"])
            self.assertEqual([source["kind"] for source in manifest["sources"]], ["proof"])
            self.assertIn("trace", pkg.next_command)

    def test_from_proof_override_does_not_fall_back_to_default_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            slug = target_slug(match.display_id)
            writer.write_text(
                f"proof/{slug}/trace.json",
                json.dumps({"reverts": [], "call_sequence": ["stale"], "assertion_failures": [], "logs": []}),
            )
            source = str((Path(tmp) / "external-proof.json").resolve())
            pkg = build_evidence(
                match,
                FIXTURE,
                writer,
                analysis,
                proof_override=_proof_payload(),
                trace_override=None,
                proof_source_path=source,
            )
            self.assertEqual(pkg.evidence_level, "EXECUTION_CONFIRMED")
            self.assertFalse(pkg.trace_found)
            self.assertEqual(pkg.payload["source_artifacts"]["proof_json"], source)
            self.assertEqual(pkg.payload["source_artifacts"]["trace_json"], "")
            self.assertEqual(_source(pkg.payload["manifest"], "proof")["path"], source)

    def test_manifest_records_external_trace_source_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            match, analysis = _match("stake")
            proof_source = str((Path(tmp) / "input" / "proof.json").resolve())
            trace_source = str((Path(tmp) / "input" / "trace.json").resolve())
            Path(proof_source).parent.mkdir(parents=True, exist_ok=True)
            Path(proof_source).write_text(json.dumps(_proof_payload()), encoding="utf-8")
            Path(trace_source).write_text(json.dumps(_trace_payload()), encoding="utf-8")
            pkg = build_evidence(
                match,
                FIXTURE,
                writer,
                analysis,
                proof_override=_proof_payload(),
                trace_override=_trace_payload(),
                proof_source_path=proof_source,
                trace_source_path=trace_source,
            )
            manifest = pkg.payload["manifest"]
            self.assertEqual(pkg.evidence_level, "EVIDENCE_READY")
            self.assertEqual(_source(manifest, "proof")["path"], proof_source)
            self.assertEqual(_source(manifest, "trace")["path"], trace_source)
            self.assertEqual(pkg.payload["source_artifacts"]["proof_json"], proof_source)
            self.assertEqual(pkg.payload["source_artifacts"]["trace_json"], trace_source)

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
