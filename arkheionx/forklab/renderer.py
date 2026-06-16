"""Renderers for the fork plan (12) — always redacted."""
from __future__ import annotations

from . import env_detect, secret_redaction, test_plan


def fork_requirements_json(reqs) -> dict:
    return {
        "schema_version": "v10-fork-plan",
        "requirement_count": len(reqs),
        "do_not_broadcast": True,
        "no_signing_keys_required": True,
        "requirements": [r.to_dict() for r in reqs],
    }


def fork_plan_md(reqs) -> str:
    if not reqs:
        body = (
            "# 12 Fork Plan\n\n"
            "No candidate requires fork proof in this run. All suspicious invariants are "
            "locally testable. (If external AMM/oracle/bridge state mattered, a fork plan "
            "would appear here.)\n\n"
            "Safety: no RPC by default, no broadcast, no private keys.\n"
        )
        return body

    all_env = sorted({e for r in reqs for e in r.required_env})
    env_status = env_detect.detect_env(all_env)
    lines = [
        "# 12 Fork Plan",
        "",
        "Some candidates need fork proof because real deployed state sets the actual loss.",
        "This plan is local simulation only: it references env var **names**, never URLs or",
        "keys, and never broadcasts.",
        "",
        f"- Required env (names only): {', '.join(all_env)}",
        f"- Present in this environment: {', '.join(env_status['present']) or 'none'}",
        f"- Missing (set before running a fork): {', '.join(env_status['missing']) or 'none'}",
        "",
    ]
    for r in reqs:
        lines += [
            f"## {r.candidate_id} — fork on {r.chain}",
            f"- Env: {', '.join(r.required_env)} (name only; never commit the URL)",
            f"- Reason: {r.reason}",
            f"- Verify: {', '.join(r.contracts_to_verify)}",
            f"- Static reads: {', '.join(r.static_calls_needed)}",
            "- Test plan:",
        ]
        lines += [f"  {i}. {s}" for i, s in enumerate(test_plan.test_steps(r), 1)]
        lines += [f"- do_not_broadcast: {r.do_not_broadcast}",
                  f"- secret_redaction_required: {r.secret_redaction_required}", ""]
    text = "\n".join(lines) + "\n"
    # Final safety pass: redact anything URL/key-like that slipped in.
    return secret_redaction.redact(text)
