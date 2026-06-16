import unittest

from pathlib import Path

from arkheionx.severity import models as S
from arkheionx.warrun import run_war_run


class GenericBindingBugRepositoryTest(unittest.TestCase):
    def test_binding_bug_is_promoted_for_proof(self):
        root = Path(__file__).resolve().parents[1] / "fixtures" / "repos" / "generic_signature_binding_bug"
        result = run_war_run(root, write=False)
        candidate = next(
            item for item in result["graph"].candidates
            if item.invariant_family == "SIGNATURE_OPERATION_BINDING"
        )
        self.assertIn(candidate.economic_severity, (
            S.SUBMIT_HIGH_CANDIDATE,
            S.SUBMIT_CRITICAL_CANDIDATE,
        ))


if __name__ == "__main__":
    unittest.main()
