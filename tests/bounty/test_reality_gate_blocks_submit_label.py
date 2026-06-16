import unittest

from arkheionx.bounty.models import BountyRealityInput
from arkheionx.bounty.reality_gate import enforce_results, evaluate
from arkheionx.severity import models as S

from ._helpers import candidate, graph, severity


class RealityGateSubmitEnforcementTest(unittest.TestCase):
    def test_blocked_candidate_cannot_keep_submit_label(self):
        item = candidate(
            "OFFCHAIN_VALIDATION_OMISSION",
            economic_severity=S.SUBMIT_HIGH_CANDIDATE,
        )
        verdict = severity()
        reality = evaluate(BountyRealityInput(
            attack_candidate=item,
            severity_result=verdict,
        ))
        changed = enforce_results(graph(item), [verdict], [reality])
        self.assertTrue(changed)
        self.assertNotIn(item.economic_severity, S.SUBMIT_LABELS)
        self.assertNotIn(verdict.label, S.SUBMIT_LABELS)


if __name__ == "__main__":
    unittest.main()
