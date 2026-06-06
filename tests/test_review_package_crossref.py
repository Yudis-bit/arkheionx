"""Tests for package-level cross-reference validation (v3.6, internal)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_package import crossref as cr
from arkheionx.review_package import manifest as mf

_MODEL = {
    "protocol_id": "protocol:abc",
    "contracts": [{"contract_id": "contract:c1:vault", "aliases": {"name": "Vault"}}],
    "functions": [{"function_id": "function:vault:f1", "aliases": {"display_name": "Vault.borrow"}}],
    "value_paths": [], "assumptions": [], "test_gaps": [], "proof_suggestions": [],
    "proof_receipts": [{"proof_receipt_id": "proof-receipt:p1"}],
    "trace_receipts": [{"trace_receipt_id": "trace-receipt:t1"}],
    "evidence_packages": [{"evidence_package_id": "evidence:e1"}],
    "report_drafts": [{"report_id": "report:r1"}],
    "evidence_links": [{"evidence_link_id": "evidence-link:proof:f1",
                        "evidence_package_id": "evidence:linklevel", "report_id": ""}],
}


class ExtractTests(unittest.TestCase):
    def test_extract_protocol_model_ids(self) -> None:
        ids = cr.extract_protocol_model_ids(_MODEL)
        self.assertIn("function:vault:f1", ids["function"])
        self.assertIn("contract:c1:vault", ids["contract"])
        self.assertIn("proof-receipt:p1", ids["proof_receipt"])
        self.assertIn("trace-receipt:t1", ids["trace_receipt"])
        self.assertIn("evidence:e1", ids["evidence_package"])
        self.assertIn("evidence:linklevel", ids["evidence_package"])  # folded from evidence_links
        self.assertIn("report:r1", ids["report"])
        self.assertIn("evidence-link:proof:f1", ids["evidence_link"])
        self.assertIn("Vault.borrow", ids["alias"])
        self.assertIn("Vault", ids["alias"])

    def test_extract_artifact_references(self) -> None:
        payload = {"functions": [{"function_id": "function:vault:f1"}],
                   "nested": {"proof_receipt_id": "proof-receipt:p1", "target_function_id": "function:x:y"}}
        refs = cr.extract_artifact_references(payload)
        self.assertIn("function:vault:f1", refs["function_id"])
        self.assertIn("proof-receipt:p1", refs["proof_receipt_id"])
        self.assertIn("function:x:y", refs["target_function_id"])

    def test_load_json_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "a.json"
            good.write_text('{"x": 1}')
            self.assertEqual(cr.load_json_artifact(good), {"x": 1})
            bad = Path(tmp) / "b.json"
            bad.write_text("{not json")
            self.assertIsNone(cr.load_json_artifact(bad))
            arr = Path(tmp) / "c.json"
            arr.write_text("[1,2]")
            self.assertIsNone(cr.load_json_artifact(arr))


def _pkg_with(tmp: str, artifact_payloads: dict) -> tuple:
    """Seed a review-map artifact set with given JSON payloads and build a manifest."""
    out = Path(tmp) / ".arkheionx" / "out"
    (out / "review-map").mkdir(parents=True, exist_ok=True)
    for rel, payload in artifact_payloads.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload), encoding="utf-8")
    (out / "artifacts-index.json").write_text('{"targets": []}', encoding="utf-8")
    return mf.build_review_package_manifest(tmp), tmp


class ValidateCrossRefTests(unittest.TestCase):
    def test_missing_model_is_warning_not_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {"review-map/review-map.json": {}})
            checks = cr.validate_package_cross_references(manifest, tmp, None, None)
            self.assertEqual(len(checks), 1)
            self.assertEqual(checks[0]["status"], "WARN")
            self.assertTrue(all(c["severity"] != "error" for c in checks))

    def test_resolved_and_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {
                "review-map/review-map.json": {"functions": [{"function_id": "function:vault:f1"}]},
                "review-map/evidence-links.json": {"x": {"function_id": "function:not:inmodel"}},
            })
            checks = cr.validate_package_cross_references(manifest, tmp, None, _MODEL)
            statuses = {(c["kind"], c["status"]) for c in checks if c["name"] == "crossref.function"}
            self.assertIn(("function", "PASS"), statuses)
            self.assertIn(("function", "WARN"), statuses)
            self.assertTrue(all(c["severity"] != "error" for c in checks))

    def test_substring_and_similar_do_not_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {
                "review-map/review-map.json": {"a": {"function_id": "function:vault:f"},
                                               "b": {"function_id": "function:vault:f1x"}},
            })
            checks = cr.validate_package_cross_references(manifest, tmp, None, _MODEL)
            fn = [c for c in checks if c["name"] == "crossref.function"]
            self.assertTrue(fn)
            self.assertTrue(all(c["status"] == "WARN" for c in fn))  # neither substring nor similar resolves

    def test_alias_resolves_exact_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {
                "review-map/review-map.json": {"x": {"review_map_target": "Vault.borrow"},
                                               "y": {"target_id": "Vault.unknown"}},
            })
            checks = cr.validate_package_cross_references(manifest, tmp, None, _MODEL)
            alias = {(c["status"]) for c in checks if c["name"] == "crossref.alias"}
            self.assertIn("PASS", alias)  # Vault.borrow is an explicit alias
            self.assertIn("WARN", alias)  # Vault.unknown is not

    def test_deterministic_and_no_mutation_no_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {
                "review-map/review-map.json": {"functions": [{"function_id": "function:vault:f1"}]},
            })
            before = mf.manifest_to_dict(manifest)
            files_before = sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*"))
            a = cr.validate_package_cross_references(manifest, tmp, None, _MODEL)
            b = cr.validate_package_cross_references(manifest, tmp, None, _MODEL)
            self.assertEqual(a, b)
            self.assertEqual(mf.manifest_to_dict(manifest), before)
            self.assertEqual(sorted(p.relative_to(tmp).as_posix() for p in Path(tmp).rglob("*")), files_before)

    def test_malformed_artifact_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {"review-map/review-map.json": {}})
            # Corrupt the source artifact after manifest build.
            (Path(tmp) / ".arkheionx" / "out" / "review-map" / "review-map.json").write_text("{not json")
            checks = cr.validate_package_cross_references(manifest, tmp, None, _MODEL)
            self.assertTrue(any(c["name"] == "crossref.artifact.malformed" for c in checks))

    def test_messages_have_no_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest, _ = _pkg_with(tmp, {
                "review-map/review-map.json": {"functions": [{"function_id": "function:vault:f1"}]},
            })
            for check in cr.validate_package_cross_references(manifest, tmp, None, _MODEL):
                self.assertNotIn(tmp, check["message"])
                self.assertFalse(str(check["path"]).startswith("/"))


if __name__ == "__main__":
    unittest.main()
