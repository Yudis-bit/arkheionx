"""Transparent evidence classification for the v6 Evidence Graph.

Maps each :class:`~arkheionx.blind_spots.models.SurfaceRecord` to an evidence
state and an evidence strength using only local/static signals the v4/v5 engine
already produced (coverage signal, criticality potential, review density,
unverified assumptions, structural complexity). Nothing here claims a bug.

The two strongest states — ``rejected-with-evidence`` and
``confirmed-candidate`` — are never inferred from scoring. They are only assigned
when an explicit local research-memory record (a hypothesis log entry with a
recorded local test) says so. In a default static run they are simply absent,
which is the honest result.
"""
from __future__ import annotations

from arkheionx.blind_spots.models import SurfaceRecord

from . import models as m

# Coverage signal vocabulary (from the v4.1 research surface engine).
_COV_TESTED = "tested"
_COV_PARTIAL = "partially tested"
_COV_NONE = "no direct test observed"

_LIQUIDATION_NAMES = ("liquidate", "liquidation", "seize", "health", "collateral",
                      "loantovalue", "ltv", "baddebt", "closefactor", "insolven")
_ORACLE_NAMES = ("oracle", "price", "feed", "aggregator", "twap", "rate", "quote", "latestround")
_SHARE_NAMES = ("preview", "converttoshares", "converttoassets", "maxwithdraw",
                "maxredeem", "shares", "share", "exchangerate")
_FEE_NAMES = ("fee", "commission", "skim", "performancefee", "managementfee", "dispatcher")
_CONNECTOR_NAMES = ("connector", "adapter", "strategy", "balanceofunderlying")
_BLOCKLIST_NAMES = ("blocklist", "blacklist", "denylist", "allowlist", "whitelist",
                    "restricted", "frozen", "freeze")
_LIFECYCLE_NAMES = ("initialize", "init", "upgrade", "migrate", "settle", "maturity", "expiry", "close")
_ADMIN_PREFIXES = ("set", "configure", "pause", "unpause", "upgrade", "initialize",
                   "init", "migrate", "kill", "shutdown", "rescue", "sweep", "emergency")


def _name(record: SurfaceRecord) -> str:
    return (record.function or "").lower()


def _risk_blob(record: SurfaceRecord) -> str:
    return " ".join(record.risk_signals).lower()


def surface_type(record: SurfaceRecord) -> str:
    """Return the most salient surface type for a record (deterministic).

    Name- and auth-anchored: the upstream value-flow detector over-labels some
    surfaces with a coarse ``value exit`` risk signal, so the function name and
    the (precise) authorization/periphery signals are trusted first.
    """
    name = _name(record)
    risk = _risk_blob(record)
    if record.auth_kinds or "signature/merkle" in risk:
        return "authorization"
    if any(k in name for k in ("callback", "hook", "onerc", "onsettlement", "receive", "fallback")):
        return "callback-external"
    if any(k in name for k in ("withdraw", "redeem", "unstake", "refund", "payout", "claim", "collect")):
        return "value-exit"
    if any(k in name for k in ("deposit", "mint", "supply", "stake", "fund", "lock")):
        return "value-entry"
    if any(k in name for k in _SHARE_NAMES):
        return "share-math"
    if any(k in name for k in _LIQUIDATION_NAMES) or "liquidation" in risk:
        return "liquidation"
    if any(name.startswith(p) for p in _ADMIN_PREFIXES):
        return "admin-emergency"
    if any(k in name for k in _ORACLE_NAMES) or "oracle" in risk:
        return "oracle"
    if record.periphery_interactions or record.cross_contract_targets or "periphery/core interaction" in risk:
        return "periphery"
    if any(k in name for k in _CONNECTOR_NAMES):
        return "connector"
    if any(k in name for k in _FEE_NAMES):
        return "fee"
    if any(k in name for k in _BLOCKLIST_NAMES):
        return "blocklist"
    if any(k in name for k in _LIFECYCLE_NAMES):
        return "lifecycle"
    if "accounting mutation" in risk:
        return "accounting"
    return "review-surface"


def _is_complex(record: SurfaceRecord) -> bool:
    return bool(record.auth_kinds or record.periphery_interactions or record.cross_contract_targets)


def evidence_strength(record: SurfaceRecord) -> str:
    """Heuristic strength of local evidence on a surface.

    strong:  a direct test exists, the surface is simple, and no unverified
             guarding assumption stacks on it.
    medium:  a direct test exists but the surface is complex or carries an
             unverified assumption (the test may not cover every edge).
    weak:    only partial test evidence was observed.
    none:    no direct local test was observed.
    unknown: could not classify coverage.
    """
    cov = record.coverage_signal
    if cov == _COV_TESTED:
        if record.test_reference_count >= 2 and not record.assumptions and not _is_complex(record):
            return m.STRENGTH_STRONG
        return m.STRENGTH_MEDIUM
    if cov == _COV_PARTIAL:
        return m.STRENGTH_WEAK
    if cov == _COV_NONE:
        return m.STRENGTH_NONE
    return m.STRENGTH_UNKNOWN


def _has_signals(record: SurfaceRecord) -> bool:
    return bool(record.impact_dimensions or record.risk_signals
                or record.auth_kinds or record.periphery_interactions)


