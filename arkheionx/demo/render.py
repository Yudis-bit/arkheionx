"""Terminal rendering for the Arkheionx demo command."""
from __future__ import annotations

from arkheionx.demo.model import Demo
from arkheionx.demo.registry import resolve_source_kind, workflow_commands

SAFETY_NOTICE = (
    "Local-only and safe: no RPC, no private keys, no secrets, no mainnet. "
    "A toy fixture, not a real protocol; not a vulnerability report or severity claim."
)


def render_list(demos: list[Demo]) -> str:
    lines = ["ARKHEIONX DEMOS", "Available demos", ""]
    for demo in demos:
        foundry = "recommended" if not demo.requires_foundry else "required"
        lines.append(f"  {demo.id}")
        lines.append(f"    {demo.description}")
        lines.append(f"    Foundry: optional but {foundry}")
        lines.append(f"    Target: {demo.recommended_target}")
        lines.append("")
    lines.append("Next")
    first = demos[0].id if demos else "<id>"
    lines.append(f"  arkheionx demo --show {first}")
    return "\n".join(lines)


def render_show(demo: Demo) -> str:
    lines = [
        f"ARKHEIONX DEMO: {demo.id}",
        f"Name: {demo.name}",
        f"Purpose: {demo.description}",
        f"Source: {resolve_source_kind(demo)}",
        f"Recommended target: {demo.recommended_target}",
        f"Expected mode: {demo.expected_mode}",
        f"Docs: {demo.docs}",
        "",
        "Recommended commands",
        f"  arkheionx demo --copy {demo.id} ./arkheionx-demo",
        f"  arkheionx demo --commands {demo.id}",
        "",
        f"Safety: {SAFETY_NOTICE}",
        f"Note: {demo.notes}",
    ]
    return "\n".join(lines)


def render_commands(demo: Demo, dest: str) -> str:
    heuristic, foundry = workflow_commands(demo, dest)
    lines = [f"ARKHEIONX DEMO COMMANDS: {demo.id}", f"Destination: {dest}", ""]
    lines.append("Heuristic workflow (no Foundry required)")
    lines.extend(f"  {cmd}" for cmd in heuristic)
    lines.append("")
    lines.append("Foundry-backed workflow (if forge is available)")
    lines.extend(f"  {cmd}" for cmd in foundry)
    lines.append("")
    lines.append(f"Safety: {SAFETY_NOTICE}")
    return "\n".join(lines)
