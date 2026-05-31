"""Render a MoneyFlow into a safe Mermaid flowchart.

Node ids are sanitized to alphanumerics and labels are escaped so generated
diagrams never break Mermaid parsing.
"""
from __future__ import annotations

import re

from .model import MoneyFlow

_MAX_EDGES = 40


def _node_id(label: str) -> str:
    nid = re.sub(r"[^A-Za-z0-9]", "_", label)
    nid = re.sub(r"_+", "_", nid).strip("_")
    return nid or "node"


def _safe_label(text: str) -> str:
    # Mermaid labels are wrapped in quotes; strip characters that break parsing.
    cleaned = text.replace('"', "'").replace("\n", " ")
    cleaned = re.sub(r"[\[\]{}|<>]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def render_mermaid(flow: MoneyFlow) -> str:
    lines = ["flowchart LR"]
    nodes: dict[str, str] = {}

    def ensure(label: str) -> str:
        nid = _node_id(label)
        if nid not in nodes:
            nodes[nid] = _safe_label(label)
        return nid

    edge_lines: list[str] = []
    for edge in flow.edges[:_MAX_EDGES]:
        src = ensure(edge.source)
        dst = ensure(edge.target)
        label = _safe_label(edge.label or edge.kind)
        edge_lines.append(f'{src} -->|"{label}"| {dst}')

    for nid, label in nodes.items():
        lines.append(f'{nid}["{label}"]')
    lines.extend(edge_lines)
    if not edge_lines:
        lines.append('Empty["No value-flow edges detected"]')
    return "\n".join(lines) + "\n"
