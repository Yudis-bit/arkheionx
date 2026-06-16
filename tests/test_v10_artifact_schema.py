"""V10 artifact schema hardening.

Every JSON artifact carries the standard machine-readable header; the manifest lists
every artifact with type/path/generated/warnings; no artifact leaks an absolute
secret path / RPC URL / key; and warnings are surfaced as a list.
"""
import json
import unittest
from pathlib import Path

from arkheionx.warrun import run_war_run

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"
_HEADER = ("schema_version", "engine_version", "generated_at", "target_label",
           "target_hash", "semantic_mode", "confidence", "warnings", "artifact_type")
_SECRET_MARKERS = ("http://", "https://", "PRIVATE_KEY", "-----BEGIN", "mnemonic",
                   "alchemy.com", "infura.io")


class ArtifactSchemaTest(unittest.TestCase):
    def setUp(self):
        self.res = run_war_run(_GODEYE / "oracle_decimal_normalization_fixture", write=False)

    def test_every_json_has_standard_header(self):
        for name, payload in self.res["jsons"].items():
            with self.subTest(artifact=name):
                for key in _HEADER:
                    self.assertIn(key, payload, f"{name} missing {key}")
                self.assertIsInstance(payload["warnings"], list)

    def test_triage_and_manifest_have_header(self):
        for payload in (self.res["triage"], self.res["manifest"]):
            for key in _HEADER:
                self.assertIn(key, payload)

    def test_manifest_lists_artifacts(self):
        arts = self.res["manifest"]["artifacts"]
        self.assertTrue(arts)
        for a in arts:
            for key in ("path", "artifact_type", "generated", "warnings"):
                self.assertIn(key, a)
        # Every assembled JSON appears in the manifest artifact list.
        listed = {a["path"] for a in arts}
        for name in self.res["jsons"]:
            self.assertIn(name, listed)

    def test_target_label_is_not_an_absolute_path(self):
        label = self.res["jsons"]["economic-severity.json"]["target_label"]
        self.assertFalse(label.startswith("/"))
        self.assertEqual(label, "oracle_decimal_normalization_fixture")

    def test_no_absolute_secret_paths_or_urls(self):
        # Scan all JSON artifact text (not the absolute 'target'/'root' provenance keys,
        # which legitimately record where the run executed) for secret markers.
        for name, payload in self.res["jsons"].items():
            scrub = dict(payload)
            scrub.pop("target_label", None)
            blob = json.dumps(scrub)
            for marker in _SECRET_MARKERS:
                self.assertNotIn(marker, blob, f"{name} contains secret marker {marker}")

    def test_warnings_rendered_as_list_everywhere(self):
        for name, payload in self.res["jsons"].items():
            self.assertIsInstance(payload.get("warnings", []), list)

    def test_written_artifacts_match_manifest(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            res = run_war_run(_GODEYE / "adapter_actual_received_vs_credited_fixture",
                              out_dir=d, write=True)
            for name in res["jsons"]:
                self.assertTrue((Path(d) / name).is_file(), f"missing written {name}")
            self.assertTrue((Path(d) / "quality-gates.json").is_file())
            self.assertTrue((Path(d) / "16-state-contradictions.json").is_file())
            self.assertTrue((Path(d) / "15-dataflow-taint.json").is_file())


if __name__ == "__main__":
    unittest.main()
