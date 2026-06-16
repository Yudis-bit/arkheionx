"""Fork test-plan steps (Layer 8). Local simulation only; never broadcast."""
from __future__ import annotations

__test__ = False


def test_steps(req) -> list:
    return [
        f"Select a fork from the env var `{', '.join(req.required_env)}` "
        f"(name only; never hardcode the URL).",
        "Pin a block; load the real external contracts to verify "
        f"({', '.join(req.contracts_to_verify)}).",
        "Run the honest path and record the victim's refund/received amount.",
        "Snapshot, then run the attacker-chosen path with the SAME protocol output.",
        "Measure the delta (refund decrease / mis-credit) against the honest path.",
        "Assert the broken invariant fails, and quantify the loss vs the cap/buffer.",
        "Do NOT broadcast. No transactions are sent; no private key is used.",
    ]


def deployment_targets(scope) -> list:
    """Contract names/addresses to verify, from scope if present (public data)."""
    if not scope:
        return []
    out = []
    for item in (scope.get("contracts") or []):
        if isinstance(item, dict):
            out.append({"name": item.get("name", ""), "address": item.get("address", "")})
        else:
            out.append({"name": str(item), "address": ""})
    return out
