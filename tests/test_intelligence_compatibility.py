"""Artifact compatibility + determinism hardening (v3.5, Agent 7).

Old v3.4-style payloads without intelligence fields stay consumable and never
fabricate links; v3.5 additive IDs coexist with the legacy IDs they alias; and
identical input produces an identical, plain-JSON model with no injected
timestamp.
"""
from __future__ import annotations

import copy
import json
import os
import unittest
from pathlib import Path

from arkheionx.intelligence import build, linking


def _full_review_map() -> dict:
    return {
        "repo_path": "/repo",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "functions": [{"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)", "path": "src/Vault.sol"}],
        "value_paths": [{"id": "vp-vault-withdraw", "label": "deposit -> withdraw",
                         "entry_function": "Vault.withdraw", "exit_function": "Vault.withdraw",
                         "assumptions": ["asm-oracle-fresh"]}],
        "assumptions": [{"id": "asm-oracle-fresh", "title": "Oracle fresh", "category": "oracle",
                         "used_by": ["Vault.withdraw"]}],
        "test_gaps": [{"id": "gap-vault-withdraw", "related_function": "Vault.withdraw", "suggested_test": "overdraw"}],
        "proof_suggestions": [{"id": "proof-vault-withdraw", "target": "Vault.withdraw",
                               "related_test_gap": "gap-vault-withdraw"}],
        "evidence_links": [{"id": "ev-proof-vault", "source": "proof", "artifact_kind": "proof",
                            "target": "Vault.withdraw", "evidence_package_id": "evidence:old"}],
    }


class OldArtifactCompatibilityTests(unittest.TestCase):
    """A: v3.4 payloads lacking ProtocolModel IDs remain consumable."""

    def test_review_map_without_intelligence_ids_builds(self) -> None:
        # Old review-map functions carry no function_id; the builder derives one and
        # does not promote a missing legacy id into a real link.
        model = build.build_protocol_model_from_review_map(
            {"functions": [{"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)"}]}, "/repo")
        self.assertTrue(model.functions[0].function_id.startswith("function:"))
        self.assertEqual(model.functions[0].aliases.get("legacy_function_id", ""), "")

    def test_old_artifacts_without_ids_do_not_crash_or_fabricate_links(self) -> None:
        # Model has only Vault.withdraw; every artifact below targets an unknown fn.
        model = build.build_protocol_model_from_review_map(
            {"functions": [{"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)"}]}, "/repo")
        linking.link_artifacts_to_protocol_model(
            model,
            proofs=[{"proof_receipt_id": "proof:old", "target": "Ghost.fn", "evidence_level": "EXECUTION_CONFIRMED"}],
            traces=[{"trace_receipt_id": "trace:old", "target": "Ghost.fn"}],
            evidence_packages=[{"evidence_package_id": "evidence:old", "target": "Ghost.fn",
                                "evidence_level": "EXECUTION_CONFIRMED"}],
            reports=[{"target": "Ghost.fn"}],
            evidence_links={"evidence_links": [{"id": "ev-old", "source": "proof", "target": "Ghost.fn"}]},
        )
        # Old primary IDs preserved verbatim.
        self.assertEqual(model.proof_receipts[0].proof_receipt_id, "proof:old")
        self.assertEqual(model.trace_receipts[0].trace_receipt_id, "trace:old")
        self.assertEqual(model.evidence_packages[0].evidence_package_id, "evidence:old")
        self.assertEqual(model.evidence_links[0].aliases["id"], "ev-old")
        # No false function links invented for unresolved targets.
        for node in (model.proof_receipts[0], model.trace_receipts[0],
                     model.evidence_packages[0], model.evidence_links[0]):
            self.assertEqual(node.target_function_id if hasattr(node, "target_function_id")
                             else node.linked_target_function_id, "")
        self.assertEqual(model.trace_receipts[0].linked_proof_receipt_id, "")

    def test_empty_payloads_are_safe(self) -> None:
        model = build.build_protocol_model_from_review_map({}, "/repo")
        linking.link_reasoning(model)
        linking.link_artifacts_to_protocol_model(model)
        self.assertTrue(model.protocol_id.startswith("protocol:"))


