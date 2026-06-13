"""Render the human-readable Senior Triage Pack (artifacts 00-09), v2.

Tone is direct and senior: pursue this, park that, kill the rest. v2 adds located
dedup evidence (source path + line range), freshness evidence, read-only deployment
results and source-vs-deployed mismatches, and an explainable score breakdown with
boosts and caps. The renderer only ever emits the approved decision vocabulary; it
never emits a confirmed-vulnerability claim, a final severity, or a submit verdict.
"""
from __future__ import annotations

from . import models as M

ARTIFACT_ORDER = (
    "00-target-decision.md", "01-bounty-eligibility.md", "02-known-issue-map.md",
    "03-freshness-diff.md", "04-deployment-reality.md", "05-lead-scoreboard.md",
    "06-top-3-leads.md", "07-do-not-touch.md", "08-next-commands.md", "09-agent-brief.md",
)

_FOOTER = (
    "---",
    "Senior triage is a local/static planning artifact. It is not a finding, not a "
    "severity, and not a confirmed vulnerability.",
    "No RPC by default. No live-chain mutation. No auto-submit. Human review is required.",
)


def _footer() -> str:
    return "\n".join(_FOOTER)


def _bullets(items, empty="(none)") -> str:
    items = [i for i in items if i]
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def _evidence_lines(evidence) -> str:
    lines = []
    for e in evidence or []:
        path = e.get("source_path", "")
        ls, le = e.get("line_start", 0), e.get("line_end", 0)
        loc = f"{path}:L{ls}-L{le}" if ls else path
        reason = e.get("reason", "")
        excerpt = (e.get("excerpt", "") or "").strip()
        if excerpt:
            lines.append(f"- {loc} — {reason}: \"{excerpt}\"")
        else:
            lines.append(f"- {loc} — {reason}")
    return "\n".join(lines) if lines else "- (no located evidence)"


def _counts(pack):
    leads = pack.leads
    return {
        "leads": len(leads),
        "pursue": sum(1 for x in leads if x.decision == M.LEAD_PURSUE),
        "park": sum(1 for x in leads if x.decision == M.LEAD_PARK),
        "kill": sum(1 for x in leads if x.decision == M.LEAD_KILL),
        "do_not_touch": len(pack.do_not_touch),
    }


def render_all(pack) -> dict:
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


def _render_target(pack) -> str:
    c = _counts(pack)
    td = pack.target_decision
    e = pack.eligibility
    d = pack.deployment_reality
    blockers = sorted({lead.dedup_status for lead in pack.leads if lead.decision == M.LEAD_KILL})
    review_now = "Yes — but only the top lead(s) below." if c["pursue"] else "No — gather context first." if td.decision != M.TARGET_TOUCH else "Yes."
    lines = [
        "# Senior Triage — Target Decision", "",
        f"Decision: {td.decision}",
        f"Confidence: {td.confidence}",
        f"Reason: {td.reason}", "",
        "## Main blockers",
        _bullets(blockers, empty="None — leads were not blocked by dedup/scope."), "",
        "## Snapshot",
        f"- Leads: {c['leads']} | Pursue: {c['pursue']} | Park: {c['park']} | Kill: {c['kill']}",
        f"- Highest-priority leads: {c['pursue']} (see 06-top-3-leads.md)",
        f"- Do-not-touch: {c['do_not_touch']} (see 07-do-not-touch.md)",
        f"- Deployment reality: {d.status} | mismatches: {len(d.mismatches)}",
        "", "## Eligibility read (see 01-bounty-eligibility.md)",
        f"- Scope: {'provided' if e.scope_provided else 'none'} ({e.scope_confidence})",
        f"- Initial severity ceiling: {e.severity_ceiling}",
        f"- Initial duplicate risk: {e.initial_duplicate_risk}",
        "", "## Missing context",
        _bullets(pack.missing_context, empty="None noted."),
        "", f"## Should `arkheionx review` run now? {review_now}",
        "", _footer(), "",
    ]
    return "\n".join(lines)


