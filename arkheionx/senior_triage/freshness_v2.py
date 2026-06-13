"""Audit-baseline and freshness v2.

Determines what changed since the last known review point, with located evidence.
Git is used only when a baseline is explicitly provided; an audit corpus acts as a
softer baseline (anything named in it is treated as already reviewed / stale). When
the baseline is weak, freshness is UNKNOWN_FRESHNESS and the missing context is
listed. Read-only; no network.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import evidence_snippets as ev
from . import models as M
from .freshness import _git_changed_basenames

# Filename / note fragments -> (status, label).
_NEW_SIGNALS = (
    ("adapter", M.NEW_ADAPTER, "adapter / external integration"),
    ("registry", M.NEW_REGISTRY_ENTRY, "registry entry"),
    ("migrat", M.NEW_MIGRATION_PATH, "migration path"),
    ("upgrade", M.NEW_IMPLEMENTATION, "upgrade / new implementation"),
    ("proxy", M.NEW_IMPLEMENTATION, "proxy / implementation"),
    ("implementation", M.NEW_IMPLEMENTATION, "new implementation"),
)

_DATE_RE = re.compile(
    r"(20\d{2}-\d{2}-\d{2})"
    r"|((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2})",
    re.IGNORECASE,
)


def _audit_baseline_date(audit_docs: list) -> str:
    for doc in audit_docs:
        m = _DATE_RE.search(doc.text)
        if m:
            return m.group(0)
    return ""


def _new_signal_for(blobs: list) -> tuple | None:
    low = " ".join(blobs).lower()
    for fragment, status, label in _NEW_SIGNALS:
        if fragment in low:
            return status, label
    return None


def assess_freshness(ctx: M.TriageContext, root: Path, leads: list, corpus: list) -> list:
    audit_docs = [d for d in corpus if d.kind == "audit"]
    audit_text = "\n".join(d.lower for d in audit_docs)
    have_audit_baseline = bool(audit_docs)
    audit_date = _audit_baseline_date(audit_docs)

    changed = _git_changed_basenames(root, ctx.baseline_ref, ctx.since_date)
    if ctx.baseline_ref:
        baseline_label = f"git:{ctx.baseline_ref}"
    elif ctx.since_date:
        baseline_label = f"since:{ctx.since_date}"
    elif have_audit_baseline:
        baseline_label = f"audit-corpus{(' @ ' + audit_date) if audit_date else ''}"
    else:
        baseline_label = "none"

    signals: list = []
    for lead in leads:
        value_out = "value-out" in lead.notes
        value_bearing = lead.materiality_score >= 60 or value_out or "value-in" in lead.notes
        oracle_related = "oracle-dependent" in lead.notes or "oracle" in lead.surface.lower()
        basenames = [Path(p).name for p in lead.linked_files]
        name_tokens = [Path(p).stem.lower() for p in lead.linked_files]
        name_tokens.append(lead.surface.split(".")[0].lower())
        audited = bool(audit_text) and any(t and len(t) >= 4 and t in audit_text for t in name_tokens)

        git_hit = changed is not None and any(b in changed for b in basenames)
        new_signal = _new_signal_for([lead.title, lead.surface, " ".join(lead.notes), " ".join(basenames)])

        notes: list = []
        changed_paths: list = []
        evidence: list = []

        if git_hit:
            changed_paths = [p for p, b in zip(lead.linked_files, basenames) if b in (changed or set())]
            if value_out:
                status, score = M.NEW_VALUE_OUT_PATH, 100
                notes.append(f"Value-out path changed after baseline ({baseline_label}).")
            elif value_bearing:
                status, score = M.POST_AUDIT_CHANGE, 100
                notes.append(f"Value-bearing code changed after baseline ({baseline_label}).")
            else:
                status, score = M.POST_AUDIT_CHANGE, 80
                notes.append(f"Code changed after baseline ({baseline_label}).")
            for p in changed_paths:
                evidence.append(M.EvidenceSnippet(source_path=p, reason="changed after baseline (git diff)").to_dict())
        elif new_signal is not None:
            status, label = new_signal
            score = 90 if value_bearing else 70
            notes.append(f"New {label} detected from local signals.")
            for p in lead.linked_files:
                evidence.append(M.EvidenceSnippet(source_path=p, reason=f"new {label}").to_dict())
        elif oracle_related and not audited:
            status, score = M.NEW_ORACLE_PATH, 85
            notes.append("Oracle/price path not present in the audit baseline.")
        elif audited:
            status, score = M.STALE, 20
            notes.append("Surface appears in the audit baseline (stale / over-audited).")
            for doc in audit_docs:
                snip = ev.first_snippet(doc, [lead.surface.split(".")[0].lower()],
                                        reason="audited surface")
                if snip:
                    evidence.append(snip.to_dict())
                    break
        elif have_audit_baseline and value_bearing:
            status, score = M.FRESH, 55
            notes.append("Value-bearing surface absent from the audit baseline (unaudited, not a priority change).")
        else:
            status, score = M.UNKNOWN_FRESHNESS, 40
            notes.append("No reliable freshness baseline; provide --baseline-ref, --audits, or --since-date.")

        signals.append(
            M.FreshnessSignal(
                lead_id=lead.id, status=status, score=score, baseline=baseline_label,
                signals=notes, changed_paths=changed_paths, evidence=evidence[:6],
                note=notes[0] if notes else "",
            )
        )
    return signals
