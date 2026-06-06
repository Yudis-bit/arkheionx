# Arkheionx Case Study Template

> This template is for defensive, authorized readiness work. It is not a formal
> audit report and does not guarantee security.

## Project

- Name:
- Repository path or public URL:
- Protocol type:
- Commit or scan date:
- Arkheionx version:

## Scope

- In scope:
- Out of scope:
- Demo, internal, or external:
- Authorization notes:

## Scan Command

```sh
python3 scripts/pre_audit_scan.py \
  --root <path> \
  --protocol-type auto \
  --output <report.md> \
  --json-output <report.json>
```

## Readiness Snapshot

- Score:
- Score band:
- Top rule packs:
- Semantic-lite status:
- Slither status:

## Top Findings

| ID | Priority | Confidence | Theme | Evidence |
|---|---|---|---|---|
| ARK-... | ... | ... | ... | ... |

## Evidence Examples

- `path/File.sol:line` in `functionName`: why this evidence matters.
- `test/File.t.sol`: matching or missing test evidence.

## Remediation Actions

- [ ] Add or improve tests.
- [ ] Document assumptions.
- [ ] Review privileged roles.
- [ ] Re-run Arkheionx.
- [ ] Compare against baseline.

## Before / After

| Metric | Before | After |
|---|---:|---:|
| Score | | |
| Active findings | | |
| High-confidence findings | | |
| Suppressed findings | | |

## What This Demonstrates

- Reproducible readiness workflow.
- Evidence-backed findings.
- Rule calibration opportunities.

## What This Does Not Prove

- It does not prove the protocol is secure.
- It does not replace a formal audit.
- It does not confirm vulnerabilities.
- It does not inspect deployed contracts.
