from arkheionx.attack.models import AttackCandidate, AttackGraph
from arkheionx.severity import models as S


def candidate(family: str, **kwargs):
    defaults = {
        "id": "AC-GENERIC",
        "invariant_family": family,
        "attacker_capability": "unprivileged user",
        "victim": "value provider",
        "asset": "generic asset",
        "broken_invariant": "authorization or accounting invariant",
        "entry_function": "GenericContract.execute",
    }
    defaults.update(kwargs)
    return AttackCandidate(**defaults)


def severity(candidate_id="AC-GENERIC", **kwargs):
    defaults = {
        "candidate_id": candidate_id,
        "label": S.SUBMIT_HIGH_CANDIDATE,
        "cap_type": S.UNCAPPED,
        "proof_quality": S.LOCAL_POC_PASSING,
        "impact_type": S.VICTIM_LOSS,
    }
    defaults.update(kwargs)
    return S.SeverityVerdict(**defaults)


def graph(item):
    return AttackGraph(root="generic", candidates=[item])
