# Launch Report OS

Arkheionx Launch Report OS turns scanner output into a client-facing launch
readiness artifact for authorized repositories.

It is not a formal audit, not a security guarantee, and not a vulnerability
confirmation. It helps teams organize pre-audit work before mainnet, material
TVL, formal audit intake, or external review.

## What It Includes

- Executive summary.
- Readiness score and score band.
- Semantic-lite and Slither status.
- Launch readiness snapshot by area.
- Top evidence-backed readiness gaps.
- Recommended remediation roadmap.
- Pre-launch checklist.
- Links to generated Arkheionx artifacts.
- Limitations and formal audit recommendation.

## Generate Locally

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --launch-report-output ARKHEIONX_LAUNCH_REPORT.md \
  --executive-summary-output ARKHEIONX_EXECUTIVE_SUMMARY.md \
  --remediation-roadmap-output ARKHEIONX_REMEDIATION_ROADMAP.md
```

## GitHub Action Usage

```yaml
with:
  output: ARKHEIONX_PRE_AUDIT_REPORT.md
  json-output: arkheionx-report.json
  launch-report-output: ARKHEIONX_LAUNCH_REPORT.md
  executive-summary-output: ARKHEIONX_EXECUTIVE_SUMMARY.md
  remediation-roadmap-output: ARKHEIONX_REMEDIATION_ROADMAP.md
```

## Paid Service Fit

A Launch Readiness Report can be reviewed manually as part of a paid Launch
Report engagement. Manual review should remove false positives, clarify
priority, add maintainer context, and prepare a formal audit handoff package.

## Limitations

The Launch Report is generated from local/static readiness findings. It does
not replace professional review and does not certify protocol safety.
