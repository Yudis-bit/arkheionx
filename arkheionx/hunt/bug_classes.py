"""Map a classified function to likely bug-class review surfaces.

Language is intentionally defensive: these are candidate review surfaces and
suggested tests, never confirmed exploits.
"""
from __future__ import annotations

from arkheionx.protocol.model import FunctionRole


def bug_classes_for(fr: FunctionRole) -> list[str]:
    classes: list[str] = []
    token_out = any(c.lower().startswith(("transfer", "safetransfer", "send")) and "from" not in c.lower() for c in fr.external_calls)

    if token_out and fr.writes_state:
        classes.append("reentrancy around external transfer (candidate)")
    if fr.role == "Reward Claim":
        classes.append("double claim / reward accounting mismatch (candidate)")
    if fr.oracle_calls:
        classes.append("stale or unsafe oracle price (candidate)")
    if fr.role in {"Share Mint", "Share Burn"} or any("share" in v.lower() or "assets" in v.lower() for v in fr.writes_state):
        classes.append("share/accounting mismatch (candidate)")
    if fr.role == "Accounting Update":
        classes.append("rounding / precision loss (candidate)")
    if fr.privileged and (token_out or any("oracle" in v.lower() or "treasury" in v.lower() or "fee" in v.lower() for v in fr.writes_state + fr.reads_state)):
        classes.append("privileged value redirection (candidate)")
    if fr.role == "Strategy Movement":
        classes.append("strategy misconfiguration / asset loss (candidate)")
    if fr.role == "Money Exit" and not classes:
        classes.append("incorrect accounting on exit (candidate)")
    if not classes and fr.external_calls:
        classes.append("external integration trust failure (candidate)")
    return classes
