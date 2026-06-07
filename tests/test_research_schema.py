"""Schema tests for the v4.1 research-memory artifacts.

The repo validates schemas by hand (no jsonschema dependency). This module adds
a small recursive validator covering the subset used by the research schemas
(type / required / properties / items / enum / pattern) and runs it against
generated agent-brief, hypothesis-log, and case-study payloads for two fixtures.
"""
import json
import re
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map
from arkheionx.research import (
    build_agent_brief_from_review_map,
    build_case_study_from_review_map,
    build_hypothesis_log_from_review_map,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
FIXTURES = [
    REPO_ROOT / "examples" / "vault-strategy-oracle-fixture",
    REPO_ROOT / "examples" / "periphery-auth-fixture",
]


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validate(instance, schema, path="$") -> list[str]:
    """Validate ``instance`` against a draft-07 subset. Returns a list of errors."""
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


# Words that must never appear in research-memory output (overclaim / unsafe).
_FORBIDDEN_OUTPUT = ("confirmed vulnerability", "guaranteed", "exploit automation is", "drain")


class ResearchSchemaTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in ("agent-brief.schema.json", "hypothesis-log.schema.json", "case-study.schema.json"):
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)

    def test_agent_brief_validates(self) -> None:
        schema = load_schema("agent-brief.schema.json")
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            payload = build_agent_brief_from_review_map(rm, fixture, source_files=4, test_files=1)
            errors = validate(payload, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(payload["kind"], "agent-brief")
            self.assertTrue(payload["hypotheses"], fixture.name)
            ids = [h["id"] for h in payload["hypotheses"]]
            self.assertEqual(ids, sorted(ids), "hypothesis ids must be ordered")
            self.assertTrue(all(re.fullmatch(r"HYP-\d{3}", i) for i in ids))
            self.assertTrue(all(h["status"] == "open" for h in payload["hypotheses"]))

    def test_hypothesis_log_validates(self) -> None:
        schema = load_schema("hypothesis-log.schema.json")
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            payload = build_hypothesis_log_from_review_map(rm, fixture)
            errors = validate(payload, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(payload["hypotheses"][0]["id"], "HYP-001")
            for entry in payload["hypotheses"]:
                for field in ("test_command", "result", "rejection_reason", "confirmation_notes", "human_decision"):
                    self.assertEqual(entry[field], "", f"{field} must start empty")
            self.assertEqual(payload["summary"]["by_status"], {"open": payload["summary"]["total"]})

    def test_case_study_validates(self) -> None:
        schema = load_schema("case-study.schema.json")
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            payload = build_case_study_from_review_map(rm, fixture)
            errors = validate(payload, schema)
            self.assertEqual(errors, [], f"{fixture.name}: {errors}")
            self.assertEqual(payload["confirmed_findings"], [], "no confirmed findings by default")
            self.assertIn("not an audit report", payload["safety_note"])

    def test_outputs_make_no_unsafe_claims(self) -> None:
        for fixture in FIXTURES:
            rm = build_review_map(fixture)
            for payload in (
                build_agent_brief_from_review_map(rm, fixture),
                build_hypothesis_log_from_review_map(rm, fixture),
                build_case_study_from_review_map(rm, fixture),
            ):
                blob = json.dumps(payload).lower()
                for phrase in _FORBIDDEN_OUTPUT:
                    self.assertNotIn(phrase, blob, f"{fixture.name}: forbidden phrase {phrase!r}")


if __name__ == "__main__":
    unittest.main()
