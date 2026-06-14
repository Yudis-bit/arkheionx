"""Attack-graph structure + renderers (09 of the war-run).

The attack graph expresses, per candidate, the chain:
attacker capability -> entry function -> call/influence path -> broken invariant
-> impact -> proof strategy.
"""
from __future__ import annotations


def attack_graph_json(graph) -> dict:
    payload = graph.to_dict()
    chains = []
    for c in graph.candidates:
        chains.append({
            "candidate_id": c.id,
            "chain": [
                {"node": "attacker_capability", "value": c.attacker_capability},
                {"node": "entry_function", "value": c.entry_function},
                {"node": "call_sequence", "value": c.call_sequence},
                {"node": "broken_invariant", "value": c.invariant_family},
                {"node": "impact", "value": f"{c.victim} loses {c.asset}"},
                {"node": "proof_strategy", "value": c.proof_strategy},
            ],
            "fork_required": c.fork_requirement,
            "rank_score": c.rank_score,
        })
    payload["chains"] = chains
    return payload


def attack_graph_md(graph) -> str:
    lines = [
        "# 09 Attack Graph",
        "",
        f"{len(graph.candidates)} attack candidates derived from suspicious invariants",
        "and role-gated value paths. A candidate is a research direction with a proof",
        "strategy, not a confirmed exploit.",
        "",
    ]
    for c in graph.candidates:
        lines += [
            f"## {c.id} {c.title}",
            f"- Root cause: {c.root_cause}",
            f"- Broken invariant: {c.invariant_family}",
            f"- Attacker -> Victim: {c.attacker_capability} -> {c.victim} ({c.asset})",
            f"- Entry: {c.entry_function}",
            f"- Chain: " + (" | ".join(c.call_sequence) if c.call_sequence else "(single function)"),
            f"- Proof: {c.proof_strategy}" + (" (FORK REQUIRED)" if c.fork_requirement else ""),
            f"- Rank score: {c.rank_score}",
            "",
        ]
    return "\n".join(lines) + "\n"
