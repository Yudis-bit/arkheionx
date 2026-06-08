"""Evidence Graph + Interaction Matrix engine (v6).

Extends the v4 review-map and v5 Blind Spot Intelligence workflow into an
evidence-classification layer for Web3 security research. v5 answers "where
should I look first?"; v6 answers "what evidence exists, what remains unresolved,
and which dangerous interactions still lack proof?".

It classifies every important surface into an evidence state (tested,
rejected-with-evidence, confirmed-candidate, unresolved, needs-human-review,
insufficient-evidence, unclassified, out-of-scope), detects meaningful
interactions between surfaces, maps everything still unresolved, and packages the
result into a complete local review package.

Local/static and heuristic. An evidence state is not a vulnerability claim.
Confirmed-candidate is not a confirmed vulnerability. Interaction priority is not
severity. Unresolved does not mean vulnerable. Human review is required.
"""
from __future__ import annotations

from .builder import (
    build_evidence_graph,
    build_evidence_graph_from_review_map,
    build_human_review_checklist,
    load_research_memory,
)
from .complete_review import (
    build_complete_review,
    build_complete_review_from_review_map,
)
from .interactions import (
    build_interaction_matrix,
    build_interaction_matrix_from_review_map,
    surface_categories,
)
from .json_output import (
    default_complete_review_dir,
    default_evidence_graph_dir,
    default_interaction_matrix_dir,
    default_unresolved_map_dir,
    write_evidence_graph,
    write_interaction_matrix,
    write_unresolved_map,
)
from .models import EvidenceNode, Interaction
from .render import (
    render_evidence_graph_cli,
    render_evidence_graph_md,
    render_interaction_matrix_cli,
    render_interaction_matrix_md,
    render_unresolved_map_cli,
    render_unresolved_map_md,
)
from .unresolved import (
    build_unresolved_map,
    build_unresolved_map_from_review_map,
)

__all__ = [
    "EvidenceNode",
    "Interaction",
    "build_evidence_graph",
    "build_evidence_graph_from_review_map",
    "build_interaction_matrix",
    "build_interaction_matrix_from_review_map",
    "build_unresolved_map",
    "build_unresolved_map_from_review_map",
    "build_complete_review",
    "build_complete_review_from_review_map",
    "build_human_review_checklist",
    "load_research_memory",
    "surface_categories",
    "render_evidence_graph_md",
    "render_evidence_graph_cli",
    "render_interaction_matrix_md",
    "render_interaction_matrix_cli",
    "render_unresolved_map_md",
    "render_unresolved_map_cli",
    "write_evidence_graph",
    "write_interaction_matrix",
    "write_unresolved_map",
    "default_evidence_graph_dir",
    "default_interaction_matrix_dir",
    "default_unresolved_map_dir",
    "default_complete_review_dir",
]
