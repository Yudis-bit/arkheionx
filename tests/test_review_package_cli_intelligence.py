"""Tests for protocol-model behavior in the review-package CLI (v3.6)."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_RM = {
    "schema_version": "1.0.0", "generated_at": "",
    "contracts": [{"name": "Vault", "path": "src/Vault.sol"}],
    "functions": [{"contract": "Vault", "name": "borrow", "signature": "borrow(uint256)", "path": "src/Vault.sol"}],
}
_PM_KEYS = {"protocol_model_requested", "protocol_model_included", "protocol_model_path",
            "protocol_model_id", "crossref_check_count", "crossref_warning_count", "crossref_error_count"}


def _seed(repo: Path) -> None:
    out = repo / ".arkheionx" / "out"
    (out / "review-map").mkdir(parents=True, exist_ok=True)
    (out / "review-map" / "review-map.json").write_text(json.dumps(_RM), encoding="utf-8")
    (out / "review-map" / "evidence-links.json").write_text('{"evidence_links": []}', encoding="utf-8")
    (out / "artifacts-index.json").write_text('{"targets": []}', encoding="utf-8")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, ARKHEIONX_COLOR="never")
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", "review-package", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class CliIntelligenceTests(unittest.TestCase):
    def test_json_has_protocol_model_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            result = _run(tmp, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\x1b[", result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(_PM_KEYS.issubset(payload))
            self.assertTrue(payload["protocol_model_requested"])
            self.assertTrue(payload["protocol_model_included"])
            self.assertTrue(payload["protocol_model_id"].startswith("protocol:"))
            self.assertTrue(payload["protocol_model_path"].startswith(".arkheionx/out/review-package/"))
            self.assertFalse(payload["ready_for_submission"])
            self.assertTrue(payload["manual_review_required"])

    def test_no_overclaim_in_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            blob = _run(tmp, "--json").stdout.lower()
            for term in ("audit passed", "confirmed vulnerability", "final severity", "bounty eligible", "human_reviewed"):
                self.assertNotIn(term, blob)

    def test_write_includes_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            _run(tmp)
            sidecar = Path(tmp) / ".arkheionx" / "out" / "review-package" / "artifacts" / "intelligence" / "protocol-model.json"
            self.assertTrue(sidecar.is_file())

    def test_no_write_writes_no_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            payload = json.loads(_run(tmp, "--no-write", "--json").stdout)
            self.assertTrue(payload["protocol_model_requested"])
            self.assertFalse(payload["protocol_model_included"])
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package").exists())

    def test_no_protocol_model_flag_disables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            payload = json.loads(_run(tmp, "--no-protocol-model", "--json").stdout)
            self.assertFalse(payload["protocol_model_requested"])
            self.assertFalse(payload["protocol_model_included"])
            self.assertFalse((Path(tmp) / ".arkheionx" / "out" / "review-package"
                              / "artifacts" / "intelligence" / "protocol-model.json").exists())

    def test_export_includes_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            _run(tmp, "--export", "zip")
            exports = Path(tmp) / ".arkheionx" / "out" / "review-package" / "exports"
            archive = list(exports.glob("*.zip"))[0]
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
            self.assertIn("arkheionx-review-package/artifacts/intelligence/protocol-model.json", names)

    def test_human_mentions_protocol_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _seed(Path(tmp))
            out = _run(tmp).stdout
            self.assertIn("Protocol model:", out)
            self.assertIn("Ready for submission: False", out)


if __name__ == "__main__":
    unittest.main()
