"""Tests for linking v3.4 artifacts into the ProtocolModel (v3.5, Agent 6)."""
from __future__ import annotations

import copy
import unittest

from arkheionx.intelligence import build, linking

PROOF_PATH = "proof/Vault_withdraw/proof.json"
TRACE_PATH = "proof/Vault_withdraw/trace.json"
PROOF_RID = "proof:Vault_withdraw"
TRACE_RID = "trace:Vault_withdraw"
EVID_ID = "evidence:Vault_withdraw:abc123"
STABLE = "src/Vault.sol:Vault.withdraw(uint256)#L10-L20"
QUALIFIED = "src/Vault.sol:Vault.withdraw(uint256)"


def _base_model():
    payload = {
        "repo_path": "/repo",
        "functions": [
            {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)", "path": "src/Vault.sol"},
        ],
        "test_gaps": [
            {"id": "gap-vault-withdraw", "related_function": "Vault.withdraw", "suggested_test": "overdraw"},
        ],
        "proof_suggestions": [
            {"id": "proof-vault-withdraw", "target": "Vault.withdraw", "related_test_gap": "gap-vault-withdraw"},
        ],
    }
    return build.build_protocol_model_from_review_map(payload, "/repo")


def _proof():
    return {
        "proof_receipt_id": PROOF_RID, "target": QUALIFIED, "target_id": STABLE,
        "review_map_target": "Vault.withdraw", "related_test_gap": "gap-vault-withdraw",
        "proof_suggestion_id": "proof-vault-withdraw", "status": "tested_passed",
        "evidence_level": "EXECUTION_CONFIRMED",
        "test_result": {"raw_output_path": "proof/Vault_withdraw/raw.txt"},
        "trace": {"trace_json_path": TRACE_PATH, "summary_available": True},
    }


def _trace():
    return {
        "trace_receipt_id": TRACE_RID, "target": QUALIFIED, "target_id": STABLE,
        "review_map_target": "Vault.withdraw", "source_proof_json": PROOF_PATH,
        "status": "tested_passed", "evidence_level": "EXECUTION_CONFIRMED",
    }


def _evidence(with_trace=True):
    sources = [{"kind": "proof", "path": PROOF_PATH, "receipt_id": PROOF_RID, "review_map_target": "Vault.withdraw"}]
    if with_trace:
        sources.append({"kind": "trace", "path": TRACE_PATH, "receipt_id": TRACE_RID, "review_map_target": "Vault.withdraw"})
    level = "EVIDENCE_READY" if with_trace else "EXECUTION_CONFIRMED"
    readiness = "evidence_ready" if with_trace else "execution_confirmed"
    pid = EVID_ID if with_trace else "evidence:NoTrace:def456"
    return {
        "evidence_package_id": pid, "target": QUALIFIED, "target_id": STABLE,
        "evidence_level": level, "status": readiness,
        "manifest": {"package_id": pid, "readiness": readiness, "sources": sources},
        "source_artifacts": {"proof_json": PROOF_PATH, "trace_json": TRACE_PATH if with_trace else ""},
    }


def _report():
    return {
        "target": QUALIFIED, "title": "Arkheionx review draft: Vault.withdraw",
        "evidence_level": "EVIDENCE_READY", "status": "draft-created",
        "review_status": "NEEDS_HUMAN_REVIEW", "what_is_not_proven": ["exploitability", "final severity"],
        "evidence_context": {"evidence_package_id": EVID_ID, "review_status": "NEEDS_HUMAN_REVIEW",
                             "source_artifacts": {"report_json": "reports/Vault_withdraw/report.json"}},
        "receipt_references": {"evidence_package_id": EVID_ID, "proof_receipt_id": PROOF_RID, "trace_receipt_id": TRACE_RID},
        "report_readiness": {"status": "draft", "ready_for_submission": False, "requires_manual_review": True, "evidence_ready": True},
        "artifact_paths": {"report_json": "reports/Vault_withdraw/report.json"},
    }


def _evidence_links():
    return {"evidence_links": [{
        "id": "ev-proof-Vault_withdraw", "source": "proof", "artifact_kind": "proof",
        "artifact_path": PROOF_PATH, "target": "Vault.withdraw", "target_id": STABLE,
        "evidence_package_id": EVID_ID, "proof_receipt_id": PROOF_RID, "trace_receipt_id": TRACE_RID,
        "evidence_level": "EVIDENCE_READY", "readiness": "evidence_ready",
    }]}


