"""Tests for protocol-model sidecar integration in review packages (v3.6)."""
from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from arkheionx.review_package import builder as bld
from arkheionx.review_package import intelligence as intel

_RM = {
    "schema_version": "1.0.0", "generated_at": "", "repo_path": "/abs/repo",
    "contracts": [{"name": "Vault", "path": "src/Vault.sol"}],
    "functions": [{"contract": "Vault", "name": "borrow", "signature": "borrow(uint256)", "path": "src/Vault.sol"}],
    "value_paths": [], "assumptions": [], "test_gaps": [], "proof_suggestions": [], "evidence_links": [],
}


def _seed(tmp: str) -> None:
    out = Path(tmp) / ".arkheionx" / "out"
    (out / "review-map").mkdir(parents=True, exist_ok=True)
    (out / "review-map" / "review-map.json").write_text(json.dumps(_RM), encoding="utf-8")
    (out / "review-map" / "evidence-links.json").write_text('{"evidence_links": []}', encoding="utf-8")
    (out / "artifacts-index.json").write_text('{"targets": []}', encoding="utf-8")


class IntelligenceTests(unittest.TestCase):
    def test_default_sidecar_path(self) -> None:
        self.assertEqual(
            intel.default_protocol_model_package_path("/p/review-package"),
            Path("/p/review-package/artifacts/intelligence/protocol-model.json"),
        )

    def test_find_existing_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(intel.find_existing_protocol_model_artifact(tmp))
            out = Path(tmp) / ".arkheionx" / "out"
            out.mkdir(parents=True)
            (out / "protocol-model.json").write_text("{}")
            self.assertIsNotNone(intel.find_existing_protocol_model_artifact(tmp))

    def test_load_review_map_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(intel.load_review_map_payload(tmp), {})
            _seed(tmp)
            self.assertIn("functions", intel.load_review_map_payload(tmp))

    def test_malformed_review_map_handled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / ".arkheionx" / "out" / "review-map"
            out.mkdir(parents=True)
            (out / "review-map.json").write_text("{not json")
            self.assertEqual(intel.load_review_map_payload(tmp), {})
            self.assertIsNone(intel.build_protocol_model_for_package(tmp))

    def test_build_and_package_dict_scrubs_repo_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp)
            data = intel.build_protocol_model_for_package(tmp)
            self.assertIsNotNone(data)
            self.assertEqual(data["repo_path"], "")
            self.assertTrue(data["protocol_id"].startswith("protocol:"))
            json.dumps(data)
            self.assertNotIn("HUMAN_REVIEWED", json.dumps(data))
            self.assertNotIn("/abs/repo", json.dumps(data))

    def test_no_build_when_review_map_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(intel.build_protocol_model_for_package(tmp))
            info = intel.include_protocol_model_sidecar(tmp, Path(tmp) / "pkg", no_write=True)
            self.assertFalse(info["included"])
            self.assertTrue(info["warnings"])

    def test_no_write_writes_no_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            info = intel.include_protocol_model_sidecar(tmp, pkg, no_write=True)
            self.assertTrue(info["in_memory"])
            self.assertFalse(info["included"])
            self.assertFalse((pkg / "artifacts" / "intelligence" / "protocol-model.json").exists())


class BuilderIntelligenceTests(unittest.TestCase):
    def test_builder_includes_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp)
            result = bld.build_review_package(tmp)
            pkg = Path(tmp) / ".arkheionx" / "out" / "review-package"
            sidecar = pkg / "artifacts" / "intelligence" / "protocol-model.json"
            self.assertTrue(result.protocol_model_included)
            self.assertTrue(sidecar.is_file())
            self.assertNotIn(tmp, sidecar.read_text(encoding="utf-8"))
            self.assertNotIn("HUMAN_REVIEWED", sidecar.read_text(encoding="utf-8"))
            manifest = json.loads((pkg / "manifest.json").read_text())
            self.assertEqual(manifest["protocol_model_id"], result.protocol_model_id)
            self.assertTrue(any(a["kind"] == "protocol_model" for a in manifest["included_artifacts"]))

    def test_builder_disabled_writes_no_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp)
            result = bld.build_review_package(tmp, include_protocol_model=False)
            self.assertFalse(result.protocol_model_requested)
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package"
                              / "artifacts" / "intelligence" / "protocol-model.json").exists())

    def test_export_includes_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp)
            bld.build_review_package(tmp, export_format="zip")
            exports = Path(tmp) / ".arkheionx" / "out" / "review-package" / "exports"
            archive = list(exports.glob("*.zip"))[0]
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
            self.assertIn("arkheionx-review-package/artifacts/intelligence/protocol-model.json", names)

    def test_no_write_build_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(tmp)
            result = bld.build_review_package(tmp, no_write=True)
            self.assertTrue(result.protocol_model_requested)
            self.assertFalse(result.protocol_model_included)
            self.assertTrue(result.protocol_model_id.startswith("protocol:"))
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())


if __name__ == "__main__":
    unittest.main()
