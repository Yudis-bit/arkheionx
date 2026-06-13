"""Step 4 — deployment reality check (local-first, optional).

This module is local-first and read-only. It never makes a live-chain call, never
broadcasts a transaction, and never touches private keys. Without ``--addresses`` it
reports NOT_RUN. With addresses but no endpoint it produces a static verification
*plan*. If an endpoint is supplied, live read-only verification is not implemented in
this pass: the module says so honestly (DEPLOYMENT_REALITY_NOT_IMPLEMENTED) and
suggests safe commands the human can run, rather than faking a live check.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import models as M

_RECOMMENDED_CHECKS = (
    "EIP-1967 implementation slot for every proxy address.",
    "Proxy admin / owner address for each upgradeable contract.",
    "Registry values and routing entries.",
    "Oracle address, decimals, and staleness window.",
    "Role holders for each privileged role.",
    "Paused / disabled state of value-bearing entry points.",
    "Token balances actually held by the deployment.",
)

# Read-only command suggestions for the human (never run here; never broadcast).
_SAFE_COMMANDS = (
    "cast code <address>            # confirm deployed bytecode exists (read-only)",
    "cast storage <proxy> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
    "  # EIP-1967 implementation slot (read-only)",
    "cast call <oracle> 'decimals()(uint8)'   # read-only oracle metadata",
    "cast call <token> 'balanceOf(address)(uint256)' <deployment>   # read-only balance",
)


def _mask_endpoint(raw: str) -> str:
    """Mask a supplied endpoint so it never appears verbatim in any output."""
    if not raw:
        return ""
    raw = raw.strip()
    scheme = raw.split("://", 1)[0] if "://" in raw else "endpoint"
    return f"{scheme}://***masked***"


def _load_addresses(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return []
    entries: list[dict] = []

    def _add(name: str, value: object) -> None:
        if isinstance(value, str) and value:
            entries.append({"name": str(name)[:64], "address": value[:80]})

    if isinstance(data, dict):
        source = data.get("contracts") if isinstance(data.get("contracts"), dict) else data
        if isinstance(source, dict):
            for name, value in source.items():
                if isinstance(value, str):
                    _add(name, value)
                elif isinstance(value, dict) and "address" in value:
                    _add(value.get("name", name), value.get("address"))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "address" in item:
                _add(item.get("name", "contract"), item.get("address"))
    return entries[:64]


def assess_deployment(ctx: M.TriageContext) -> M.DeploymentRealitySignal:
    rpc_mode = ctx.rpc_mode
    masked = ctx.rpc_endpoint_masked or _mask_endpoint("")
    addresses_file = (ctx.addresses_file or "").strip()

    if not addresses_file:
        return M.DeploymentRealitySignal(
            status=M.DEPLOY_NOT_RUN,
            rpc_mode=rpc_mode,
            addresses_provided=False,
            recommended_checks=list(_RECOMMENDED_CHECKS),
            safe_commands=[],
            rpc_endpoint_masked=masked,
            reason="No addresses file provided (--addresses). Deployment reality not run.",
            notes=[
                "Live state: NOT_RUN.",
                "Provide --addresses to generate a static deployment-reality plan.",
            ],
        )

    addresses = _load_addresses(Path(addresses_file).expanduser())
    if not addresses:
        return M.DeploymentRealitySignal(
            status=M.DEPLOY_NOT_RUN,
            rpc_mode=rpc_mode,
            addresses_provided=True,
            addresses=[],
            recommended_checks=list(_RECOMMENDED_CHECKS),
            safe_commands=list(_SAFE_COMMANDS),
            rpc_endpoint_masked=masked,
            reason="Addresses file present but no usable address entries were parsed.",
            notes=["Provide a JSON object or list mapping names to 0x addresses."],
        )

    if rpc_mode == "provided_not_run":
        # An endpoint was supplied. We do not perform live reads in this pass and we
        # never mutate chain — say so honestly instead of faking a live check.
        return M.DeploymentRealitySignal(
            status=M.DEPLOY_NOT_IMPLEMENTED,
            rpc_mode=rpc_mode,
            addresses_provided=True,
            addresses=addresses,
            recommended_checks=list(_RECOMMENDED_CHECKS),
            safe_commands=list(_SAFE_COMMANDS),
            rpc_endpoint_masked=masked,
            reason=(
                "A read-only endpoint was supplied, but live read-only verification is "
                "not implemented in this pass. No live-chain call was made and the chain "
                "was never mutated."
            ),
            notes=[
                "Endpoint is masked in all output.",
                "Run the suggested read-only commands yourself to compare live state to source.",
            ],
        )

    # Addresses provided, no endpoint -> static plan only.
    return M.DeploymentRealitySignal(
        status=M.DEPLOY_ADDRESSES_PROVIDED,
        rpc_mode=rpc_mode,
        addresses_provided=True,
        addresses=addresses,
        recommended_checks=list(_RECOMMENDED_CHECKS),
        safe_commands=list(_SAFE_COMMANDS),
        rpc_endpoint_masked=masked,
        reason="Addresses provided; no endpoint supplied, so read-only live verification was not run.",
        notes=[
            "Live state: NOT_RUN (no endpoint; triage makes no live-chain calls by default).",
            "Use the recommended read-only checks to compare deployed state to source.",
        ],
    )