class NodeCreationTests(unittest.TestCase):
    def test_proof_payload_creates_proof_receipt_node(self):
        model = _base_model()
        linking.link_proof_receipts_to_model(model, [_proof()])
        self.assertEqual(len(model.proof_receipts), 1)
        node = model.proof_receipts[0]
        self.assertEqual(node.proof_receipt_id, PROOF_RID)  # old id preserved
        self.assertEqual(node.target_function_id, model.functions[0].function_id)
        self.assertEqual(node.linked_proof_suggestion_id, model.proof_suggestions[0].proof_suggestion_id)
        self.assertEqual(node.evidence_level, "EXECUTION_CONFIRMED")  # unchanged

    def test_evidence_payload_creates_package_node_with_receipt_links(self):
        model = _base_model()
        linking.link_evidence_packages_to_model(model, [_evidence()])
        node = model.evidence_packages[0]
        self.assertEqual(node.evidence_package_id, EVID_ID)
        self.assertEqual(node.linked_proof_receipt_id, PROOF_RID)
        self.assertEqual(node.linked_trace_receipt_id, TRACE_RID)
        self.assertEqual(node.evidence_level, "EVIDENCE_READY")
        self.assertEqual(node.readiness, "evidence_ready")

    def test_report_payload_creates_report_draft_node(self):
        model = _base_model()
        linking.link_artifacts_to_protocol_model(model, evidence_packages=[_evidence()], reports=[_report()])
        node = model.report_drafts[0]
        self.assertEqual(node.linked_evidence_package_id, EVID_ID)
        self.assertEqual(node.linked_target_function_id, model.functions[0].function_id)
        self.assertEqual(node.review_status, "NEEDS_HUMAN_REVIEW")
        self.assertFalse(node.report_readiness["ready_for_submission"])
        self.assertNotIn("HUMAN_REVIEWED", node.review_status)

    def test_evidence_links_payload_creates_link_node(self):
        model = _base_model()
        linking.link_evidence_links_to_model(model, _evidence_links())
        node = model.evidence_links[0]
        self.assertEqual(node.aliases["id"], "ev-proof-Vault_withdraw")  # old id preserved
        self.assertEqual(node.linked_artifact_path, PROOF_PATH)
        self.assertEqual(node.linked_target_function_id, model.functions[0].function_id)


class TraceLinkTests(unittest.TestCase):
    def test_trace_links_to_proof_when_exact(self):
        model = _base_model()
        linking.link_artifacts_to_protocol_model(
            model, proofs=[_proof()], evidence_packages=[_evidence()], traces=[_trace()])
        node = model.trace_receipts[0]
        self.assertEqual(node.trace_receipt_id, TRACE_RID)
        self.assertEqual(node.linked_proof_receipt_id, PROOF_RID)

    def test_trace_without_proof_is_not_invented(self):
        model = _base_model()
        linking.link_trace_receipts_to_model(model, [_trace()])
        self.assertEqual(model.trace_receipts[0].linked_proof_receipt_id, "")


class ContractPreservationTests(unittest.TestCase):
    def test_evidence_without_trace_stays_execution_confirmed(self):
        model = _base_model()
        linking.link_evidence_packages_to_model(model, [_evidence(with_trace=False)])
        node = model.evidence_packages[0]
        self.assertEqual(node.evidence_level, "EXECUTION_CONFIRMED")  # never promoted
        self.assertEqual(node.linked_trace_receipt_id, "")  # no trace link invented
        self.assertEqual(node.readiness, "execution_confirmed")

    def test_linking_is_additive_only(self):
        model = _base_model()
        before = (len(model.functions), len(model.proof_suggestions),
                  model.functions[0].function_id, model.proof_suggestions[0].proof_suggestion_id)
        linking.link_artifacts_to_protocol_model(
            model, proofs=[_proof()], traces=[_trace()], evidence_packages=[_evidence()],
            reports=[_report()], evidence_links=_evidence_links())
        after = (len(model.functions), len(model.proof_suggestions),
                 model.functions[0].function_id, model.proof_suggestions[0].proof_suggestion_id)
        self.assertEqual(before, after)


class NoOverlinkTests(unittest.TestCase):
    def test_ambiguous_target_is_not_resolved(self):
        payload = {"functions": [
            {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)"},
            {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256,address)"},
        ]}
        model = build.build_protocol_model_from_review_map(payload, "/repo")
        proof = {"proof_receipt_id": PROOF_RID, "review_map_target": "Vault.withdraw", "target": "Vault.withdraw"}
        linking.link_proof_receipts_to_model(model, [proof])
        self.assertEqual(model.proof_receipts[0].target_function_id, "")


class DeterminismAndPurityTests(unittest.TestCase):
    def _link_all(self, model):
        return linking.link_artifacts_to_protocol_model(
            model, proofs=[_proof()], traces=[_trace()], evidence_packages=[_evidence()],
            reports=[_report()], evidence_links=_evidence_links())

    def test_determinism_across_independent_models(self):
        m1 = self._link_all(_base_model())
        m2 = self._link_all(_base_model())
        self.assertEqual(build.protocol_model_to_dict(m1), build.protocol_model_to_dict(m2))

    def test_idempotent_relinking(self):
        model = _base_model()
        once = build.protocol_model_to_dict(self._link_all(model))
        twice = build.protocol_model_to_dict(self._link_all(model))
        self.assertEqual(once, twice)
        self.assertEqual(len(model.proof_receipts), 1)
        self.assertEqual(len(model.evidence_packages), 1)

    def test_no_mutation_of_input_payloads(self):
        artifacts = {"proofs": [_proof()], "traces": [_trace()], "evidence_packages": [_evidence()],
                     "reports": [_report()], "evidence_links": _evidence_links()}
        original = copy.deepcopy(artifacts)
        linking.link_artifacts_to_protocol_model(_base_model(), **artifacts)
        self.assertEqual(artifacts, original)


if __name__ == "__main__":
    unittest.main()