def _render_eligibility(pack) -> str:
    e = pack.eligibility
    lines = [
        "# 01 — Bounty Eligibility", "",
        f"Target decision: {e.target_decision}",
        f"Scope confidence: {e.scope_confidence}",
        f"Initial severity ceiling: {e.severity_ceiling}",
        f"Initial duplicate risk: {e.initial_duplicate_risk}",
        f"Requires PoC: {'yes' if e.requires_poc else 'unstated'}",
        f"KYC noted: {'yes' if e.kyc_noted else 'no'}", "",
        "## Reward / severity notes", _bullets(e.reward_notes, empty="No reward or severity bands found in the scope."), "",
        "## Out-of-scope traps", _bullets(e.oos_traps, empty="None detected in the scope text."), "",
        "## Trusted-role traps", _bullets(e.trusted_role_traps, empty="None detected in the scope text."), "",
        "## Excluded impacts", _bullets(e.excluded_impacts, empty="None detected."), "",
        "## Missing context", _bullets(e.missing_context, empty="None noted."), "",
        "## Recommended action", f"- {e.recommended_action or 'Confirm scope before spending time.'}",
    ]
    if not e.scope_provided:
        lines += ["", "> target decision: NEEDS_MORE_CONTEXT",
                  "> reason: scope file does not include enough program rules to estimate bounty eligibility.",
                  "> Local technical triage still continues below."]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_known(pack, known_map) -> str:
    provided = bool(pack.context.known_path or pack.context.audits_path)
    lines = [
        "# 02 — Known Issue / Dedup Map", "",
        f"Known/audit material provided: {'yes' if provided else 'no'}",
        f"Dedup confidence: {'usable' if provided else 'LOW'}", "",
    ]
    if not provided:
        lines += ["Known issue map: NOT_PROVIDED", "Dedup confidence: LOW",
                  "Action: provide audit reports (--audits), public findings, repo issues, previous "
                  "reports, and known limitations (--known). Local tests are still scanned below.", ""]
    lines.append("## Per-lead dedup verdict")
    for lead in pack.leads:
        sig = known_map.get(lead.id)
        if sig is None:
            continue
        lines += [
            "", f"### {lead.id} — {lead.title}",
            f"- Status: {sig.status}",
            f"- Confidence: {sig.confidence} | similarity: {sig.similarity_score}/100 | duplicate risk: {sig.duplicate_risk_score}",
            f"- Public test covered: {'yes' if sig.public_test_covered else 'no'}",
            f"- Matched behavior: {', '.join(sig.matched_terms) if sig.matched_terms else '(none)'}",
            "- Evidence:",
            _evidence_lines(sig.evidence),
            f"- Decision: {lead.decision} — {sig.note}",
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_freshness(pack, fresh_map) -> str:
    lines = ["# 03 — Freshness Diff", "",
             "Fresh / post-audit / value-bearing surface ranks higher. Stale, over-audited "
             "surface ranks lower.", ""]
    base = pack.freshness_diff[0].baseline if pack.freshness_diff else "none"
    lines.append(f"Baseline: {base}")
    lines.append("")
    for lead in pack.leads:
        sig = fresh_map.get(lead.id)
        if sig is None:
            continue
        lines += [
            f"### {lead.id} — {lead.title}",
            f"- Status: {sig.status} | freshness score: {sig.score} | priority effect: {'boost' if sig.status in M.FRESHNESS_PRIORITY else ('downrank' if sig.status == M.STALE else 'neutral')}",
            f"- Changed paths: {', '.join(sig.changed_paths) if sig.changed_paths else '(none)'}",
            "- Evidence:",
            _evidence_lines(sig.evidence),
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _render_deployment(pack) -> str:
    d = pack.deployment_reality
    lines = [
        "# 04 — Deployment Reality", "",
        f"Status: {d.status}",
        f"RPC mode: {d.rpc_mode}",
        f"Chain id: {d.chain_id or 'not checked'}",
        f"Endpoint: {d.rpc_endpoint_masked or 'not provided'} (masked)",
        f"Addresses provided: {'yes' if d.addresses_provided else 'no'}",
        f"Reason: {d.reason}", "",
        "## Addresses",
    ]
    if d.addresses:
        for entry in d.addresses:
            lines.append(f"- {entry.get('name', 'contract')} ({entry.get('kind') or 'contract'}): {entry.get('address', '')}")
    else:
        lines.append("- (none provided)")
    if d.results:
        lines += ["", "## Read-only results"]
        for r in d.results:
            lines.append(
                f"- {r.get('name')}: status={r.get('status')} has_code={r.get('has_code')} "
                f"code_size={r.get('code_size')} code_hash={r.get('code_hash') or '-'}"
            )
            if r.get("implementation"):
                lines.append(f"    implementation={r.get('implementation')} expected={r.get('expected_implementation') or '-'}")
            for call in r.get("calls", []):
                lines.append(f"    call {call.get('name')} = {call.get('value')}")
    if d.mismatches:
        lines += ["", "## Source-vs-deployed mismatches (priority signal, not a bug)"]
        for m in d.mismatches:
            lines.append(f"- {m.get('name')} {m.get('address')}: {m.get('type')} expected={m.get('expected','-')} live={m.get('live','-')}")
    lines += [
        "", "## Recommended read-only checks", _bullets(d.recommended_checks),
        "", "## Safe read-only commands (run these yourself; nothing is executed here)",
        _bullets(d.safe_commands, empty="Provide --addresses to generate command suggestions."),
        "", "## How this affects priority",
        _bullets([
            "IMPLEMENTATION_CHANGED / LIVE_SOURCE_MISMATCH on a value-bearing contract boosts the lead.",
            "ADDRESS_NO_CODE kills a lead that depends on code at that address.",
            "LIVE_SOURCE_MATCH on audited code downranks (verified-stable).",
            "NOT_RUN / RPC_CHECK_FAILED caps live-wiring-dependent leads to PARK under fail-closed mode.",
        ]),
        "", "## Notes", _bullets(d.notes, empty="None."),
        "", _footer(), "",
    ]
    return "\n".join(lines)


def _render_scoreboard(pack) -> str:
    lines = [
        "# 05 — Lead Scoreboard", "",
        "Research-priority ordering (0-100). A time-allocation ranking, not a severity and "
        "not a validity claim.", "",
        "| Score | Decision | Dedup | Freshness | Deployment | Lead | Surface |",
        "| ----- | -------- | ----- | --------- | ---------- | ---- | ------- |",
    ]
    for lead in _sorted(pack.leads):
        lines.append(
            f"| {lead.research_priority_score} | {lead.decision} | {lead.dedup_status} "
            f"({lead.dedup_confidence}) | {lead.freshness_status} | {lead.deployment_status or 'n/a'} | "
            f"{lead.id} {lead.title} | {lead.surface} |"
        )
    lines += ["", "## Reasoning"]
    for lead in _sorted(pack.leads):
        lines += [
            "", f"### {lead.id} — {lead.title} — {lead.research_priority_score} ({lead.decision})",
            _bullets(lead.score_reasons),
        ]
        if lead.priority_boosts:
            lines += ["- Boosts:", _bullets(lead.priority_boosts)]
        if lead.decision_caps:
            lines += ["- Caps:", _bullets(lead.decision_caps)]
        if lead.score_breakdown:
            parts = ", ".join(f"{k}={v}" for k, v in lead.score_breakdown.items())
            lines.append(f"- Breakdown: {parts}")
        lines.append(f"- Kill condition: {lead.kill_condition}")
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_top3(pack) -> str:
    top = pack.top_leads(M.TOP_LEAD_LIMIT)
    lines = ["# 06 — Top Leads (max 3)", ""]
    if not top:
        lines += ["NO_HIGH_PRIORITY_LEADS", "",
                  "No lead is worth touching right now. See 07-do-not-touch.md and 08-next-commands.md.",
                  "", _footer(), ""]
        return "\n".join(lines)
    for i, lead in enumerate(top, 1):
        deploy_line = f"{lead.deployment_status}" if lead.deployment_status else "not verified"
        lines += [
            f"# Lead {i} — {lead.title}", "",
            f"Decision: {lead.decision}",
            f"Research Priority Score: {lead.research_priority_score}",
            f"Surface: {lead.surface}",
            f"Why this can matter: {lead.reason}",
            f"Why it may be fresh: {lead.freshness_status} ({lead.freshness_score}).",
            f"Deployment reality: {deploy_line}.",
            f"Scope fit: {pack.eligibility.scope_confidence} confidence; ceiling {lead.expected_severity_ceiling}.",
            f"Dedup status: {lead.dedup_status} ({lead.dedup_confidence}, dup risk {lead.duplicate_risk_score}).",
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


def _render_do_not_touch(pack) -> str:
    lines = ["# 07 — Do Not Touch", "",
             "Senior researchers save time by saying no. Do not spend time on these now.", ""]
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


def _render_next_commands(pack) -> str:
    c = _counts(pack)
    lines = ["# 08 — Next Commands", ""]
    if c["pursue"] or c["park"]:
        scope_flag = f" --scope-file {pack.context.scope_file}" if pack.context.scope_file else ""
        lines += [
            "1. Build the review pack for the top lead(s):",
            f"   arkheionx review {pack.context.repo_path}{scope_flag} --out .arkheionx/review",
            "2. Create a local Foundry test harness for the top lead only.",
            "3. Run a dedup search for the exact root behavior before writing a report.",
            "4. If deployment matters, verify live wiring read-only with --rpc-url + --addresses.",
            "5. Apply each lead's kill condition aggressively.",
        ]
    else:
        lines += [
            "1. Gather missing context.",
            "2. Add audit reports to ./audits and pass --audits.",
            "3. Add known findings to ./known and pass --known.",
            "4. Provide deployed addresses (--addresses) and optional read-only --rpc-url.",
            "5. Re-run: arkheionx triage with the added context.",
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _render_agent_brief(pack) -> str:
    top_ids = ", ".join(lead.id for lead in pack.top_leads(M.TOP_LEAD_LIMIT)) or "(none)"
    lines = [
        "# 09 — Agent Brief", "",
        "You are a follow-up research agent. Read this before doing anything.", "",
        "- Do not write a PoC before checking the known issue map (02).",
        "- Do not pursue KILL leads.",
        "- Do not claim vulnerabilities.",
        "- Do not submit. No auto-submit.",
        "- Do not ignore deployment mismatch.",
        "- Do not assume source equals deployed.",
        "- Do not make RPC or live-chain calls beyond read-only verification you were asked for.",
        "- Only work on the top leads.",
        "- Apply kill conditions aggressively.",
        "- Return NO_CLEAN_CANDIDATE if all leads die.",
        "", f"Top leads to consider: {top_ids}",
        f"Target decision: {pack.target_decision.decision}",
        "", "A human always makes the security call. Senior triage does not confirm "
        "vulnerabilities and does not replace human review.",
        "", _footer(), "",
    ]
    return "\n".join(lines)


def _sorted(leads):
    order = {M.LEAD_PURSUE: 0, M.LEAD_PARK: 1, M.LEAD_KILL: 2}
    return sorted(leads, key=lambda x: (-x.research_priority_score, order.get(x.decision, 9), x.id))
