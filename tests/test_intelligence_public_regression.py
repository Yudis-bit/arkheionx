"""Public-surface + safety regression for the intelligence layer (v3.5, Agent 7).

The internal intelligence layer must stay additive: version metadata is
unchanged, no CLI command is added, building/linking writes nothing, and the
v3.4 safety contract (trace-bounded readiness, manual-review-only reports, no
auto HUMAN_REVIEWED / submission readiness) is preserved. Authoritative CLI/JSON
checks live in tests.test_public_workflow and tests.test_evidence; these are the
fast model-level regressions.
"""
from __future__ import annotations

import argparse
import copy
import os
import unittest

from arkheionx import version
from arkheionx.intelligence import build, linking
from arkheionx.intelligence.model import HUMAN_REVIEWED


def _commands() -> list[str]:
    from arkheionx.cli.main import build_parser

    for action in build_parser()._actions:
        if isinstance(action, argparse._SubParsersAction):
            return list(action.choices.keys())
    return []


class MetadataUnchangedTests(unittest.TestCase):
    def test_version_metadata_is_frozen(self) -> None:
        self.assertEqual(version.PACKAGE_VERSION, "9.1.0.dev0")
        self.assertEqual(version.STABLE_RELEASE, "v8.0.1")
        self.assertEqual(version.CURRENT_MILESTONE, "v9.1.0-dev")
        self.assertEqual(version.NEXT_MILESTONE, "v9.1.0")


class NoNewCommandTests(unittest.TestCase):
    def test_intelligence_adds_no_cli_command(self) -> None:
        commands = _commands()
        for command in commands:
            self.assertNotIn("intelligence", command)
            self.assertNotIn("protocol-model", command)
        # Existing public commands remain present.
        for command in ("review-map", "evidence", "report", "evidence-links"):
            self.assertIn(command, commands)


class ReadOnlyTests(unittest.TestCase):
    def test_build_and_link_write_no_files(self) -> None:
        tmp = os.path.join(os.getcwd(), ".arkheionx-agent7-tmp")
        os.makedirs(tmp, exist_ok=True)
        try:
            before = sorted(os.listdir(tmp))
            model = build.build_protocol_model_from_review_map(
                {"functions": [{"contract": "V", "name": "f", "signature": "f()"}]}, tmp)
            linking.link_artifacts_to_protocol_model(
                model, evidence_links={"evidence_links": [{"id": "ev-x", "source": "proof", "target": "V.f"}]})
            self.assertEqual(sorted(os.listdir(tmp)), before)  # read-only contract
        finally:
            os.rmdir(tmp)

    def test_evidence_links_input_not_mutated(self) -> None:
        payload = {"evidence_links": [{"id": "ev-x", "source": "proof", "target": "V.f"}]}
        original = copy.deepcopy(payload)
        model = build.build_protocol_model_from_review_map(
            {"functions": [{"contract": "V", "name": "f", "signature": "f()"}]}, "/repo")
        linking.link_evidence_links_to_model(model, payload)
        self.assertEqual(payload, original)


class SafetyContractTests(unittest.TestCase):
    def _model(self):
        return build.build_protocol_model_from_review_map(
            {"functions": [{"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)"}]}, "/repo")

    def test_report_defaults_to_manual_review_and_never_auto_submits(self) -> None:
        model = self._model()
        linking.link_report_drafts_to_model(model, [{"target": "Vault.withdraw"}])  # no review_status/readiness
        node = model.report_drafts[0]
        self.assertEqual(node.review_status, "NEEDS_HUMAN_REVIEW")
        self.assertNotIn(HUMAN_REVIEWED, node.review_status)
        self.assertEqual(node.report_readiness, {})  # ready_for_submission not invented

    def test_report_readiness_preserved_not_promoted(self) -> None:
        model = self._model()
        readiness = {"ready_for_submission": False, "requires_manual_review": True}
        linking.link_report_drafts_to_model(
            model, [{"target": "Vault.withdraw", "report_readiness": dict(readiness)}])
        self.assertEqual(model.report_drafts[0].report_readiness, readiness)

    def test_evidence_without_trace_is_not_promoted(self) -> None:
        model = self._model()
        linking.link_evidence_packages_to_model(model, [{
            "evidence_package_id": "evidence:nt", "evidence_level": "EXECUTION_CONFIRMED",
            "manifest": {"sources": [{"kind": "proof", "path": "p.json", "receipt_id": "proof:x"}]},
        }])
        node = model.evidence_packages[0]
        self.assertEqual(node.evidence_level, "EXECUTION_CONFIRMED")  # never raised to EVIDENCE_READY
        self.assertEqual(node.linked_trace_receipt_id, "")  # no trace link fabricated

    def test_no_node_auto_emits_human_reviewed(self) -> None:
        model = self._model()
        linking.link_artifacts_to_protocol_model(
            model, reports=[{"target": "Vault.withdraw", "review_status": "NEEDS_HUMAN_REVIEW"}])
        self.assertTrue(all(n.review_status != HUMAN_REVIEWED for n in model.report_drafts))


if __name__ == "__main__":
    unittest.main()
