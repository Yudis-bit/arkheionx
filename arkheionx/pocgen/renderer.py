"""Renderer for the PoC skeleton directory (11-poc-skeletons/)."""
from __future__ import annotations


def skeletons_readme(skeletons) -> str:
    lines = [
        "# 11 PoC Skeletons",
        "",
        "Foundry test skeletons for the top candidates. These are **skeletons**:",
        "`compile_ready_level = requires_manual_fill`. Each encodes the right actors,",
        "setup, action sequence, and the assertion that falsifies the broken invariant,",
        "but you must supply the target import, constructor args, and TODO values.",
        "",
        "Local simulation only. No broadcast, no private keys, no live network. A fork",
        "skeleton reads its RPC from an env var name and never hardcodes a URL.",
        "",
        "| File | Candidate | Family | Proof | Compile-readiness |",
        "| --- | --- | --- | --- | --- |",
    ]
    for s in skeletons:
        proof = "fork" if s.required_fork_env else "local"
        lines.append(f"| {s.file_name} | {s.candidate_id} | {s.family} | {proof} | "
                     f"{s.compile_readiness} |")
    lines += [
        "",
        "## Run (after filling TODOs)",
        "```bash",
        "forge test --match-path test/<file>.t.sol -vvv",
        "# fork skeletons: export FORK_RPC_URL=... first (never commit it)",
        "```",
    ]
    return "\n".join(lines) + "\n"


def skeleton_files(skeletons) -> dict:
    """Map relative filename -> source text for writing under 11-poc-skeletons/."""
    return {s.file_name: s.source for s in skeletons}
