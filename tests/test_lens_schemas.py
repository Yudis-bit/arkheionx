"""Schema tests for the v7.5 Protocol Lens artifacts.

Uses the same recursive draft-07 subset validator as tests/test_v7_scope_schemas.py
and tests/test_v6_schemas.py (no jsonschema dependency). Validates the real
lens-pack manifest produced for the synthetic Morpho Midnight toy fixture, plus the
five standalone command artifacts embedded in the pack, against committed schemas.
"""
import json
import re
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.protocol_lens import SCHEMA_VERSION, build_lens_pack, get_lens

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "morpho_midnight_toy"
SCOPE = str(FIXTURE / "scope.md")


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validate(instance, schema, path="$") -> list[str]:
    errors: list[str] = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object, got {type(instance).__name__}"]
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{path}: missing required '{field}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors += validate(instance[key], subschema, f"{path}.{key}")
    elif t == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array, got {type(instance).__name__}"]
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors += validate(item, item_schema, f"{path}[{i}]")
    elif t == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string, got {type(instance).__name__}"]
    elif t == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            return [f"{path}: expected integer"]
    elif t == "boolean":
        if not isinstance(instance, bool):
            return [f"{path}: expected boolean"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if "pattern" in schema and isinstance(instance, str) and not re.search(schema["pattern"], instance):
        errors.append(f"{path}: {instance!r} does not match {schema['pattern']}")
    return errors


LENS_SCHEMA_NAMES = (
    "lens-pack.schema.json", "lens-map.schema.json", "lens-lanes.schema.json",
    "lens-tasks.schema.json", "lens-evidence.schema.json", "lens-report-filter.schema.json",
)


class LensSchemaFilesTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in LENS_SCHEMA_NAMES:
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)


class LensSchemaValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rm = build_review_map(FIXTURE)
        lens = get_lens("morpho-midnight")
        cls.manifest = build_lens_pack(lens, rm, FIXTURE, scope_file=SCOPE, write=False)["manifest"]

    def test_lens_pack_manifest_validates(self) -> None:
        self.assertEqual(validate(self.manifest, load_schema("lens-pack.schema.json")), [])

    def test_schema_version_present(self) -> None:
        self.assertTrue(self.manifest["schema_version"])
        self.assertEqual(self.manifest["schema_version"], SCHEMA_VERSION)

    def test_lens_id_is_morpho_midnight(self) -> None:
        self.assertEqual(self.manifest["lens"]["lens_id"], "morpho-midnight")

    def test_behavior_promises_non_empty(self) -> None:
        promises = self.manifest["data"]["lens_map"]["behavior_promises"]
        self.assertTrue(promises)
        self.assertTrue(all(p.get("id") and p.get("text") for p in promises))

    def test_economic_invariants_non_empty(self) -> None:
        invariants = self.manifest["data"]["lens_map"]["economic_invariants"]
        self.assertTrue(invariants)
        self.assertTrue(all(i.get("id") and i.get("statement") for i in invariants))

    def test_review_lanes_non_empty(self) -> None:
        lanes = self.manifest["data"]["review_lanes"]
        self.assertGreater(lanes["lane_count"], 0)
        self.assertTrue(lanes["lanes"])

    def test_report_filter_present(self) -> None:
        self.assertIn("report_filter", self.manifest["data"])
        self.assertIn("candidate_count", self.manifest["data"]["report_filter"])

    def test_embedded_command_artifacts_validate(self) -> None:
        data = self.manifest["data"]
        self.assertEqual(validate(data["lens_map"], load_schema("lens-map.schema.json")), [])
        self.assertEqual(validate(data["review_lanes"], load_schema("lens-lanes.schema.json")), [])
        self.assertEqual(validate(data["scope_tasks"], load_schema("lens-tasks.schema.json")), [])
        self.assertEqual(validate(data["evidence_map"], load_schema("lens-evidence.schema.json")), [])
        self.assertEqual(validate(data["report_filter"], load_schema("lens-report-filter.schema.json")), [])

    def test_validator_detects_missing_required_key(self) -> None:
        # Prove the validator actually enforces required keys (no false green).
        broken = json.loads(json.dumps(self.manifest))
        del broken["schema_version"]
        self.assertTrue(validate(broken, load_schema("lens-pack.schema.json")))


if __name__ == "__main__":
    unittest.main()
