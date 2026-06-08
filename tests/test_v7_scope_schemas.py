"""Schema tests for the v7 scope-orchestration artifacts.

Uses the same recursive draft-07 subset validator as tests/test_v6_schemas.py
(no jsonschema dependency).
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
import arkheionx.scope_orchestration as so

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE = REPO_ROOT / "examples" / "scope-fixture"
SCOPE = str(FIXTURE / "scope-note.md")


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


class V7SchemaFilesTests(unittest.TestCase):
    NAMES = ("scope-map.schema.json", "scope-lanes.schema.json", "scope-tasks.schema.json",
             "scope-pack-manifest.schema.json", "evidence-judge.schema.json", "report-filter.schema.json")

    def test_schema_files_exist_and_parse(self) -> None:
        for name in self.NAMES:
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)


class V7SchemaValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rm = build_review_map(FIXTURE)

    def test_scope_map_validates(self) -> None:
        data = so.build_scope_map(self.rm, FIXTURE, SCOPE)
        self.assertEqual(validate(data, load_schema("scope-map.schema.json")), [])

    def test_scope_lanes_validates(self) -> None:
        data = so.build_scope_lanes(self.rm, FIXTURE, SCOPE)
        self.assertEqual(validate(data, load_schema("scope-lanes.schema.json")), [])

    def test_scope_tasks_validates(self) -> None:
        data = so.build_scope_tasks(self.rm, FIXTURE, SCOPE)
        self.assertEqual(validate(data, load_schema("scope-tasks.schema.json")), [])

    def test_evidence_judge_validates(self) -> None:
        data = so.judge_evidence(self.rm, FIXTURE, SCOPE)
        self.assertEqual(validate(data, load_schema("evidence-judge.schema.json")), [])

    def test_report_filter_validates(self) -> None:
        data = so.filter_report_candidates(self.rm, FIXTURE, SCOPE)
        self.assertEqual(validate(data, load_schema("report-filter.schema.json")), [])

    def test_scope_pack_manifest_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = so.build_scope_pack(self.rm, FIXTURE, SCOPE, Path(tmp) / "pack", write=True)
        self.assertEqual(validate(result["manifest"], load_schema("scope-pack-manifest.schema.json")), [])


if __name__ == "__main__":
    unittest.main()
