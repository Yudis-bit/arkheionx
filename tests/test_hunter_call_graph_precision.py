"""Tests for hunter call-graph precision (no fake edges)."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def edges(name):
    b = FX / name
    res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
    return res["pack"].call_edges


class CallGraphPrecisionTests(unittest.TestCase):
    def test_real_direct_call_edge_present(self) -> None:
        es = edges("call_graph_spurious")
        self.assertTrue(any(e.caller == "Graph.process" and e.callee == "Graph.settle"
                            and e.status == M.DIRECT_CALL for e in es),
                        f"expected Graph.process -> Graph.settle DIRECT_CALL, got {[(e.caller, e.callee, e.status) for e in es]}")

    def test_spurious_edge_absent(self) -> None:
        es = edges("call_graph_spurious")
        # audit() mentions 'report' in a comment and uses reportCount, but never calls report().
        self.assertFalse(any(e.caller == "Graph.audit" and "report" in e.callee for e in es),
                         "a shared word / comment must not create a call edge")

    def test_only_real_edge_statuses(self) -> None:
        es = edges("call_graph_spurious")
        for e in es:
            self.assertIn(e.status, M.REAL_CALL_EDGES)

    def test_low_level_call_edges_when_present(self) -> None:
        # The bridge fixture uses interface/transfer calls; edges must be real statuses only.
        es = edges("bridge_domain_replay")
        for e in es:
            self.assertIn(e.status, M.REAL_CALL_EDGES)


if __name__ == "__main__":
    unittest.main()
