# Report UX

Arkheionx v1.8.0 improves report readability for founders, engineers,
reviewers, audit-prep teams, CI users, and ecosystem operators.

Markdown reports now emphasize:

- a concise executive summary;
- Fix First prioritization;
- findings grouped by rule family;
- findings grouped by confidence;
- suppression and config summaries;
- generated artifact ignore status;
- suggested tests and invariant candidates.

JSON reports keep backward-compatible fields and add:

- `fix_first`;
- `findings_by_rule_family`;
- `findings_by_confidence`;
- `active_findings_count`;
- `suppressed_findings_count`;
- `suppression_summary`;
- `report_ux`.

Issue plans include Fix First ordering, rule family, confidence reason, and
suggested test/invariant content so generated remediation tasks are easier to
triage.

These changes improve presentation only. Arkheionx remains a local/static
pre-audit readiness tool, not a formal audit.
