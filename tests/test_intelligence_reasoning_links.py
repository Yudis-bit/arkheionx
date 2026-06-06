"""Tests for the protocol intelligence reasoning links (v3.5, Agent 5)."""
from __future__ import annotations

import unittest

from arkheionx.intelligence import build, linking
from arkheionx.intelligence.model import (
    AssumptionNode,
    ProofSuggestionNode,
    ProtocolModel,
    TestGapNode,
)


def _payload(extra_assumptions: list[dict] | None = None) -> dict:
    assumptions = [
        {"id": "asm-oracle-fresh", "title": "Oracle is fresh", "category": "oracle",
         "used_by": ["Vault.withdraw"], "evidence_level": "HEURISTIC"},
    ]
    assumptions += extra_assumptions or []
    return {
        "repo_path": "/repo",
        "functions": [
            {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)",
             "path": "src/Vault.sol", "line": 10},
        ],
        "value_paths": [
            {"id": "vp-vault-withdraw", "label": "deposit -> withdraw",
             "entry_function": "Vault.withdraw", "exit_function": "Vault.withdraw",
             "assumptions": ["asm-oracle-fresh"], "review_priority": "high"},
        ],
        "assumptions": assumptions,
        "test_gaps": [
            {"id": "gap-vault-withdraw", "title": "withdraw under-collateralized",
             "related_function": "Vault.withdraw", "related_value_path": "vp-vault-withdraw",
             "suggested_test": "withdraw more than balance"},
        ],
        "proof_suggestions": [
            {"id": "proof-vault-withdraw", "target": "Vault.withdraw",
             "related_test_gap": "gap-vault-withdraw", "objective": "no overdraw"},
        ],
    }


class ReasoningLinkResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = linking.link_reasoning(build.build_protocol_model_from_review_map(_payload(), "/repo"))

    def test_test_gap_links_to_single_matching_assumption(self) -> None:
        gap = self.model.test_gaps[0]
        self.assertEqual(gap.linked_assumption_id, self.model.assumptions[0].assumption_id)

    def test_assumption_back_links_to_value_path(self) -> None:
        self.assertIn(self.model.value_paths[0].value_path_id,
                      self.model.assumptions[0].linked_value_path_ids)

    def test_test_gap_and_proof_suggestion_are_bidirectional(self) -> None:
        gap, ps = self.model.test_gaps[0], self.model.proof_suggestions[0]
        self.assertEqual(ps.linked_test_gap_id, gap.test_gap_id)
        self.assertEqual(gap.proof_suggestion_id, ps.proof_suggestion_id)


class NoOverlinkTests(unittest.TestCase):
    def test_ambiguous_assumption_leaves_test_gap_link_empty(self) -> None:
        extra = [{"id": "asm-oracle-bounds", "title": "Oracle bounded", "category": "oracle",
                  "used_by": ["Vault.withdraw"]}]
        model = linking.link_reasoning(build.build_protocol_model_from_review_map(_payload(extra), "/repo"))
        self.assertEqual(len(model.assumptions), 2)
        self.assertEqual(model.test_gaps[0].linked_assumption_id, "")

    def test_ambiguous_proof_suggestion_leaves_test_gap_empty(self) -> None:
        model = ProtocolModel(
            protocol_id="protocol:x",
            test_gaps=[TestGapNode(test_gap_id="test-gap:g")],
            proof_suggestions=[
                ProofSuggestionNode(proof_suggestion_id="proof-suggestion:a", linked_test_gap_id="test-gap:g"),
                ProofSuggestionNode(proof_suggestion_id="proof-suggestion:b", linked_test_gap_id="test-gap:g"),
            ],
        )
        linking.link_proof_suggestions_to_test_gaps(model)
        self.assertEqual(model.test_gaps[0].proof_suggestion_id, "")

    def test_test_gap_without_function_or_match_stays_empty(self) -> None:
        model = ProtocolModel(
            protocol_id="protocol:x",
            assumptions=[AssumptionNode(assumption_id="assumption:a", linked_function_ids=["function:x"])],
            test_gaps=[
                TestGapNode(test_gap_id="test-gap:nofn"),  # no linked_function_id
                TestGapNode(test_gap_id="test-gap:other", linked_function_id="function:y"),  # no match
            ],
        )
        linking.link_test_gaps_to_assumptions(model)
        self.assertEqual(model.test_gaps[0].linked_assumption_id, "")
        self.assertEqual(model.test_gaps[1].linked_assumption_id, "")


class IdempotenceAndDeterminismTests(unittest.TestCase):
    def test_linking_returns_same_model_object(self) -> None:
        model = build.build_protocol_model_from_review_map(_payload(), "/repo")
        self.assertIs(linking.link_reasoning(model), model)

    def test_linking_is_idempotent(self) -> None:
        model = build.build_protocol_model_from_review_map(_payload(), "/repo")
        once = build.protocol_model_to_dict(linking.link_reasoning(model))
        twice = build.protocol_model_to_dict(linking.link_reasoning(model))
        self.assertEqual(once, twice)

    def test_linking_is_deterministic_across_independent_models(self) -> None:
        m1 = linking.link_reasoning(build.build_protocol_model_from_review_map(_payload(), "/repo"))
        m2 = linking.link_reasoning(build.build_protocol_model_from_review_map(_payload(), "/repo"))
        self.assertEqual(build.protocol_model_to_dict(m1), build.protocol_model_to_dict(m2))

    def test_existing_fields_and_aliases_preserved(self) -> None:
        model = build.build_protocol_model_from_review_map(_payload(), "/repo")
        before_aliases = [dict(a.aliases) for a in model.assumptions]
        before_fids = [list(a.linked_function_ids) for a in model.assumptions]
        linking.link_reasoning(model)
        self.assertEqual([a.aliases for a in model.assumptions], before_aliases)
        self.assertEqual([a.linked_function_ids for a in model.assumptions], before_fids)


if __name__ == "__main__":
    unittest.main()
