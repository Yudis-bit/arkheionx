"""Tests for protocol intelligence dataclasses (v3.5, internal)."""
from __future__ import annotations

import unittest

from arkheionx.intelligence import model


class ProtocolModelDataclassTests(unittest.TestCase):
    def test_nodes_default_aliases_and_metadata_to_empty_dicts(self) -> None:
        c = model.ContractNode(contract_id="contract:1:vault")
        f = model.FunctionNode(function_id="function:vault:1")
        self.assertEqual(c.aliases, {})
        self.assertEqual(c.metadata, {})
        self.assertEqual(f.aliases, {})
        self.assertEqual(f.metadata, {})

    def test_protocol_model_serializes_to_plain_dict(self) -> None:
        pm = model.ProtocolModel(
            protocol_id="protocol:abc",
            contracts=[model.ContractNode(contract_id="contract:1:vault", name="Vault")],
            functions=[model.FunctionNode(function_id="function:vault:1", display_name="Vault.deposit")],
        )
        data = pm.to_dict()
        self.assertIsInstance(data, dict)
        for section in (
            "contracts", "functions", "value_paths", "assumptions", "test_gaps",
            "proof_suggestions", "proof_receipts", "trace_receipts",
            "evidence_packages", "report_drafts", "evidence_links",
        ):
            self.assertIn(section, data)
        self.assertEqual(data["contracts"][0]["name"], "Vault")
        self.assertEqual(data["functions"][0]["display_name"], "Vault.deposit")

    def test_generated_at_defaults_to_empty(self) -> None:
        pm = model.ProtocolModel(protocol_id="protocol:abc")
        self.assertEqual(pm.generated_at, "")
        self.assertEqual(pm.schema_version, model.SCHEMA_VERSION)

    def test_to_dict_helper_handles_lists_and_scalars(self) -> None:
        nodes = [model.AssumptionNode(assumption_id="assumption:oracle:1")]
        self.assertEqual(model.to_dict(nodes)[0]["assumption_id"], "assumption:oracle:1")
        self.assertEqual(model.to_dict("x"), "x")


if __name__ == "__main__":
    unittest.main()
