"""Render repository ingestion summaries."""
from __future__ import annotations


def ingest_json(summary) -> dict:
    return {
        "schema_version": "v10.1-ingest-summary",
        "artifact_type": "ingest_summary",
        **summary.to_dict(),
    }


def ingest_md(summary) -> str:
    lines = [
        "# Ingest Summary",
        "",
        f"- Framework detected: {summary.framework}",
        f"- Solidity files indexed: {summary.solidity_files_indexed}",
        f"- Contracts indexed: {summary.contracts_indexed}",
        f"- Real source contracts indexed: {summary.real_contracts_indexed}",
        f"- Artifact-only contracts indexed: {summary.artifact_only_contracts_indexed}",
        f"- Artifact mode: {summary.artifact_mode}",
        f"- Stale artifacts ignored: {summary.stale_artifacts_ignored}",
        f"- Sample artifacts ignored: {summary.sample_artifacts_ignored}",
        f"- Excluded dependency files: {summary.excluded_dependency_files}",
    ]
    if summary.warnings:
        lines += ["", "## Warnings"] + [f"- {warning}" for warning in summary.warnings]
    return "\n".join(lines) + "\n"
