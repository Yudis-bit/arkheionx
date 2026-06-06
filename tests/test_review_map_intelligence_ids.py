"""Tests for additive protocol intelligence ID backfill in the review map (v3.5)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from arkheionx.intelligence import build as intel_build
from arkheionx.review_map import build_review_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "arkheionx" / "demo" / "fixtures" / "lending-vault"
SCHEMA = json.loads((REPO_ROOT / "schemas" / "review-map.schema.json").read_text(encoding="utf-8"))

# Fields introduced by the v3.5 additive backfill, by array section.
NEW_FIELDS = {
    "contracts": ["contract_id"],
    "functions": ["function_id"],
    "value_paths": ["entry_function_id", "exit_function_id"],
    "test_gaps": ["function_id"],
    "proof_suggestions": ["target_function_id"],
}


class BackfillPresenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rm = build_review_map(FIXTURE, top=10)

    def test_contract_and_function_ids_backfilled(self) -> None:
        self.assertTrue(self.rm.contracts and self.rm.functions)
        for contract in self.rm.contracts:
            self.assertTrue(contract.contract_id.startswith("contract:"))
        for function in self.rm.functions:
            self.assertTrue(function.function_id.startswith("function:"))

    def test_linked_ids_resolve_to_function_ids(self) -> None:
        fids = {f.display_id: f.function_id for f in self.rm.functions}
        for vp in self.rm.value_paths:
            if vp.exit_function and "." in vp.exit_function:
                self.assertEqual(vp.exit_function_id, fids.get(vp.exit_function, ""))
        for gap in self.rm.test_gaps:
            if gap.related_function in fids:
                self.assertEqual(gap.function_id, fids[gap.related_function])
        for proof in self.rm.proof_suggestions:
            if proof.target in fids:
                self.assertEqual(proof.target_function_id, fids[proof.target])

    def test_ids_match_protocol_model_builder(self) -> None:
        model = intel_build.build_protocol_model_from_review_map(self.rm, str(FIXTURE))
        self.assertEqual(
            {c.name: c.contract_id for c in self.rm.contracts},
            {c.name: c.contract_id for c in model.contracts},
        )
        self.assertEqual(
            {f.display_id: f.function_id for f in self.rm.functions},
            {f.display_name: f.function_id for f in model.functions},
        )

    def test_backfill_is_deterministic(self) -> None:
        again = build_review_map(FIXTURE, top=10)
        self.assertEqual(
            [f.function_id for f in self.rm.functions],
            [f.function_id for f in again.functions],
        )


class BackwardCompatibilityTests(unittest.TestCase):
    def test_new_fields_are_optional_not_required(self) -> None:
        for section, fields in NEW_FIELDS.items():
            required = SCHEMA["properties"][section]["items"].get("required", [])
            for name in fields:
                self.assertNotIn(name, required, f"{section}.{name} must stay optional")

    def test_new_fields_documented_in_schema_properties(self) -> None:
        for section, fields in NEW_FIELDS.items():
            props = SCHEMA["properties"][section]["items"]["properties"]
            for name in fields:
                self.assertIn(name, props, f"{section}.{name} should be documented")

    def test_old_artifact_without_new_fields_still_valid(self) -> None:
        # Strip the new fields to simulate a pre-v3.5 artifact and confirm every
        # schema-required field is still present.
        payload = build_review_map(FIXTURE, top=10).to_payload()
        for section, fields in NEW_FIELDS.items():
            for item in payload[section]:
                for name in fields:
                    item.pop(name, None)
        for section in NEW_FIELDS:
            required = SCHEMA["properties"][section]["items"].get("required", [])
            for item in payload[section]:
                for name in required:
                    self.assertIn(name, item, f"{section}.{name}")

    def test_top_level_keys_unchanged(self) -> None:
        payload = build_review_map(FIXTURE, top=10).to_payload()
        self.assertEqual(set(payload.keys()), set(SCHEMA["required"]))


if __name__ == "__main__":
    unittest.main()
