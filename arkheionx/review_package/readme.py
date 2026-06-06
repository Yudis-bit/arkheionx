"""Reviewer README and limitations text for the review package (v3.6, additive).

Generates deterministic, local Markdown that states the package status and the
fixed safety boundary in negative framing only. The text never claims a
confirmed vulnerability, a final severity, an audit-passed outcome, or bounty
eligibility, never emits an automatic human-reviewed status, and contains no
absolute paths (only package-relative file names).
"""
from __future__ import annotations

from .model import ReviewPackageManifest, ReviewPackageValidationResult

_SAFETY_BULLETS = [
    "Local/static review context only.",
    "No RPC and no live-chain calls.",
    "No private keys and no seed phrases.",
    "No transaction broadcasting.",
    "No exploit automation.",
    "No auto-submit.",
    "No automatic human-reviewed status.",
    "No confirmed vulnerabilities.",
    "No final severity.",
    "No audit-passed claim.",
    "No bounty eligibility.",
    "Manual review is required.",
]


def _kinds(manifest: ReviewPackageManifest) -> list[str]:
    return sorted({a.kind for a in manifest.included_artifacts})


def build_reviewer_readme(manifest: ReviewPackageManifest, validation: ReviewPackageValidationResult) -> str:
    present_required = sorted({a.kind for a in manifest.included_artifacts if a.required and a.exists})
    lines = [
        f"# Arkheionx Review Package: {manifest.package_name or 'review-package'}",
        "",
        "Local, static, reviewer-ready package assembled from existing "
        "`.arkheionx/out/` artifacts. Review guidance only.",
        "",
        "## Status",
        "",
        f"- Validation status: {validation.status}",
        f"- Artifacts included: {len(manifest.included_artifacts)}",
        f"- Required artifacts present: {', '.join(present_required) or '(none)'}",
        f"- Missing required artifacts: {', '.join(validation.missing_required_artifacts) or '(none)'}",
        f"- Manual review required: {manifest.manual_review_required}",
        f"- Ready for submission: {manifest.ready_for_submission}",
        "",
        "## Included Artifact Kinds",
        "",
    ]
    lines += [f"- {kind}" for kind in _kinds(manifest)] or ["- (none)"]
    lines += [
        "",
        "## How To Inspect",
        "",
        "- Read `manifest.json` for the artifact inventory, checksums, and package id.",
        "- Read `validation.json` for per-check results, errors, and warnings.",
        "- Read `limitations.md` for the boundary and what this package is not.",
        "- Copied artifacts live under `artifacts/` with their original relative layout.",
        "",
        "## Safety Boundary",
        "",
    ]
    lines += [f"- {bullet}" for bullet in _SAFETY_BULLETS]
    lines += ["", "## Limitations", "", "See `limitations.md`. Human review is required before any use."]
    return "\n".join(lines) + "\n"


def build_limitations_text(manifest: ReviewPackageManifest, validation: ReviewPackageValidationResult) -> str:
    lines = [
        "# Limitations",
        "",
        "- This is a local-only review package generated from local/static artifacts.",
        "- It is not a formal audit.",
        "- It is not a vulnerability confirmation.",
        "- It does not assign a final severity.",
        "- It does not establish bounty eligibility.",
        "- It is not ready for submission; `ready_for_submission` is false.",
        "- Manual review is required before any decision.",
        "- Optional artifacts may be missing; absence is recorded honestly, not failed.",
        f"- Validation status is `{validation.status}`; review `validation.json` before relying on it.",
        "- Checksums in `checksums/SHA256SUMS` and `manifest.json` should be reviewed.",
        "- No RPC, no private keys, no seed phrases, no broadcasting, no exploit automation, no auto-submit.",
    ]
    return "\n".join(lines) + "\n"
