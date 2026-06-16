"""Schema tests for the V9 hunter pack (triage.json + manifest.json).

Uses the same recursive draft-07 subset validator as the other schema tests
(no jsonschema dependency). Validates the real hunter triage.json / manifest.json
for several generic fixtures, including an RPC run with a mock transport.
"""
import json
import re
import unittest
from pathlib import Path

from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"
SMOKE = FX / "fresh_state_machine_value_flow"
PROXY = FX / "proxy_impl_changed"
ENDPOINT = "https://node.example.com/v3/SECRET"


def mock(endpoint, payload):
    res = {"eth_chainId": "0x1", "eth_getCode": "0x60016000f3",
           "eth_getStorageAt": "0x" + "0" * 24 + "bb" * 20, "eth_call": "0x" + "0" * 64}.get(
        payload.get("method"), "0x")
    return {"jsonrpc": "2.0", "id": payload.get("id", 1), "result": res}


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validate(instance, schema, path="$") -> list:
    errors: list = []
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


class HunterSchemaFilesTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in ("hunter-triage.schema.json", "hunter-manifest.schema.json"):
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("required", schema)


class HunterSchemaValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.triage_schema = load_schema("hunter-triage.schema.json")
        cls.manifest_schema = load_schema("hunter-manifest.schema.json")
        cls.smoke = build_hunter_pack(SMOKE, scope_file=str(SMOKE / "scope.md"),
                                      known_path=str(SMOKE / "known"), audits_path=str(SMOKE / "audits"),
                                      write=False)
        cls.collision = build_hunter_pack(FX / "scope_collision_versions",
                                          scope_file=str(FX / "scope_collision_versions" / "scope.md"),
                                          write=False)
        cls.rpc = build_hunter_pack(PROXY, scope_file=str(PROXY / "scope.md"),
                                    addresses_file=str(PROXY / "addresses.json"),
                                    rpc_endpoint=ENDPOINT, rpc_transport=mock, write=False)

    def test_triage_validates(self) -> None:
        for case in (self.smoke, self.collision, self.rpc):
            self.assertEqual(validate(case["triage"], self.triage_schema), [])

    def test_manifest_validates(self) -> None:
        for case in (self.smoke, self.collision, self.rpc):
            self.assertEqual(validate(case["manifest"], self.manifest_schema), [])

    def test_artifact_type_and_command(self) -> None:
        self.assertEqual(self.smoke["triage"]["artifact_type"], "hunter_triage")
        self.assertEqual(self.smoke["triage"]["schema_version"], "v9-universal-hunter")
        self.assertEqual(self.smoke["manifest"]["artifact_type"], "hunter_manifest")
        self.assertEqual(self.smoke["triage"]["command"], "hunter")

    def test_validator_detects_missing_required_key(self) -> None:
        broken = json.loads(json.dumps(self.smoke["triage"]))
        del broken["schema_version"]
        self.assertTrue(validate(broken, self.triage_schema))


if __name__ == "__main__":
    unittest.main()