class AdditiveCompatibilityTests(unittest.TestCase):
    """B: new intelligence IDs are additive; legacy IDs survive as aliases."""

    def setUp(self) -> None:
        self.model = build.build_protocol_model_from_review_map(_full_review_map(), "/repo")

    def test_legacy_ids_coexist_with_new_ids(self) -> None:
        vp, asm = self.model.value_paths[0], self.model.assumptions[0]
        gap, ps = self.model.test_gaps[0], self.model.proof_suggestions[0]
        self.assertTrue(vp.value_path_id.startswith("value-path:") and vp.aliases["id"] == "vp-vault-withdraw")
        self.assertTrue(asm.assumption_id.startswith("assumption:") and asm.aliases["id"] == "asm-oracle-fresh")
        self.assertTrue(gap.test_gap_id.startswith("test-gap:") and gap.aliases["id"] == "gap-vault-withdraw")
        self.assertTrue(ps.proof_suggestion_id.startswith("proof-suggestion:") and ps.aliases["id"] == "proof-vault-withdraw")
        self.assertEqual(self.model.evidence_links[0].aliases["id"], "ev-proof-vault")

    def test_old_receipt_ids_plus_additive_function_link(self) -> None:
        linking.link_proof_receipts_to_model(
            self.model, [{"proof_receipt_id": "proof:old", "review_map_target": "Vault.withdraw"}])
        node = self.model.proof_receipts[0]
        self.assertEqual(node.proof_receipt_id, "proof:old")  # old field intact
        self.assertEqual(node.target_function_id, self.model.functions[0].function_id)  # additive link

    def test_model_dict_is_plain_json(self) -> None:
        data = build.protocol_model_to_dict(self.model)
        self.assertEqual(json.loads(json.dumps(data)), data)


class DeterminismTests(unittest.TestCase):
    """E: stable, reorder-invariant, path-consistent, timestamp-free serialization."""

    def test_repeated_build_is_identical(self) -> None:
        a = build.build_protocol_model_from_review_map(_full_review_map(), "/repo")
        b = build.build_protocol_model_from_review_map(_full_review_map(), "/repo")
        self.assertEqual(build.protocol_model_to_dict(a), build.protocol_model_to_dict(b))

    def test_key_reorder_does_not_change_ids(self) -> None:
        payload = _full_review_map()
        reordered = {k: payload[k] for k in reversed(list(payload))}
        reordered["functions"] = [{k: f[k] for k in reversed(list(f))} for f in payload["functions"]]
        a = build.build_protocol_model_from_review_map(payload, "/repo")
        b = build.build_protocol_model_from_review_map(reordered, "/repo")
        self.assertEqual(a.functions[0].function_id, b.functions[0].function_id)
        self.assertEqual(build.protocol_model_to_dict(a), build.protocol_model_to_dict(b))

    def test_path_and_str_repo_are_consistent(self) -> None:
        a = build.build_protocol_model_from_review_map(_full_review_map(), Path("/repo"))
        b = build.build_protocol_model_from_review_map(_full_review_map(), "/repo")
        self.assertEqual(build.protocol_model_to_dict(a), build.protocol_model_to_dict(b))

    def test_no_timestamp_invented(self) -> None:
        model = build.build_protocol_model_from_review_map({"functions": []}, "/repo")
        self.assertEqual(model.generated_at, "")

    def test_build_is_non_mutating(self) -> None:
        payload = _full_review_map()
        original = copy.deepcopy(payload)
        build.build_protocol_model_from_review_map(payload, "/repo")
        self.assertEqual(payload, original)


if __name__ == "__main__":
    unittest.main()
