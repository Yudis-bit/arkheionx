"""Render bounty-reality artifacts."""
from __future__ import annotations


def reality_json(results) -> dict:
    blocked = [item for item in results if item.blocked]
    return {
        "schema_version": "v10.1-bounty-reality",
        "artifact_type": "bounty_reality",
        "candidate_count": len(results),
        "blocked_count": len(blocked),
        "results": [item.to_dict() for item in results],
    }


def reality_md(results) -> str:
    lines = [
        "# Bounty Reality Gate",
        "",
        "Technical validity and bounty relevance are separate decisions.",
        "",
        "| Candidate | Family | Verdict | Final | Recommendation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in results:
        lines.append(
            f"| {item.candidate_id or '-'} | {item.family} | {item.verdict} | "
            f"{item.final_verdict} | {item.submit_recommendation} |"
        )
    if not results:
        lines.append("| - | - | HUMAN_REVIEW_REQUIRED | HUMAN_REVIEW_REQUIRED | HUMAN_REVIEW |")
    return "\n".join(lines) + "\n"
