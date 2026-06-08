"""Schema tests for the v6 Evidence Graph artifacts.

Validates generated evidence-graph, interaction-matrix, unresolved-map, and
complete-review-manifest payloads with the same recursive draft-07 subset
validator used by tests/test_v5_schemas.py (no jsonschema dependency).
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.research.surfaces import build_research_surfaces
from arkheionx.evidence_graph import (
    build_complete_review,
    build_evidence_graph,
    build_interaction_matrix,
    build_unresolved_map,
)
from arkheionx.version import PACKAGE_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURES = [
    REPO_ROOT / "examples" / "blind-spot-fixture",
    REPO_ROOT / "examples" / "vault-strategy-oracle-fixture",
    REPO_ROOT / "examples" / "periphery-auth-fixture",
]


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


class V6SchemaFilesTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in ("evidence-graph.schema.json", "interaction-matrix.schema.json",
                     "unresolved-map.schema.json", "complete-review-manifest.schema.json"):
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)


class V6SchemaValidationTests(unittest.TestCase):
    def _surfaces(self, fixture):
        rm = build_review_map(fixture)
        return rm, build_research_surfaces(rm, fixture)

    def test_evidence_graph_validates(self) -> None:
        schema = load_schema("evidence-graph.schema.json")
        for fixture in FIXTURES:
            rm, surf = self._surfaces(fixture)
            payload = build_evidence_graph(rm, surf, source_files=6, test_files=1,
                                           package_version=PACKAGE_VERSION)
            self.assertEqual(validate(payload, schema), [], fixture.name)
            for n in payload["nodes"]:
                self.assertRegex(n["node_id"], r"^EV-\d{3}$")

    def test_interaction_matrix_validates(self) -> None:
        schema = load_schema("interaction-matrix.schema.json")
        for fixture in FIXTURES:
            rm, surf = self._surfaces(fixture)
            payload = build_interaction_matrix(rm, surf, package_version=PACKAGE_VERSION)
            self.assertEqual(validate(payload, schema), [], fixture.name)
            ids = [ix["interaction_id"] for ix in payload["interactions"]]
            self.assertTrue(all(re.fullmatch(r"IX-\d{3}", i) for i in ids))

    def test_unresolved_map_validates(self) -> None:
        schema = load_schema("unresolved-map.schema.json")
        for fixture in FIXTURES:
            rm, surf = self._surfaces(fixture)
            payload = build_unresolved_map(rm, surf, package_version=PACKAGE_VERSION)
            self.assertEqual(validate(payload, schema), [], fixture.name)

    def test_complete_review_manifest_validates(self) -> None:
        schema = load_schema("complete-review-manifest.schema.json")
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            with tempfile.TemporaryDirectory() as tmp:
                result = build_complete_review(rm, fixture, Path(tmp) / "cr",
                                               package_version=PACKAGE_VERSION, write=False)
            self.assertEqual(validate(result["manifest"], schema), [], fixture.name)
            self.assertEqual(result["manifest"]["kind"], "complete-review-manifest")


if __name__ == "__main__":
    unittest.main()
