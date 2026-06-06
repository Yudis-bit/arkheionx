"""Tests for the internal ProtocolModel builder (v3.5, Agent 3)."""
from __future__ import annotations

import copy
import json
import unittest
from types import SimpleNamespace

from arkheionx.intelligence import build


def _analysis_fixture() -> SimpleNamespace:
    contract = SimpleNamespace(
        contract_name="Vault",
        file_path="src/Vault.sol",
        role="Value Holder",
        confidence="high",
        evidence_level="HEURISTIC",
        value_state_vars=["totalAssets"],
        source_kind="production",
    )
    function = SimpleNamespace(
        contract_name="Vault",
        function_name="withdraw",
        signature="withdraw(uint256)",
        visibility="external",
        role="Money Exit",
        file_path="src/Vault.sol",
        line_range=[10, 20],
        display_id="Vault.withdraw",
        qualified_id="src/Vault.sol:Vault.withdraw(uint256)",
        stable_id="src/Vault.sol:Vault.withdraw(uint256)#L10-L20",
        function_id="",
    )
    return SimpleNamespace(contracts=[contract], functions=[function])


def _review_map_payload() -> dict:
    return {
        "repo_path": "/repo",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "contracts": [
            {"name": "Vault", "path": "src/Vault.sol", "kind": "production",
             "roles": ["Value Holder"], "value_sensitive": True},
        ],
        "functions": [
            {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)",
             "mutability": "nonpayable", "path": "src/Vault.sol", "line": 10,
             "value_direction": "out", "risk_signals": ["value-out"]},
        ],
        "value_paths": [
            {"id": "vp-vault-withdraw", "label": "Vault: deposit -> withdraw",
             "entry_function": "Vault.withdraw", "exit_function": "Vault.withdraw",
             "assets": ["asset"], "conditions": ["balance check"],
             "assumptions": ["asm-oracle-fresh"], "review_priority": "high"},
        ],
        "assumptions": [
            {"id": "asm-oracle-fresh", "title": "Oracle is fresh", "category": "oracle",
             "used_by": ["Vault.withdraw"], "evidence_level": "HEURISTIC", "status": "unverified"},
        ],
        "test_gaps": [
            {"id": "gap-vault-withdraw", "title": "withdraw under-collateralized",
             "related_function": "Vault.withdraw", "related_value_path": "vp-vault-withdraw",
             "suggested_test": "withdraw more than balance", "confidence": "high"},
        ],
        "proof_suggestions": [
            {"id": "proof-vault-withdraw", "target": "Vault.withdraw", "objective": "no overdraw",
             "setup": ["deploy"], "action": "call withdraw", "assertions": ["revert"],
             "related_test_gap": "gap-vault-withdraw", "related_assumption": "asm-oracle-fresh"},
        ],
        "evidence_links": [
            {"id": "ev-proof-vault_withdraw", "source": "proof", "artifact_kind": "proof",
             "artifact_path": ".arkheionx/out/proof/vault_withdraw/proof.json",
             "target": "Vault.withdraw", "target_id": "src/Vault.sol:Vault.withdraw(uint256)#L10-L20",
             "evidence_package_id": "evidence:pkg123", "proof_receipt_id": "proof:vault_withdraw",
             "trace_receipt_id": "trace:vault_withdraw", "readiness": "evidence_ready"},
        ],
    }


