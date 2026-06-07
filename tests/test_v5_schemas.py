"""Schema tests for the v5 Blind Spot Intelligence artifacts.

The repo validates schemas by hand (no jsonschema dependency). This mirrors the
recursive draft-07 subset validator used by tests/test_research_schema.py and
runs it against generated blind-spots, criticality-map, counterfactuals, and
research-pack-manifest payloads for both demo fixtures.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.research.surfaces import build_research_surfaces
from arkheionx.blind_spots import (
    build_blind_spot_map,
    build_criticality_map,
    build_counterfactual_plan,
    build_research_pack,
)
from arkheionx.version import PACKAGE_VERSION

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURES = [
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


class V5SchemaFilesTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in ("blind-spots.schema.json", "criticality-map.schema.json",
                     "counterfactuals.schema.json", "research-pack-manifest.schema.json"):
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)


class V5SchemaValidationTests(unittest.TestCase):
    def _surfaces(self, fixture):
        rm = build_review_map(fixture)
        return rm, build_research_surfaces(rm, fixture)

    def test_blind_spots_validates(self) -> None:
        schema = load_schema("blind-spots.schema.json")
        for fixture in FIXTURES:
            rm, surfaces = self._surfaces(fixture)
            payload = build_blind_spot_map(rm, surfaces, source_files=4, test_files=1)
            errors = validate(payload, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(payload["kind"], "blind-spots")

    def test_criticality_map_validates(self) -> None:
        schema = load_schema("criticality-map.schema.json")
        for fixture in FIXTURES:
            rm, surfaces = self._surfaces(fixture)
            payload = build_criticality_map(rm, surfaces)
            errors = validate(payload, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(payload["kind"], "criticality-map")

    def test_counterfactuals_validates(self) -> None:
        schema = load_schema("counterfactuals.schema.json")
        for fixture in FIXTURES:
            rm, surfaces = self._surfaces(fixture)
            payload = build_counterfactual_plan(rm, surfaces)
            errors = validate(payload, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(payload["kind"], "counterfactuals")
            ids = [cf["id"] for cf in payload["counterfactuals"]]
            self.assertTrue(all(re.fullmatch(r"CF-\d{3}", i) for i in ids))

    def test_research_pack_manifest_validates(self) -> None:
        schema = load_schema("research-pack-manifest.schema.json")
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            with tempfile.TemporaryDirectory() as tmp:
                result = build_research_pack(rm, fixture, Path(tmp) / "pack",
                                             package_version=PACKAGE_VERSION, write=False)
            manifest = result["manifest"]
            errors = validate(manifest, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(manifest["kind"], "research-pack-manifest")


if __name__ == "__main__":
    unittest.main()
