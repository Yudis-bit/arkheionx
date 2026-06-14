"""V10 memory: dedup classification (same vs distinct root cause)."""
import tempfile
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.memory import MemoryStore, MemoryEntry, duplicate_classifier
from arkheionx.memory import models as MM

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _graph(name):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    return ranking.rank(build_candidates(smap, emap, tmap, invset))


class DedupTest(unittest.TestCase):
    def test_repeating_567_logic_is_same_root_cause(self):
        with tempfile.TemporaryDirectory() as d:
            store = MemoryStore(Path(d) / "memory")
            store.add("findings", MemoryEntry(
                target="DemoCredit", invariant_family="DEBT_REPAYMENT_RECONCILIATION",
                function_role="repay", attacker_category="borrower",
                status=MM.SUBMITTED, finding_id="#567"))
            graph = _graph("loan_repay_rounding_fixture")
            duplicate_classifier.annotate(graph, store)
            recon = next(c for c in graph.candidates
                         if c.invariant_family == "DEBT_REPAYMENT_RECONCILIATION")
            self.assertEqual(recon.duplicate_risk, MM.SAME_ROOT_CAUSE)

    def test_route_buffer_after_567_is_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            store = MemoryStore(Path(d) / "memory")
            store.add("findings", MemoryEntry(
                target="DemoCredit", invariant_family="DEBT_REPAYMENT_RECONCILIATION",
                function_role="repay", attacker_category="borrower",
                status=MM.SUBMITTED, finding_id="#567"))
            graph = _graph("borrow_swapdata_consent_fixture")
            duplicate_classifier.annotate(graph, store)
            consent = next(c for c in graph.candidates
                           if c.invariant_family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
            self.assertEqual(consent.duplicate_risk, MM.DISTINCT)

    def test_route_buffer_variant_different_pool_is_same(self):
        with tempfile.TemporaryDirectory() as d:
            store = MemoryStore(Path(d) / "memory")
            store.add("findings", MemoryEntry(
                target="OtherPool", invariant_family="LENDER_CONSENT_VALUE_AFFECTING_CALLDATA",
                function_role="borrow", attacker_category="borrower", status=MM.SUBMITTED))
            graph = _graph("borrow_swapdata_consent_fixture")
            duplicate_classifier.annotate(graph, store)
            consent = next(c for c in graph.candidates
                           if c.invariant_family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
            self.assertEqual(consent.duplicate_risk, MM.SAME_ROOT_CAUSE)

    def test_unknown_without_memory(self):
        with tempfile.TemporaryDirectory() as d:
            store = MemoryStore(Path(d) / "memory")  # empty
            graph = _graph("loan_repay_rounding_fixture")
            duplicate_classifier.annotate(graph, store)
            for c in graph.candidates:
                self.assertEqual(c.duplicate_risk, MM.DUP_UNKNOWN)

    def test_store_roundtrip_persists_hash(self):
        with tempfile.TemporaryDirectory() as d:
            store = MemoryStore(Path(d) / "memory")
            store.add("killed", MemoryEntry(
                invariant_family="DEPOSIT_CONSUMPTION", function_role="consume",
                attacker_category="user", status=MM.KILLED))
            store2 = MemoryStore(Path(d) / "memory")
            hashes = store2.known_hashes()
            self.assertEqual(len(hashes), 1)


if __name__ == "__main__":
    unittest.main()