class BuildFromAnalysisTests(unittest.TestCase):
    def test_minimal_model_from_analysis_like_objects(self) -> None:
        model = build.build_protocol_model_from_analysis(_analysis_fixture(), "/repo")
        self.assertTrue(model.protocol_id.startswith("protocol:"))
        self.assertEqual(len(model.contracts), 1)
        self.assertEqual(len(model.functions), 1)
        contract = model.contracts[0]
        function = model.functions[0]
        self.assertTrue(contract.contract_id.startswith("contract:"))
        self.assertTrue(function.function_id.startswith("function:"))
        # Deterministic IDs for identical input.
        again = build.build_protocol_model_from_analysis(_analysis_fixture(), "/repo")
        self.assertEqual(contract.contract_id, again.contracts[0].contract_id)
        self.assertEqual(function.function_id, again.functions[0].function_id)
        # Legacy aliases preserved.
        self.assertEqual(function.aliases["display_id"], "Vault.withdraw")
        self.assertEqual(function.aliases["stable_id"], "src/Vault.sol:Vault.withdraw(uint256)#L10-L20")
        self.assertEqual(function.aliases["target_id"], function.aliases["stable_id"])
        self.assertEqual(function.aliases["qualified_id"], "src/Vault.sol:Vault.withdraw(uint256)")
        self.assertEqual(contract.aliases["contract_name"], "Vault")
        self.assertTrue(contract.value_holding)

    def test_missing_signature_records_uncertainty(self) -> None:
        analysis = SimpleNamespace(
            contracts=[SimpleNamespace(contract_name="C", file_path="src/C.sol")],
            functions=[SimpleNamespace(contract_name="C", function_name="f", file_path="src/C.sol")],
        )
        model = build.build_protocol_model_from_analysis(analysis, "/repo")
        function = model.functions[0]
        self.assertEqual(function.signature, "C.f")
        self.assertEqual(function.metadata["signature_source"], "display_name")
        self.assertEqual(function.metadata["signature_confidence"], "low")


class BuildFromReviewMapTests(unittest.TestCase):
    def test_each_section_maps_to_its_node_type(self) -> None:
        model = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        self.assertEqual(len(model.contracts), 1)
        self.assertEqual(len(model.functions), 1)
        self.assertEqual(len(model.value_paths), 1)
        self.assertEqual(len(model.assumptions), 1)
        self.assertEqual(len(model.test_gaps), 1)
        self.assertEqual(len(model.proof_suggestions), 1)
        self.assertEqual(len(model.evidence_links), 1)
        # Receipt node lists stay empty (Agent 6 territory).
        self.assertEqual(model.proof_receipts, [])
        self.assertEqual(model.trace_receipts, [])
        self.assertEqual(model.evidence_packages, [])
        self.assertEqual(model.report_drafts, [])

    def test_old_ids_preserved_as_aliases(self) -> None:
        model = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        self.assertEqual(model.value_paths[0].aliases["id"], "vp-vault-withdraw")
        self.assertEqual(model.assumptions[0].aliases["id"], "asm-oracle-fresh")
        self.assertEqual(model.test_gaps[0].aliases["id"], "gap-vault-withdraw")
        self.assertEqual(model.proof_suggestions[0].aliases["id"], "proof-vault-withdraw")
        self.assertEqual(model.evidence_links[0].aliases["id"], "ev-proof-vault_withdraw")

    def test_links_resolve_to_function_ids(self) -> None:
        model = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        fid = model.functions[0].function_id
        self.assertEqual(model.value_paths[0].exit_function_id, fid)
        self.assertEqual(model.assumptions[0].linked_function_ids, [fid])
        self.assertEqual(model.test_gaps[0].linked_function_id, fid)
        self.assertEqual(model.proof_suggestions[0].target_function_id, fid)
        self.assertEqual(model.evidence_links[0].linked_target_function_id, fid)
        # Cross-links between nodes use new IDs.
        self.assertEqual(model.proof_suggestions[0].linked_test_gap_id, model.test_gaps[0].test_gap_id)
        self.assertEqual(model.test_gaps[0].proof_suggestion_id, model.proof_suggestions[0].proof_suggestion_id)
        self.assertEqual(model.value_paths[0].assumptions, [model.assumptions[0].assumption_id])

    def test_receipt_ids_preserved_without_fabricating_nodes(self) -> None:
        link = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo").evidence_links[0]
        self.assertEqual(link.evidence_package_id, "evidence:pkg123")
        self.assertEqual(link.proof_receipt_id, "proof:vault_withdraw")
        self.assertEqual(link.trace_receipt_id, "trace:vault_withdraw")
        self.assertEqual(link.report_id, "")  # not present -> not fabricated

    def test_unresolved_links_stay_empty(self) -> None:
        payload = {
            "functions": [],
            "value_paths": [{"id": "vp-x", "entry_function": "external caller", "exit_function": "Ghost.fn"}],
        }
        model = build.build_protocol_model_from_review_map(payload, "/repo")
        self.assertEqual(model.value_paths[0].entry_function_id, "")
        self.assertEqual(model.value_paths[0].exit_function_id, "")


class ResolveFunctionIdTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        self.fid = self.model.functions[0].function_id

    def test_resolve_by_function_id(self) -> None:
        self.assertEqual(build.resolve_function_id_by_alias(self.model, self.fid), self.fid)

    def test_resolve_by_display_name(self) -> None:
        self.assertEqual(build.resolve_function_id_by_alias(self.model, "Vault.withdraw"), self.fid)

    def test_resolve_by_legacy_alias(self) -> None:
        self.assertEqual(build.resolve_function_id_by_alias(self.model, "Vault.withdraw"), self.fid)
        # review_map_target alias holds the display target as well.
        self.assertIn("Vault.withdraw", self.model.functions[0].aliases.values())

    def test_resolve_by_signature(self) -> None:
        self.assertEqual(build.resolve_function_id_by_alias(self.model, "withdraw(uint256)"), self.fid)

    def test_missing_alias_returns_empty(self) -> None:
        self.assertEqual(build.resolve_function_id_by_alias(self.model, ""), "")
        self.assertEqual(build.resolve_function_id_by_alias(self.model, "Nope.gone"), "")

    def test_ambiguous_alias_returns_empty(self) -> None:
        payload = {"functions": [
            {"contract": "A", "name": "f", "signature": "g()"},
            {"contract": "B", "name": "h", "signature": "g()"},
        ]}
        model = build.build_protocol_model_from_review_map(payload, "/repo")
        self.assertEqual(build.resolve_function_id_by_alias(model, "g()"), "")

    def test_index_functions_by_alias(self) -> None:
        index = build.index_functions_by_alias(self.model)
        self.assertEqual(index["Vault.withdraw"], [self.fid])
        self.assertEqual(index[self.fid], [self.fid])


class DeterminismAndPurityTests(unittest.TestCase):
    def test_to_dict_deterministic_for_same_input(self) -> None:
        m1 = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        m2 = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        self.assertEqual(build.protocol_model_to_dict(m1), build.protocol_model_to_dict(m2))

    def test_no_mutation_of_input(self) -> None:
        payload = _review_map_payload()
        original = copy.deepcopy(payload)
        build.build_protocol_model_from_review_map(payload, "/repo")
        self.assertEqual(payload, original)

    def test_serialization_is_plain_json(self) -> None:
        model = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        data = build.protocol_model_to_dict(model)
        self.assertIsInstance(data, dict)
        # Round-trips through json without custom encoders.
        reloaded = json.loads(json.dumps(data))
        for section in ("contracts", "functions", "value_paths", "assumptions",
                        "test_gaps", "proof_suggestions", "evidence_links"):
            self.assertIn(section, reloaded)

    def test_generated_at_not_invented(self) -> None:
        # Analysis fixture has no generated_at -> stays empty (no timestamp inserted).
        model = build.build_protocol_model_from_analysis(_analysis_fixture(), "/repo")
        self.assertEqual(model.generated_at, "")
        # Review-map payload carries one -> preserved verbatim.
        rm_model = build.build_protocol_model_from_review_map(_review_map_payload(), "/repo")
        self.assertEqual(rm_model.generated_at, "2026-01-01T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