def classify_state(record: SurfaceRecord, strength: str,
                   memory_status: str | None = None) -> tuple[str, str, str]:
    """Return ``(evidence_state, why_state, unresolved_reason)``.

    ``memory_status`` is the only path to the two strongest states and comes
    from explicit local research memory, never from scoring.
    """
    if memory_status == "rejected":
        return (m.STATE_REJECTED_WITH_EVIDENCE,
                "A local hypothesis log records this surface as tested and rejected with evidence.",
                "")
    if memory_status == "confirmed":
        return (m.STATE_CONFIRMED_CANDIDATE,
                "A local hypothesis log records a candidate here. This is not a confirmed vulnerability; human review required.",
                "")
    if memory_status in ("needs-human-review", "testing"):
        return (m.STATE_NEEDS_HUMAN_REVIEW,
                "A local hypothesis log marks this surface as under review with ambiguous evidence.",
                "Local research memory flags this surface for manual judgement.")

    crit = record.criticality_potential
    high_crit = crit in (m.CRIT_VERY_HIGH, m.CRIT_HIGH)
    mid_crit = crit == m.CRIT_MEDIUM
    complex_surface = _is_complex(record)
    has_unverified = bool(record.assumptions)

    if not _has_signals(record):
        return (m.STATE_UNCLASSIFIED,
                "An important surface was detected but no signal is strong enough to assign a stronger state.",
                "Detected as a surface, but local signals are insufficient to classify it.")

    if strength == m.STRENGTH_STRONG:
        return (m.STATE_TESTED,
                "A direct local test was observed on a simple surface with no unverified guarding assumption.",
                "")

    if strength == m.STRENGTH_MEDIUM:
        # A single file-level/shallow test reference on a high-impact surface is
        # exactly the "looks tested but may not cover the relevant edge" trap.
        if high_crit:
            return (m.STATE_NEEDS_HUMAN_REVIEW,
                    "A local test references this surface, but coverage is shallow (file-level / single reference) on a high-impact surface; a human must confirm the relevant edge is actually exercised.",
                    "High criticality potential with only medium (shallow/file-level) evidence — looks tested, but the relevant assumption or edge may not be covered.")
        if complex_surface:
            return (m.STATE_INSUFFICIENT_EVIDENCE,
                    "A test references this surface but it crosses an authorization/periphery/contract boundary the shallow test may not cover.",
                    "Tests touch the surface but may not prove the cross-boundary assumption or counterfactual.")
        return (m.STATE_TESTED,
                "A direct local test was observed on a structurally simple, lower-impact surface."
                + (" A guarding assumption remains and is recorded as a residual gap." if has_unverified else ""),
                "")

    if strength == m.STRENGTH_WEAK:
        return (m.STATE_INSUFFICIENT_EVIDENCE,
                "Only partial/indirect local test evidence was observed; it does not clearly prove the guarding assumption.",
                "Partial evidence exists but does not close the question on this surface.")

    if strength == m.STRENGTH_NONE:
        if high_crit or mid_crit:
            return (m.STATE_UNRESOLVED,
                    "No direct local test was observed on a high-impact surface.",
                    "High criticality potential with no observed local test or counterfactual coverage.")
        return (m.STATE_UNCLASSIFIED,
                "No direct local test was observed and impact is low; not enough to assign a stronger state.",
                "Low impact and no observed test — left unclassified rather than overstated.")

    # strength unknown
    if high_crit:
        return (m.STATE_NEEDS_HUMAN_REVIEW,
                "Coverage could not be classified on a high-impact surface; a human must inspect.",
                "Ambiguous coverage on a high-impact surface.")
    return (m.STATE_UNCLASSIFIED,
            "Coverage could not be classified and impact is not high.",
            "Coverage signals are ambiguous; left unclassified.")


def confidence_label(strength: str) -> str:
    """Heuristic confidence in the local evidence (never a probability)."""
    if strength == m.STRENGTH_STRONG:
        return m.CONFIDENCE_HIGH
    if strength == m.STRENGTH_MEDIUM:
        return m.CONFIDENCE_MEDIUM
    return m.CONFIDENCE_LOW


def missing_evidence(record: SurfaceRecord, strength: str, stype: str) -> list[str]:
    """Heuristic list of evidence gap types for a surface (deterministic)."""
    gaps: list[str] = []

    def add(gap: str) -> None:
        if gap not in gaps:
            gaps.append(gap)

    if strength in (m.STRENGTH_NONE, m.STRENGTH_UNKNOWN):
        add("no-direct-test")
    add("no-invariant")
    add("no-fuzz")

    if stype in ("value-exit", "value-entry", "accounting", "share-math"):
        add("no-pre-post-balance-check")
        add("no-rounding-edge-test")
    if stype == "value-exit":
        add("no-attacker-victim-separation")
    if stype == "authorization":
        add("no-negative-path-test")
        if record.auth_kinds and (set(record.auth_kinds) & {"signature", "domain", "replay"}):
            add("no-signature-replay-test")
        if "merkle" in record.auth_kinds:
            add("no-merkle-shape-test")
    if stype == "oracle":
        add("no-oracle-edge-test")
    if stype == "liquidation":
        add("no-boundary-test")
        add("no-oracle-edge-test")
    if stype == "callback-external":
        add("no-callback-order-test")
        add("no-pre-post-state-check")
    if stype in ("periphery", "connector") or record.cross_contract_targets:
        add("no-cross-contract-test")
        add("no-preview-vs-actual-test")
    if stype == "connector":
        add("no-connector-accounting-test")
    if stype == "admin-emergency":
        add("no-admin-path-test")
    if stype == "fee":
        add("no-fee-edge-test")
    if stype == "blocklist":
        add("no-pause/blocklist-test")
    if stype == "lifecycle":
        add("no-lifecycle-test")

    # Anything value/accounting relevant that lacks a focused interaction test.
    if stype in ("value-exit", "periphery", "callback-external", "liquidation", "connector"):
        add("no-interaction-test")
    return gaps[:8]
