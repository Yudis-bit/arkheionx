# Pre-Audit Sprint Workflow

Arkheionx Pre-Audit Sprint output turns readiness findings into a practical
3, 5, 7, or 10 day remediation plan.

It is a defensive planning document. It is not a formal audit and does not
guarantee security.

## Who It Is For

- Indie DeFi teams preparing for first audit intake.
- Grant-funded builders preparing launch readiness updates.
- Small DAOs organizing security remediation work.
- Protocol teams preparing for a contest or external review.

## Sprint Lengths

| Length | Best Fit |
|---:|---|
| 3 days | Focused triage, blockers, and handoff package. |
| 5 days | Standard readiness sprint for small teams. |
| 7 days | Deeper invariant, docs, and role/oracle/accounting work. |
| 10 days | Larger protocol prep with more remediation cycles. |

## Generate A Sprint Plan

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --issue-plan-output ARKHEIONX_ISSUE_PLAN.json \
  --sprint-plan-output ARKHEIONX_SPRINT_PLAN.md \
  --sprint-days 5
```

## How Issue Plans Map To Sprint Backlog

Arkheionx groups findings into:

- launch blockers;
- high-priority readiness gaps;
- medium-priority hardening tasks;
- documentation tasks;
- low-confidence manual review tasks.

Each backlog item includes a finding ID, suggested owner placeholder,
expected output, and acceptance checklist.

## Baseline Diff

Use baseline diff mode at the end of the sprint to show new, resolved,
unchanged, and changed readiness gaps:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --compare-baseline arkheionx.baseline.json \
  --diff-output ARKHEIONX_DIFF.md
```

## Paid Service Fit

In a paid Pre-Audit Sprint, the generated plan can become the working
remediation board. Manual review should triage issue-plan tasks, tune
priorities, and produce a final readiness handoff.

## Limits

The sprint plan is generated from heuristic readiness findings. It should be
reviewed by maintainers before work begins.
