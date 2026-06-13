"""Artifact + schema tests for `arkheionx triage`."""
import json
import re
import unittest
from pathlib import Path

from arkheionx.senior_triage import models as M
from arkheionx.senior_triage.pack import build_senior_triage_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "senior_triage_toy"
SCHEMAS = REPO_ROOT / "schemas"

MD_ARTIFACTS = [
    "00-target-decision.md", "01-bounty-eligibility.md", "02-known-issue-map.md",
    "03-freshness-diff.md", "04-deployment-reality.md", "05-lead-scoreboard.md",
    "06-top-3-leads.md", "07-do-not-touch.md", "08-next-commands.md", "09-agent-brief.md",
]


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate(instance, schema, path="$") -> list:
    errors: list = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object, got {type(instance).__name__}"]
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{path}: missing required '{field}'")
        for key, sub in schema.get("properties", {}).items():
            if key in instance:
                errors += validate(instance[key], sub, f"{path}.{key}")
    elif t == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array, got {type(instance).__name__}"]
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors += validate(item, item_schema, f"{path}[{i}]")
    elif t == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string"]
    elif t == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            return [f"{path}: expected integer"]
    elif t == "boolean":
        if not isinstance(instance, bool):
            return [f"{path}: expected boolean"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if "pattern" in schema and isinstance(instance, str) and not re.search(schema["pattern"], instance):
        errors.append(f"{path}: {instance!r} !~ {schema['pattern']}")
    return errors


def build():
    return build_senior_triage_pack(
        FIXTURE,
        scope_file=str(FIXTURE / "scope.md"),
        known_path=str(FIXTURE / "known"),
        audits_path=str(FIXTURE / "audits"),
        addresses_file=str(FIXTURE / "addresses.json"),
        write=False,
    )


class SchemaFilesTests(unittest.TestCase):
    def test_schema_files_parse_and_are_draft07(self) -> None:
        for name in ("senior-triage.schema.json", "senior-triage-manifest.schema.json"):
            schema = load_schema(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("required", schema)


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()
        cls.triage = cls.result["triage"]
        cls.manifest = cls.result["manifest"]
        cls.contents = cls.result["contents"]

    def test_triage_json_validates(self) -> None:
        self.assertEqual(validate(self.triage, load_schema("senior-triage.schema.json")), [])

    def test_manifest_validates(self) -> None:
        self.assertEqual(validate(self.manifest, load_schema("senior-triage-manifest.schema.json")), [])

    def test_all_markdown_artifacts_present(self) -> None:
        for name in MD_ARTIFACTS:
            self.assertIn(name, self.contents)
            self.assertTrue(self.contents[name].strip(), name)

    def test_manifest_counts_twelve_artifacts(self) -> None:
        self.assertEqual(self.manifest["artifact_count"], 12)
        self.assertEqual(len(self.manifest["artifact_paths"]), 12)

    def test_top_leads_capped_at_three(self) -> None:
        self.assertLessEqual(len(self.triage["top_3_leads"]), 3)

    def test_do_not_touch_exists(self) -> None:
        self.assertTrue(self.triage["do_not_touch"])
        for item in self.triage["do_not_touch"]:
            self.assertTrue(item["reason"])
            self.assertTrue(item["what_would_change"])

    def test_every_lead_has_a_kill_condition(self) -> None:
        self.assertTrue(self.triage["lead_scoreboard"])
        for lead in self.triage["lead_scoreboard"]:
            self.assertTrue(lead["kill_condition"], f"{lead['id']} missing kill_condition")

    def test_manifest_is_local_only(self) -> None:
        for flag in ("local_only", "no_push", "no_remote_write"):
            self.assertTrue(self.manifest[flag], flag)

    def test_lead_decisions_use_strict_vocabulary(self) -> None:
        for lead in self.triage["lead_scoreboard"]:
            self.assertIn(lead["decision"], (M.LEAD_PURSUE, M.LEAD_PARK, M.LEAD_KILL))


if __name__ == "__main__":
    unittest.main()
