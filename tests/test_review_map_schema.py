"""Protocol Review Map schema tests."""
import json
import unittest
from pathlib import Path

from arkheionx.review_map import build_review_map, build_test_gap_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "arkheionx" / "demo" / "fixtures"
SCHEMA_DIR = REPO_ROOT / "schemas"


def load(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


class ReviewMapSchemaTests(unittest.TestCase):
    def test_schema_files_exist_and_parse(self) -> None:
        for name in ("review-map.schema.json", "assumptions.schema.json", "test-gaps.schema.json"):
            schema = load(name)
            self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)
            self.assertIn("required", schema)

    def test_generated_payload_satisfies_required_top_level(self) -> None:
        schema = load("review-map.schema.json")
        payload = build_review_map(FIXTURES / "lending-vault", top=10).to_payload()
        for field in schema["required"]:
            self.assertIn(field, payload, field)

    def test_summary_and_safety_required_fields(self) -> None:
        schema = load("review-map.schema.json")
        payload = build_review_map(FIXTURES / "amm-swap", top=10).to_payload()
        for field in schema["properties"]["summary"]["required"]:
            self.assertIn(field, payload["summary"], field)
        for field in schema["properties"]["safety"]["required"]:
            self.assertIn(field, payload["safety"], field)

    def test_array_item_required_fields(self) -> None:
        schema = load("review-map.schema.json")
        payload = build_review_map(FIXTURES / "lending-vault", top=10).to_payload()
        for key in ("value_paths", "assumptions", "test_gaps", "proof_suggestions",
                    "functions", "contracts", "reviewer_notes"):
            req = schema["properties"][key].get("items", {}).get("required", [])
            items = payload[key]
            self.assertTrue(items, f"{key} should be non-empty for lending-vault")
            for field in req:
                self.assertIn(field, items[0], f"{key}.{field}")

    def test_mode_is_valid_enum(self) -> None:
        schema = load("review-map.schema.json")
        payload = build_review_map(FIXTURES / "oracle-staking", top=10).to_payload()
        self.assertIn(payload["mode"], schema["properties"]["mode"]["enum"])

    def test_test_gap_map_schema_and_payload(self) -> None:
        schema = load("test-gap-map.schema.json")
        self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
        payload = build_test_gap_map(build_review_map(FIXTURES / "lending-vault", top=10))
        for field in schema["required"]:
            self.assertIn(field, payload, field)
        self.assertTrue(payload["items"], "lending-vault should surface test gaps")
        for field in schema["properties"]["items"]["items"]["required"]:
            self.assertIn(field, payload["items"][0], field)


if __name__ == "__main__":
    unittest.main()
