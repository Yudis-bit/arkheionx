"""V10 semantic core: call-graph precision (fallback mode)."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import models as M

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _fixture(name):
    return _GODEYE / name


class SemanticCallGraphTest(unittest.TestCase):
    def setUp(self):
        self.smap = build_semantic_map(_fixture("loan_repay_rounding_fixture"))

    def test_internal_edge_repay_to_distribute(self):
        edges = {(e.caller, e.callee, e.kind) for e in self.smap.call_edges}
        self.assertIn(("LoanRouter.repay", "LoanRouter._distribute", M.CALL_INTERNAL), edges)
        self.assertIn(("LoanRouter._distribute", "LoanRouter._totalPrincipal", M.CALL_INTERNAL), edges)

    def test_interface_edge_to_token_transfer(self):
        callees = {e.callee for e in self.smap.call_edges}
        # _distribute calls asset.transfer; transfer is a known IERC20 function.
        self.assertTrue(any(c.endswith(".transfer") for c in callees))

    def test_no_fabricated_edges(self):
        for e in self.smap.call_edges:
            self.assertTrue(e.caller and "." in e.caller, f"bad caller {e.caller!r}")
            self.assertTrue(e.callee, "empty callee")
            self.assertIn(e.kind, (M.CALL_INTERNAL, M.CALL_INTERFACE, M.CALL_EXTERNAL,
                                   M.CALL_LOWLEVEL, M.CALL_LIBRARY))
            # require/if/for must never appear as callees.
            self.assertNotIn(e.callee.split(".")[-1], ("require", "if", "for", "while", "emit"))

    def test_call_graph_json_shape(self):
        from arkheionx.semantic import renderer
        cg = renderer.call_graph_json(self.smap)
        self.assertEqual(cg["artifact_type"], "semantic_call_graph")
        self.assertEqual(cg["edge_count"], len(self.smap.call_edges))


if __name__ == "__main__":
    unittest.main()
