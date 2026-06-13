"""Render the V9 hunter pack to human-readable artifacts (00..90).

Direct, senior tone: pursue this, prove that, kill the rest. The renderer only emits
the approved decision vocabulary; it never emits a confirmed-vulnerability claim, a
final severity, an auto-submit verdict, or a masked RPC endpoint's secret. Every
artifact carries the same safety footer.
"""
from __future__ import annotations

from . import lane_templates
from . import models as M

ARTIFACT_ORDER = (
    "00-run-context.md", "01-scope-map.md", "02-source-provenance.md", "03-known-issue-map.md",
    "04-freshness-map.md", "05-deployment-reality.md", "06-value-flow-map.md", "07-state-machine-map.md",
    "08-top-leads.md", "09-poc-plans.md", "10-submission-risk.md", "11-report-filter.md",
    "90-engine-evaluation.md",
)

_FOOTER = (
    "---",
    "Arkheionx hunter mode is a local-first senior research decision engine. It is not a "
    "finding, not a severity, and not a confirmed vulnerability.",
    "No live-chain mutation. Read-only RPC only when explicitly provided (endpoint masked). "
    "No auto-submit. A human always makes the security call.",
)


def _footer() -> str:
    return "\n".join(_FOOTER)


def _bullets(items, empty="(none)") -> str:
    items = [str(i) for i in items if i]
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def render_all(pack: M.HunterPack) -> dict:
    return {
        "00-run-context.md": _run_context(pack),
        "01-scope-map.md": _scope_map(pack),
        "02-source-provenance.md": _source(pack),
        "03-known-issue-map.md": _known(pack),
        "04-freshness-map.md": _freshness(pack),
        "05-deployment-reality.md": _deployment(pack),
        "06-value-flow-map.md": _value_flow(pack),
        "07-state-machine-map.md": _state_machine(pack),
        "08-top-leads.md": _top_leads(pack),
        "09-poc-plans.md": _poc_plans(pack),
        "10-submission-risk.md": _submission_risk(pack),
        "11-report-filter.md": _report_filter(pack),
        "90-engine-evaluation.md": _engine_eval(pack),
    }


def _run_context(pack: M.HunterPack) -> str:
    ctx = pack.context
    c = pack.counts
    lines = [
        "# 00 — Run Context", "",
        "Hunter mode answers: where to spend the next 30-90 minutes for the highest chance "
        "of a fresh, in-scope, payable, non-duplicate, attacker-reachable bug.", "",
        f"- Repo: {ctx.repo_path}",
        f"- Scope file: {ctx.scope_file or '(none)'}",
        f"- Known corpus: {ctx.known_path or '(none)'} | Audits: {ctx.audits_path or '(none)'}",
        f"- Addresses: {ctx.addresses_file or '(none)'} ({pack.address_parse.status})",
        f"- Source dir: {ctx.source_dir or '(none)'} | recovery mode: {ctx.source_recovery_mode}",
        f"- Baseline: ref={ctx.baseline_ref or '-'} since={ctx.since_date or '-'} audit_date={ctx.audit_date or '-'}",
        f"- RPC mode: {ctx.rpc_mode} | endpoint: {ctx.rpc_endpoint_masked or 'not provided'} (masked)",
        f"- Strict context: {ctx.strict_context}",
        "",
        "## Run snapshot",
        f"- Scope status: {pack.program_identity.scope_status} ({pack.program_identity.scope_confidence})",
        f"- Source: {pack.source_provenance.overall_status}",
        f"- Dedup quality: {pack.dedup_quality.status}",
        f"- Deployment: {pack.deployment_reality.status} | mismatches: {len(pack.deployment_reality.mismatches)}",
        f"- Registry diff: {pack.registry_diff.status}",
        f"- Value paths: {len(pack.value_paths)} | State machines: {len(pack.state_machines)} "
        f"(value-gating: {sum(1 for s in pack.state_machines if s.touches_value)})",
        f"- Call edges: {len(pack.call_edges)}",
        f"- Leads: {c.get('leads', 0)} | pursue_now {c.get('pursue_now', 0)} | needs_poc {c.get('needs_poc', 0)} "
        f"| park {c.get('park', 0)} | kill {c.get('kill', 0)}",
        "",
        "## Missing context", _bullets(pack.missing_context, empty="None noted."),
        "", "## Engine warnings", _bullets(pack.engine_warnings, empty="None."),
        "", _footer(), "",
    ]
    return "\n".join(lines)


