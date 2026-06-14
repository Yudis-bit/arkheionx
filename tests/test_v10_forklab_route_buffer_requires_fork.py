"""V10 fork lab: route-buffer candidate requires a fork plan (no keys, no broadcast)."""
import unittest
from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.defi import build_defi_entities
from arkheionx.state import build_transitions
from arkheionx.invariants import build_invariants
from arkheionx.attack import build_candidates, ranking
from arkheionx.severity import apply_gate
from arkheionx.forklab import build_fork_plan, renderer

_GODEYE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "godeye"


def _plan(name, scope=None):
    smap = build_semantic_map(_GODEYE / name)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)
    graph = ranking.rank(build_candidates(smap, emap, tmap, invset))
    apply_gate(graph)
    return graph, build_fork_plan(graph, smap, scope)


class RouteBufferForkTest(unittest.TestCase):
    def test_consent_candidate_requires_fork(self):
        graph, reqs = _plan("borrow_swapdata_consent_fixture")
        consent = next(c for c in graph.candidates
                       if c.invariant_family == "LENDER_CONSENT_VALUE_AFFECTING_CALLDATA")
        req = next(r for r in reqs if r.candidate_id == consent.id)
        self.assertIn("liquidity", req.reason.lower())
        self.assertTrue(req.do_not_broadcast)
        self.assertTrue(req.secret_redaction_required)

    def test_chain_inferred_from_scope_env_name(self):
        _, reqs = _plan("borrow_swapdata_consent_fixture", scope={"chain": "arbitrum"})
        self.assertTrue(reqs)
        self.assertIn("ARBITRUM_RPC_URL", reqs[0].required_env)

    def test_local_only_fixtures_have_no_fork_requirement(self):
        graph, reqs = _plan("deposit_double_use_fixture")
        self.assertEqual(reqs, [])


class NoPrivateKeyTest(unittest.TestCase):
    def test_no_private_key_in_required_env(self):
        _, reqs = _plan("borrow_swapdata_consent_fixture", scope={"chain": "arbitrum"})
        for r in reqs:
            for env in r.required_env:
                self.assertNotIn("PRIVATE", env.upper())
                self.assertNotIn("KEY", env.upper())
                self.assertTrue(env.endswith("RPC_URL"))

    def test_rendered_plan_has_no_url_and_marks_no_keys(self):
        graph, reqs = _plan("borrow_swapdata_consent_fixture", scope={"chain": "arbitrum"})
        md = renderer.fork_plan_md(reqs)
        self.assertNotIn("http://", md)
        self.assertNotIn("https://", md)
        js = renderer.fork_requirements_json(reqs)
        self.assertTrue(js["no_signing_keys_required"])
        self.assertTrue(js["do_not_broadcast"])


if __name__ == "__main__":
    unittest.main()
