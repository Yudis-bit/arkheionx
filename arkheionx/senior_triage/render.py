"""Render the human-readable Senior Triage Pack (artifacts 00-09).

Tone is direct and senior: pursue this, park that, kill the rest. The renderer only
ever emits the approved decision vocabulary. It never emits a confirmed-vulnerability
claim, never assigns a final severity, and never tells anyone to submit. Every
artifact restates the local-only, human-review-required boundary.
"""
from __future__ import annotations

from . import models as M

ARTIFACT_ORDER = (
    "00-target-decision.md",
    "01-bounty-eligibility.md",
    "02-known-issue-map.md",
    "03-freshness-diff.md",
    "04-deployment-reality.md",
    "05-lead-scoreboard.md",
    "06-top-3-leads.md",
    "07-do-not-touch.md",
    "08-next-commands.md",
    "09-agent-brief.md",
)

_FOOTER = (
    "---",
    "Senior triage is a local/static planning artifact. It is not a finding, not a "
    "severity, and not a confirmed vulnerability.",
    "No RPC by default. No live-chain calls. No auto-submit. Human review is required.",
)


def _footer() -> str:
    return "\n".join(_FOOTER)


def _bullets(items, empty="(none)") -> str:
    items = [i for i in items if i]
    if not items:
        return f"- {empty}"
    return "\n".join(f"- {i}" for i in items)


def _counts(pack: M.SeniorTriagePack) -> dict:
    leads = pack.leads
    return {
        "leads": len(leads),
        "pursue": sum(1 for x in leads if x.decision == M.LEAD_PURSUE),
        "park": sum(1 for x in leads if x.decision == M.LEAD_PARK),
        "kill": sum(1 for x in leads if x.decision == M.LEAD_KILL),
        "do_not_touch": len(pack.do_not_touch),
    }


def render_all(pack: M.SeniorTriagePack) -> dict[str, str]:
    known_map = {k.lead_id: k for k in pack.known_issue_map}
    fresh_map = {f.lead_id: f for f in pack.freshness_diff}
    return {
        "00-target-decision.md": _render_target(pack),
        "01-bounty-eligibility.md": _render_eligibility(pack),
        "02-known-issue-map.md": _render_known(pack, known_map),
        "03-freshness-diff.md": _render_freshness(pack, fresh_map),
        "04-deployment-reality.md": _render_deployment(pack),
        "05-lead-scoreboard.md": _render_scoreboard(pack),
        "06-top-3-leads.md": _render_top3(pack),
        "07-do-not-touch.md": _render_do_not_touch(pack),
        "08-next-commands.md": _render_next_commands(pack),
        "09-agent-brief.md": _render_agent_brief(pack),
    }


def _render_target(pack: M.SeniorTriagePack) -> str:
    c = _counts(pack)
    td = pack.target_decision
    elig = pack.eligibility
    lines = [
        "# Senior Triage — Target Decision",
        "",
        f"Decision: {td.decision}",
        f"Confidence: {td.confidence}",
        f"Reason: {td.reason}",
        "",
        "## Snapshot",
        f"- Leads generated: {c['leads']}",
        f"- Pursue: {c['pursue']} | Park: {c['park']} | Kill: {c['kill']}",
        f"- Do-not-touch: {c['do_not_touch']} (see 07-do-not-touch.md)",
        f"- Top leads: up to {M.TOP_LEAD_LIMIT} (see 06-top-3-leads.md)",
        "",
        "## Eligibility read (see 01-bounty-eligibility.md)",
        f"- Scope: {'provided' if elig.scope_provided else 'none'}",
        f"- Scope confidence: {elig.scope_confidence}",
        f"- Initial severity ceiling: {elig.severity_ceiling}",
        f"- Initial duplicate risk: {elig.initial_duplicate_risk}",
        "",
        "## What to do next",
        _next_for_target(td.decision, c),
        "",
        "## Missing context",
        _bullets(pack.missing_context, empty="None noted."),
        "",
        _footer(),
        "",
    ]
    return "\n".join(lines)


def _next_for_target(decision: str, counts: dict) -> str:
    if decision == M.TARGET_TOUCH:
        return (
            f"- Touch this target, but only the top {min(counts['pursue'] or counts['park'], M.TOP_LEAD_LIMIT)} "
            "lead(s) in 06-top-3-leads.md.\n"
            "- Kill everything in 07-do-not-touch.md before writing any test."
        )
    if decision == M.TARGET_SKIP:
        return (
            "- Skip this target for now. No lead clears the bar.\n"
            "- See 07-do-not-touch.md for why, and 08-next-commands.md for what context would change this."
        )
    return (
        "- Gather more context before spending time (see 08-next-commands.md).\n"
        "- Local technical leads are still ranked below, but eligibility is unconfirmed."
    )