def _scope_map(pack: M.HunterPack) -> str:
    p = pack.program_identity
    lines = [
        "# 01 — Scope Map / Program Identity", "",
        f"Scope status: {p.scope_status} ({p.scope_confidence} confidence)", "",
        f"- Program: {p.program_name or '(not stated)'}",
        f"- Company: {p.company or '(not stated)'}",
        f"- Platform: {p.platform or '(not stated)'}",
        f"- Bounty URL: {p.bounty_url or '(not stated)'}",
        f"- PoC required: {'yes' if p.poc_required else 'unstated'}",
        f"- Reward severities: {', '.join(p.reward_severities) or '(not stated)'}",
        f"- Chain ids: {', '.join(p.chain_ids) or '(none)'}",
        "",
        "## Repos", _bullets(p.repo_urls, empty="(none referenced)"),
        "", "## Contract families", _bullets(p.contract_families, empty="(none detected)"),
        "", "## In-scope keywords", _bullets(p.in_scope_keywords, empty="(none parsed)"),
        "", "## Out-of-scope keywords", _bullets(p.out_of_scope_keywords, empty="(none parsed)"),
        "", "## Trusted roles", _bullets(p.trusted_roles, empty="(none detected)"),
        "", "## Known-issue links", _bullets(p.known_issue_links, empty="(none referenced)"),
        "", "## Scope collision warnings", _bullets(p.scope_warnings, empty="None — scope looks coherent."),
        "", "## Notes", _bullets(p.notes, empty="None."),
    ]
    if p.scope_status == M.SCOPE_COLLISION:
        lines += ["", "> Scope collision unresolved -> all leads are capped to PARK_SCOPE until the "
                  "exact product / version / chain is confirmed."]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _source(pack: M.HunterPack) -> str:
    sp = pack.source_provenance
    lines = [
        "# 02 — Source Provenance", "",
        f"Overall source status: {sp.overall_status}",
        f"Recovery mode: {sp.recovery_mode} | network recovery attempted: {sp.network_recovery_attempted}",
        "", "## Per-contract source records",
    ]
    if not sp.records:
        lines.append("- (no per-contract records; judged on local repo presence)")
    for r in sp.records:
        lines += [
            f"### {r.get('contract_name') or '(unnamed)'} {('@ ' + r['address']) if r.get('address') else ''}".rstrip(),
            f"- Origin: {r.get('source_origin')} | match: {r.get('match_type') or '-'} | files: {r.get('file_count', 0)}",
            f"- Path: {r.get('source_path') or '-'} | compiler: {r.get('compiler_version') or '-'}",
            f"- Limitations: {', '.join(r.get('limitations', [])) or 'none'}",
        ]
    lines += ["", "## Notes", _bullets(sp.notes), "",
              "## How this affects priority",
              _bullets([
                  "SOURCE_LOCAL / PROVIDED / SOURCIFY_EXACT / ETHERSCAN_VERIFIED back source-level analysis.",
                  "SOURCE_ABI_ONLY / SOURCE_MISSING cap source-level leads to PARK_SOURCE.",
                  "A source-recovery gap on a value-bearing contract becomes its own SOURCE_RECOVERY_GAP lead.",
              ]),
              "", _footer(), ""]
    return "\n".join(lines)


