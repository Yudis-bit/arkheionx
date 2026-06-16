"""Step 3 — freshness diff.

Freshness asks: what changed since the last known review point? A stale,
heavily-audited surface is downranked; a fresh adapter / new implementation / a
value-bearing function absent from the provided audit baseline is upranked.

Git is used only when a baseline is explicitly provided (``--baseline-ref`` or
``--since-date``); otherwise freshness is inferred from local filename/behaviour
signals and audit-baseline coverage, and marked UNKNOWN_FRESHNESS when inference is
weak. Read-only; no network access.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from . import models as M
from .corpus import Doc

# Filename / note fragments that imply newly added surface.
_NEW_SIGNALS = (
    ("adapter", M.NEW_ADAPTER, "adapter / external integration"),
    ("registry", M.NEW_REGISTRY_ENTRY, "registry entry"),
    ("migrat", M.NEW_MIGRATION_PATH, "migration path"),
    ("upgrade", M.NEW_IMPLEMENTATION, "upgrade / new implementation"),
    ("proxy", M.NEW_IMPLEMENTATION, "proxy / implementation"),
    ("implementation", M.NEW_IMPLEMENTATION, "new implementation"),
)


def _git_changed_basenames(root: Path, baseline_ref: str, since_date: str) -> set[str] | None:
    """Return basenames of files changed since the baseline, or None if unavailable."""
    cmd: list[str] | None = None
    if baseline_ref:
        cmd = ["git", "-C", str(root), "diff", "--name-only", f"{baseline_ref}..HEAD"]
    elif since_date:
        cmd = ["git", "-C", str(root), "log", "--name-only", "--pretty=format:", f"--since={since_date}"]
    if cmd is None:
        return None
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    names: set[str] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if line:
            names.add(Path(line).name)
    return names or set()


def _new_signal_for(text_blobs: list[str]) -> tuple[str, str] | None:
    low = " ".join(text_blobs).lower()
    for fragment, status, label in _NEW_SIGNALS:
        if fragment in low:
            return status, label
    return None


def assess_freshness(
    ctx: M.TriageContext,
    root: Path,
    leads: list[M.LeadCandidate],
    docs: list[Doc],
) -> list[M.FreshnessSignal]:
    audit_docs = [d for d in docs if d.kind == "audit"]
    audit_text = "\n".join(d.lower for d in audit_docs)
    have_audit_baseline = bool(audit_docs)

    changed = _git_changed_basenames(root, ctx.baseline_ref, ctx.since_date)
    baseline_label = (
        f"git:{ctx.baseline_ref}" if ctx.baseline_ref
        else (f"since:{ctx.since_date}" if ctx.since_date
              else ("audit-corpus" if have_audit_baseline else "none"))
    )

    signals: list[M.FreshnessSignal] = []
    for lead in leads:
        value_bearing = lead.materiality_score >= 60 or "value-out" in lead.notes
        basenames = [Path(p).name for p in lead.linked_files]
        name_tokens = [Path(p).stem.lower() for p in lead.linked_files]
        name_tokens.append(lead.surface.split(".")[0].lower())
        audited = bool(audit_text) and any(tok and len(tok) >= 4 and tok in audit_text for tok in name_tokens)

        git_hit = changed is not None and any(b in changed for b in basenames)
        new_signal = _new_signal_for([lead.title, lead.surface, " ".join(lead.notes), " ".join(basenames)])

        sig_notes: list[str] = []
        changed_paths: list[str] = []

        if git_hit:
            changed_paths = [p for p, b in zip(lead.linked_files, basenames) if b in (changed or set())]
            status = M.POST_AUDIT_CHANGE
            score = 100 if value_bearing else 80
            sig_notes.append(f"Changed after baseline ({baseline_label}).")
        elif new_signal is not None:
            status, label = new_signal
            score = 85 if value_bearing else 70
            sig_notes.append(f"New {label} detected from local signals.")
        elif audited:
            status = M.STALE
            score = 20
            sig_notes.append("Surface appears in the provided audit baseline (stale / over-audited).")
        elif have_audit_baseline and value_bearing:
            status = M.FRESH
            score = 55
            sig_notes.append("Value-bearing surface absent from the provided audit baseline (unaudited, not a priority change).")
        else:
            status = M.UNKNOWN_FRESHNESS
            score = 40
            sig_notes.append("No reliable freshness baseline; provide --baseline-ref, --audits, or --since-date.")

        signals.append(
            M.FreshnessSignal(
                lead_id=lead.id,
                status=status,
                score=score,
                baseline=baseline_label,
                signals=sig_notes,
                changed_paths=changed_paths,
                note=sig_notes[0] if sig_notes else "",
            )
        )
    return signals