def _render_eligibility(pack: M.SeniorTriagePack) -> str:
    e = pack.eligibility
    lines = [
        "# 01 — Bounty Eligibility",
        "",
        f"Target decision: {e.target_decision}",
        f"Scope confidence: {e.scope_confidence}",
        f"Initial severity ceiling: {e.severity_ceiling}",
        f"Initial duplicate risk: {e.initial_duplicate_risk}",
        f"Requires PoC: {'yes' if e.requires_poc else 'unstated'}",
        f"KYC noted: {'yes' if e.kyc_noted else 'no'}",
        "",
        "## Reward / severity notes",
        _bullets(e.reward_notes, empty="No reward or severity bands found in the scope."),
        "",
        "## Out-of-scope traps",
        _bullets(e.oos_traps, empty="None detected in the scope text."),
        "",
        "## Trusted-role traps",
        _bullets(e.trusted_role_traps, empty="None detected in the scope text."),
        "",
        "## Excluded impacts",
        _bullets(e.excluded_impacts, empty="None detected."),
        "",
        "## Missing context",
        _bullets(e.missing_context, empty="None noted."),
        "",
        "## Recommended action",
        f"- {e.recommended_action or 'Confirm scope before spending time.'}",
    ]
    if not e.scope_provided:
        lines += [
            "",
            "> target decision: NEEDS_MORE_CONTEXT",
            "> reason: scope file does not include enough program rules to estimate bounty eligibility.",
            "> Local technical triage still continues below.",
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_known(pack: M.SeniorTriagePack, known_map: dict) -> str:
    provided = bool(pack.context.known_path or pack.context.audits_path)
    lines = [
        "# 02 — Known Issue / Dedup Map",
        "",
        f"Known/audit material provided: {'yes' if provided else 'no'}",
        f"Dedup confidence: {'usable' if provided else 'LOW'}",
        "",
    ]
    if not provided:
        lines += [
            "Known issue map: NOT_PROVIDED",
            "Dedup confidence: LOW",
            "Action: provide audit reports (--audits), public findings, repo issues, previous "
            "reports, and known limitations (--known). Local tests are still scanned below.",
            "",
        ]
    lines.append("## Per-lead dedup verdict")
    for lead in pack.leads:
        sig = known_map.get(lead.id)
        if sig is None:
            continue
        lines += [
            "",
            f"### {lead.id} — {lead.title}",
            f"- Status: {sig.status}",
            f"- Duplicate risk: {sig.duplicate_risk_score}",
            f"- Public test covered: {'yes' if sig.public_test_covered else 'no'}",
            f"- Matched terms: {', '.join(sig.matched_terms) if sig.matched_terms else '(none)'}",
            f"- Sources: {', '.join(sig.sources) if sig.sources else '(none)'}",
            f"- Note: {sig.note}",
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_freshness(pack: M.SeniorTriagePack, fresh_map: dict) -> str:
    lines = [
        "# 03 — Freshness Diff",
        "",
        "Fresh, post-audit, value-bearing surface ranks higher. Stale, over-audited "
        "surface ranks lower.",
        "",
    ]
    for lead in pack.leads:
        sig = fresh_map.get(lead.id)
        if sig is None:
            continue
        lines += [
            f"### {lead.id} — {lead.title}",
            f"- Status: {sig.status}",
            f"- Freshness score: {sig.score}",
            f"- Baseline: {sig.baseline}",
            f"- Signals: {'; '.join(sig.signals) if sig.signals else '(none)'}",
            f"- Changed paths: {', '.join(sig.changed_paths) if sig.changed_paths else '(none)'}",
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _render_deployment(pack: M.SeniorTriagePack) -> str:
    d = pack.deployment_reality
    lines = [
        "# 04 — Deployment Reality",
        "",
        f"Status: {d.status}",
        f"RPC mode: {d.rpc_mode}",
        f"Endpoint: {d.rpc_endpoint_masked or 'not provided'} (masked)",
        f"Addresses provided: {'yes' if d.addresses_provided else 'no'}",
        f"Reason: {d.reason}",
        "",
        "## Addresses",
    ]
    if d.addresses:
        for entry in d.addresses:
            lines.append(f"- {entry.get('name', 'contract')}: {entry.get('address', '')}")
    else:
        lines.append("- (none provided)")
    lines += [
        "",
        "## Recommended read-only checks",
        _bullets(d.recommended_checks),
        "",
        "## Safe read-only commands (run these yourself; nothing is executed here)",
        _bullets(d.safe_commands, empty="Provide --addresses to generate command suggestions."),
        "",
        "## Notes",
        _bullets(d.notes, empty="None."),
        "",
        _footer(),
        "",
    ]
    return "\n".join(lines)


def _render_scoreboard(pack: M.SeniorTriagePack) -> str:
    lines = [
        "# 05 — Lead Scoreboard",
        "",
        "Research-priority ordering (0-100). This is a time-allocation ranking, not a "
        "severity and not a validity claim.",
        "",
        "| Score | Decision | Dedup | Freshness | Lead | Surface |",
        "| ----- | -------- | ----- | --------- | ---- | ------- |",
    ]
    for lead in _sorted_leads(pack.leads):
        lines.append(
            f"| {lead.research_priority_score} | {lead.decision} | {lead.dedup_status} | "
            f"{lead.freshness_status} | {lead.id} {lead.title} | {lead.surface} |"
        )
    lines += ["", "## Reasoning"]
    for lead in _sorted_leads(pack.leads):
        lines += [
            "",
            f"### {lead.id} — {lead.title} — {lead.research_priority_score} ({lead.decision})",
            _bullets(lead.score_reasons),
            f"- Kill condition: {lead.kill_condition}",
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_top3(pack: M.SeniorTriagePack) -> str:
    top = pack.top_leads()
    lines = ["# 06 — Top Leads (max 3)", ""]
    if not top:
        lines += [
            "NO_HIGH_PRIORITY_LEADS",
            "",
            "No lead is worth touching right now. See 07-do-not-touch.md and "
            "08-next-commands.md.",
            "",
            _footer(),
            "",
        ]
        return "\n".join(lines)
    for i, lead in enumerate(top, 1):
        lines += [
            f"# Lead {i} — {lead.title}",
            "",
            f"Decision: {lead.decision}",
            f"Research Priority Score: {lead.research_priority_score}",
            f"Surface: {lead.surface}",
            f"Why this can matter: {lead.reason}",
            f"Why it may be fresh: {lead.freshness_status} ({lead.freshness_score}).",
            f"Scope fit: {pack.eligibility.scope_confidence} confidence; "
            f"ceiling {lead.expected_severity_ceiling}.",
            f"Dedup status: {lead.dedup_status} (duplicate risk {lead.duplicate_risk_score}).",
            f"Expected severity ceiling: {lead.expected_severity_ceiling}",
            f"Exact PoC path: Create a local Foundry test targeting {lead.surface} "
            f"(e.g. forge test --match-contract {lead.surface.split('.')[0]} -vvv).",
            f"Kill condition: {lead.kill_condition}",
            f"Next command: {lead.next_command}",
            f"Submit readiness: {lead.submit_readiness}",
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _render_do_not_touch(pack: M.SeniorTriagePack) -> str:
    lines = [
        "# 07 — Do Not Touch",
        "",
        "Senior researchers save time by saying no. Do not spend time on these now.",
        "",
    ]
    if not pack.do_not_touch:
        lines += ["- (nothing parked or killed)"]
    for item in pack.do_not_touch:
        lines += [
            f"## Do not touch: {item.get('title', '')}",
            f"- Reason: {item.get('reason', '')}",
            f"- Blocking factor: {item.get('blocking_factor', '')}",
            f"- What would change this: {item.get('what_would_change', '')}",
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _render_next_commands(pack: M.SeniorTriagePack) -> str:
    c = _counts(pack)
    lines = ["# 08 — Next Commands", ""]
    if c["pursue"] or c["park"]:
        scope_flag = f" --scope-file {pack.context.scope_file}" if pack.context.scope_file else ""
        lines += [
            "1. Build the review pack for the top lead(s):",
            f"   arkheionx review {pack.context.repo_path}{scope_flag} --out .arkheionx/review",
            "2. Create a local Foundry test harness for the top lead only.",
            "3. Run a dedup search for the exact root behavior before writing a report.",
            "4. Apply each lead's kill condition aggressively.",
        ]
    else:
        lines += [
            "1. Gather missing context.",
            "2. Add audit reports to ./audits and pass --audits.",
            "3. Add known findings to ./known and pass --known.",
            "4. Provide deployed addresses (--addresses) if live state matters.",
            "5. Re-run: arkheionx triage with the added context.",
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_agent_brief(pack: M.SeniorTriagePack) -> str:
    top_ids = ", ".join(lead.id for lead in pack.top_leads()) or "(none)"
    lines = [
        "# 09 — Agent Brief",
        "",
        "You are a follow-up research agent. Read this before doing anything.",
        "",
        "- Do not scan everything.",
        "- Do not write reports.",
        "- Do not claim vulnerabilities.",
        "- Do not submit. No auto-submit.",
        "- Do not use live-chain assumptions.",
        "- Do not make RPC or live-chain calls.",
        "- Do not ignore dedup risk.",
        "- Do not write a PoC before checking the known issue map (02).",
        "- Do not pursue KILL leads.",
        "- Only work on the top leads.",
        "- Apply kill conditions aggressively.",
        "- Return NO_CLEAN_CANDIDATE if all leads die.",
        "",
        f"Top leads to consider: {top_ids}",
        f"Target decision: {pack.target_decision.decision}",
        "",
        "A human always makes the security call. Senior triage does not confirm "
        "vulnerabilities and does not replace human review.",
        "",
        _footer(),
        "",
    ]
    return "\n".join(lines)


def _sorted_leads(leads: list[M.LeadCandidate]) -> list[M.LeadCandidate]:
    order = {M.LEAD_PURSUE: 0, M.LEAD_PARK: 1, M.LEAD_KILL: 2}
    return sorted(
        leads,
        key=lambda x: (-x.research_priority_score, order.get(x.decision, 9), x.id),
    )
