"""Schema tests for the v8 review pack (`arkheionx review`).

Uses the same recursive draft-07 subset validator as tests/test_v7_scope_schemas.py
and tests/test_lens_schemas.py (no jsonschema dependency). Validates the real
review.json and manifest.json produced for the synthetic fixed-credit-market toy
fixture, both without and with a lens, against the committed v8 schemas.
"""
import json
import re
import unittest
from pathlib import Path

from arkheionx.review_pack import build_review_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "fixed_credit_market_toy"
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


class V8SchemaFilesTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in ("manifest.schema.json", "review-pack.schema.json"):
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)


class V8ReviewPackSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.nolens = build_review_pack(FIXTURE, scope_file=SCOPE, write=False)
        cls.lens = build_review_pack(FIXTURE, scope_file=SCOPE, lens_id="fixed-credit-market", write=False)
        cls.review_schema = load_schema("review-pack.schema.json")
        cls.manifest_schema = load_schema("manifest.schema.json")

    def test_review_json_validates_without_lens(self) -> None:
        self.assertEqual(validate(self.nolens["review"], self.review_schema), [])

    def test_review_json_validates_with_lens(self) -> None:
        self.assertEqual(validate(self.lens["review"], self.review_schema), [])

    def test_manifest_validates_without_lens(self) -> None:
        self.assertEqual(validate(self.nolens["manifest"], self.manifest_schema), [])

    def test_manifest_validates_with_lens(self) -> None:
        self.assertEqual(validate(self.lens["manifest"], self.manifest_schema), [])

    def test_artifact_type_and_command(self) -> None:
        self.assertEqual(self.nolens["review"]["artifact_type"], "review-pack")
        self.assertEqual(self.nolens["manifest"]["artifact_type"], "review-pack-manifest")
        self.assertEqual(self.nolens["review"]["command"], "review")

    def test_lens_manifest_counts_artifacts(self) -> None:
        self.assertEqual(self.lens["manifest"]["artifact_count"], 18)
        self.assertEqual(self.nolens["manifest"]["artifact_count"], 12)

    def test_every_review_carries_version_fields(self) -> None:
        for pack in (self.nolens, self.lens):
            r = pack["review"]
            self.assertTrue(r["schema_version"])
            self.assertTrue(r["arkheionx_version"])
            self.assertTrue(r["generated_at"])

    def test_scope_tasks_have_kill_conditions(self) -> None:
        tasks = self.nolens["review"]["data"]["evidence_tasks"]["tasks"]
        self.assertTrue(tasks)
        for t in tasks:
            self.assertTrue(t.get("kill_condition"), f"task {t.get('task_id')} missing kill_condition")

    def test_lens_tasks_have_kill_conditions(self) -> None:
        tasks = self.lens["review"]["data"]["lens"]["scope_tasks"]["tasks"]
        self.assertTrue(tasks)
        for t in tasks:
            self.assertTrue(t.get("kill_condition"), f"lens task {t.get('id')} missing kill_condition")

    def test_validator_detects_missing_required_key(self) -> None:
        broken = json.loads(json.dumps(self.nolens["review"]))
        del broken["schema_version"]
        self.assertTrue(validate(broken, self.review_schema))


if __name__ == "__main__":
    unittest.main()