def _known(pack: M.HunterPack) -> str:
    q = pack.dedup_quality
    km = {k.lead_id: k for k in pack.known_matches}
    lines = [
        "# 03 — Known Issue / Dedup Map", "",
        f"Corpus quality: {q.status}",
        f"- Parsed docs: {q.parsed_docs} | known: {q.known_docs} | audit: {q.audit_docs} | test: {q.test_docs}",
        f"- Unparsed: {', '.join(q.unparsed) or 'none'}",
        "## Quality reasons", _bullets(q.reasons),
    ]
    if q.status == M.DEDUP_BLIND:
        lines += ["", "> DEDUP_BLIND: no usable known/audit/test material. Normal leads are capped to "
                  "PARK_DEDUP unless a hard deployment mismatch or explicit post-audit freshness exists."]
    lines += ["", "## Per-lead dedup verdict"]
    for lead in pack.ranked_leads():
        sig = km.get(lead.lead_id)
        if sig is None:
            continue
        lines += [
            "", f"### {lead.lead_id} — {lead.title}",
            f"- Known match: {sig.known_match_status} | corpus: {sig.dedup_status} | "
            f"confidence: {sig.known_issue_confidence} (cap {sig.dedup_confidence_cap})",
            f"- Similarity: {sig.dedup_similarity_score} | public test covered: {'yes' if sig.public_test_covered else 'no'}",
            "- Reasoning:", _bullets(sig.dedup_reasoning, empty="(none)"),
        ]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _freshness(pack: M.HunterPack) -> str:
    fv = {f.lead_id: f for f in pack.freshness_verdicts}
    lines = ["# 04 — Freshness Map", "",
             "Freshness is evidence-based. A positive status requires a baseline diff, a deployment "
             "mismatch, a live-registry entry, an audit-coverage gap, or a user fresh-allowlist.", ""]
    for lead in pack.ranked_leads():
        f = fv.get(lead.lead_id)
        if f is None:
            continue
        effect = ("boost" if f.freshness_status in M.FRESHNESS_POSITIVE else
                  ("downrank" if f.freshness_status == M.AUDIT_COVERED else "neutral / capped"))
        lines += [
            f"### {lead.lead_id} — {lead.title}",
            f"- Status: {f.freshness_status} ({f.freshness_confidence}) | score: {f.score} | effect: {effect}",
            "- Evidence:", _bullets([e.get("reason") or e.get("source_path") or str(e) for e in f.freshness_evidence],
                                    empty="(no concrete change evidence)"),
            "- Caps:", _bullets(f.freshness_caps, empty="(none)"),
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _deployment(pack: M.HunterPack) -> str:
    d = pack.deployment_reality
    lines = [
        "# 05 — Deployment Reality", "",
        f"Status: {d.status} | RPC mode: {d.rpc_mode} | chain id: {d.chain_id or 'not checked'}",
        f"Endpoint: {d.rpc_endpoint_masked or 'not provided'} (masked)",
        f"Addresses provided: {'yes' if d.addresses_provided else 'no'}",
        f"Reason: {d.reason}", "",
        "## Read-only results",
    ]
    if not d.results:
        lines.append("- (no live results; provide --rpc-url for read-only verification)")
    for r in d.results:
        lines.append(
            f"- {r.get('name')} {r.get('address')}: status={r.get('status')} pattern={r.get('proxy_pattern') or '-'} "
            f"has_code={r.get('has_code')} code_size={r.get('code_size')}")
        if r.get("implementation") or r.get("expected_implementation"):
            lines.append(f"    implementation={r.get('implementation') or '-'} expected={r.get('expected_implementation') or '-'}")
        if r.get("beacon"):
            lines.append(f"    beacon={r.get('beacon')}")
        for call in r.get("calls", []):
            lines.append(f"    call {call.get('name')} = {call.get('value')}")
    if d.mismatches:
        lines += ["", "## Source-vs-deployed mismatches (priority signal, not a bug)"]
        for m in d.mismatches:
            lines.append(f"- {m.get('name')} {m.get('address')}: {m.get('type')} "
                         f"expected={m.get('expected', '-')} live={m.get('live', '-')}")
    lines += ["", "## Recommended read-only checks", _bullets(d.recommended_checks),
              "", "## Safe read-only commands (run these yourself; nothing is executed here)",
              _bullets(d.safe_commands, empty="Provide --addresses to generate command suggestions."),
              "", "## Live registry / live-set diff", f"- Status: {pack.registry_diff.status}",
              f"- Live entries: {len(pack.registry_diff.live_entries)} | listed: {len(pack.registry_diff.listed_entries)}",
              f"- Extra (live not listed): {', '.join(pack.registry_diff.extra_entries) or 'none'}",
              f"- Missing (listed not live): {', '.join(pack.registry_diff.missing_entries) or 'none'}",
              "- Notes:", _bullets(pack.registry_diff.notes, empty="(registry diff not run)"),
              "", "## Notes", _bullets(d.notes), "", _footer(), ""]
    return "\n".join(lines)


def _value_flow(pack: M.HunterPack) -> str:
    lines = ["# 06 — Value-Flow Map", "",
             "Where value enters, moves, and exits, the accounting/state variables that gate each "
             "path, and the external-call ordering. A value path is a research lens, not a finding.", ""]
    if not pack.value_paths:
        lines.append("- (no value paths extracted from the local source)")
    for vp in pack.value_paths:
        lines += [
            f"### {vp.path_id} — {vp.exit_function or vp.entry_function or 'value path'}",
            f"- Entry: {vp.entry_function or '-'} ({vp.entry_asset or 'asset n/a'})",
            f"- Exit: {vp.exit_function or '-'} -> recipient: {vp.recipient or '-'}",
            f"- Accounting vars: {', '.join(vp.accounting_variables) or '(none)'}",
            f"- State-machine vars: {', '.join(vp.state_machine_variables) or '(none)'}",
            f"- External calls: {', '.join(vp.external_calls) or '(none)'}",
            f"- State update ordering: {vp.state_update_ordering}",
            f"- Attacker reachability: {vp.attacker_reachability} | trusted role required: {vp.trusted_role_required}",
            f"- Impact if broken: {vp.impact_if_broken}",
            f"- Source: {', '.join(vp.source_lines) or '-'}",
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _state_machine(pack: M.HunterPack) -> str:
    lines = ["# 07 — State-Machine Map", "",
             "State machines are boosted only when they gate value movement. A benign status enum "
             "with no value link is recorded but not boosted.", ""]
    if not pack.state_machines:
        lines.append("- (no state machines detected)")
    for sm in pack.state_machines:
        lines += [
            f"### {sm.state_machine_id} — {sm.contract}"
            + (f" [{sm.subtype}]" if sm.subtype else ""),
            f"- Touches value: {'YES (boosted)' if sm.touches_value else 'no (not boosted)'}",
            f"- State variables: {', '.join(sm.state_variables) or '(none)'}",
            f"- Transitions: {'; '.join(sm.transitions) or '(none parsed)'}",
            f"- Value surfaces: {', '.join(sm.value_surfaces) or '(none)'}",
            "- Notes:", _bullets(sm.notes),
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _top_leads(pack: M.HunterPack) -> str:
    top = pack.top_leads(pack.counts.get("top", M.TOP_LEAD_LIMIT))
    lines = [f"# 08 — Top Leads (max {pack.counts.get('top', M.TOP_LEAD_LIMIT)})", ""]
    if not top:
        lines += ["NO_PURSUEABLE_LEADS", "",
                  "No lead clears the bar right now. See 11-report-filter.md and 90-engine-evaluation.md.",
                  "", _footer(), ""]
        return "\n".join(lines)
    for i, lead in enumerate(top, 1):
        lines += [
            f"## Lead {i} — {lead.title}",
            f"- Lead id / type: {lead.lead_id} / {lead.lead_type}",
            f"- Decision: {lead.decision} (score {lead.score})",
            f"- Surface: {lead.surface or lead.contract}",
            f"- Scope: {lead.scope_confidence} | Freshness: {lead.freshness_status} | Dedup: {lead.known_match_status} "
            f"({lead.dedup_status})",
            f"- Deployment: {lead.deployment_status or 'not verified'} | Source: {lead.source_status}",
            f"- Attacker reachability: {lead.attacker_reachability} | Materiality: {lead.materiality} | "
            f"Trusted-role risk: {lead.trusted_role_risk}",
            f"- Expected severity ceiling: {lead.expected_severity_ceiling} | payout EV: {lead.expected_payout_ev}/100",
            f"- Value paths: {', '.join(lead.value_path_ids) or '-'} | State machines: {', '.join(lead.state_machine_ids) or '-'}",
            f"- PoC plan: {lead.poc_plan_id or '(none)'}",
            "- Why this decision:", _bullets(lead.decision_reasons),
            "- Kill conditions:", _bullets(lead.kill_conditions),
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _poc_plans(pack: M.HunterPack) -> str:
    lines = ["# 09 — PoC Plans", "",
             "A minimal PoC plan exists only for a pursueable lead. No plan is made for a killed "
             "duplicate, an out-of-scope lead, or a trusted-role-only lead.", ""]
    if not pack.poc_plans:
        lines.append("- (no pursueable leads; no PoC plans)")
    for p in pack.poc_plans:
        lines += [
            f"## {p.poc_plan_id} — lead {p.lead_id} ({p.status})",
            f"- Hypothesis: {p.hypothesis}",
            f"- Why eligible: {p.why_eligible}",
            f"- Why not duplicate: {p.why_not_duplicate}",
            f"- Why not OOS: {p.why_not_oos}",
            f"- Why not trusted-role-only: {p.why_not_trusted_role_only}",
            f"- Baseline: {p.baseline}",
            f"- Attack: {p.attack}",
            f"- Expected assertion: {p.expected_assertion}",
            f"- Measured impact: {p.measured_impact}",
            f"- Required actors: {', '.join(p.required_actors)}",
            f"- Required balances: {', '.join(p.required_balances)}",
            f"- Required contract state: {', '.join(p.required_contract_state)}",
            f"- Required mocks: {', '.join(p.required_mocks)}",
            f"- Existing harness: {p.existing_harness}",
            f"- Target files: {', '.join(p.target_files) or '-'}",
            f"- Target functions: {', '.join(p.target_functions) or '-'}",
            f"- Suggested test filename: {p.suggested_test_filename}",
            "- Minimal skeleton:", "", "```solidity", p.minimal_skeleton, "```",
            f"- Kill condition: {p.kill_condition}",
            f"- Stop condition: {p.stop_condition}",
            f"- Report condition: {p.report_condition}",
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _submission_risk(pack: M.HunterPack) -> str:
    lines = ["# 10 — Submission Risk", "",
             "Why a reviewer might reject a report — estimated before any time is spent writing one.", ""]
    for r in pack.submission_risks:
        lines += [
            f"## {r.lead_id} — {r.status}",
            f"- Expected severity ceiling: {r.expected_severity_ceiling} | payout eligibility: {r.expected_payout_eligibility}",
            f"- Duplicate rejection risk: {r.duplicate_rejection_risk}",
            f"- OOS rejection risk: {r.oos_rejection_risk}",
            f"- Trusted-role rejection risk: {r.trusted_role_rejection_risk}",
            f"- Known-corpus gap risk: {r.known_corpus_gap_risk}",
            f"- Deployment-context gap risk: {r.deployment_context_gap_risk}",
            f"- Materiality risk: {r.materiality_risk} | proof difficulty risk: {r.proof_difficulty_risk}",
            "- Reviewer pushback:", _bullets(r.reviewer_pushback, empty="(low expected pushback)"),
            "- Evidence needed:", _bullets(r.evidence_needed, empty="(none beyond a passing PoC)"),
            f"- Submit-ready threshold: {r.submit_ready_threshold}",
            "",
        ]
    lines += [_footer(), ""]
    return "\n".join(lines)


def _report_filter(pack: M.HunterPack) -> str:
    lines = ["# 11 — Report Filter", "",
             "Default is Submit: NO. A row only relaxes to AFTER_POC_ASSERTION_PASSES when every gate "
             "passes. A human rewrite is always required, and no report is written before the PoC "
             "assertion passes.", "",
             "| Lead | Type | Severity | Dedup | Attacker | Material | PoC | Submit |",
             "| ---- | ---- | -------- | ----- | -------- | -------- | --- | ------ |"]
    for row in pack.report_filter:
        lines.append(
            f"| {row.lead_id} {row.title[:28]} | {row.lead_type} | {row.severity_candidate} | {row.dedup} | "
            f"{row.attacker} | {row.materiality} | {row.poc_status} | {row.submit} |")
    lines += ["", "## Per-lead reasons"]
    for row in pack.report_filter:
        lines += [f"- {row.lead_id}: Submit {row.submit} (human rewrite required) — {row.reason}"]
    lines += ["", _footer(), ""]
    return "\n".join(lines)


def _engine_eval(pack: M.HunterPack) -> str:
    e = pack.engine_evaluation
    s = e.scores
    lines = [
        "# 90 — Engine Evaluation", "",
        "Honest self-assessment. No marketing. Every signal is heuristic and unconfirmed.", "",
        "## Quality read",
        f"- Scope parsing: {e.scope_parsing_quality}",
        f"- Source recovery: {e.source_recovery_quality}",
        f"- Known corpus: {e.known_corpus_quality}",
        f"- Dedup: {e.dedup_quality}",
        f"- Freshness: {e.freshness_quality}",
        f"- Deployment reality: {e.deployment_reality_quality}",
        f"- Value-flow: {e.value_flow_quality}",
        f"- State-machine: {e.state_machine_quality}",
        f"- Top lead quality: {e.top_lead_quality}",
        f"- PoC planner: {e.poc_planner_usefulness}",
        f"- Submission risk: {e.submission_risk_usefulness}",
        "",
        "## Risk read",
        f"- False positive risk: {e.false_positive_risk}",
        f"- False negative risk: {e.false_negative_risk}",
        f"- Missed surface risk: {e.missed_surface_risk}",
        f"- Manual review dependency: {e.manual_review_dependency}",
        f"- Biggest uncertainty: {e.biggest_uncertainty}",
        "",
        "## What Arkheionx got wrong", _bullets(e.what_arkheionx_got_wrong),
        "", "## What Arkheionx should fix next", _bullets(e.what_to_fix_next),
        "", "## Scores (0-10)",
        f"- Scope: {s.get('scope')}",
        f"- Dedup: {s.get('dedup')}",
        f"- Freshness: {s.get('freshness')}",
        f"- Deployment: {s.get('deployment')}",
        f"- Value-flow: {s.get('value_flow')}",
        f"- State-machine: {s.get('state_machine')}",
        f"- Lead discovery: {s.get('lead_discovery')}",
        f"- PoC planning: {s.get('poc_planning')}",
        f"- Submission risk: {s.get('submission_risk')}",
        f"- Overall: {s.get('overall')}",
        "", _footer(), "",
    ]
    return "\n".join(lines)


def lane_template_reference() -> str:
    """A static reference of the universal bug-lane templates (not part of the pack)."""
    lines = ["# Universal Bug-Lane Templates (research lenses, not findings)", ""]
    for tid, t in lane_templates.all_templates().items():
        lines += [
            f"## {tid}",
            f"- Patterns: {', '.join(t['patterns'])}",
            f"- Severity ceiling: {t['severity_ceiling']}",
            f"- Minimal PoC shape: {t['minimal_poc_shape']}",
        ]
    return "\n".join(lines)
