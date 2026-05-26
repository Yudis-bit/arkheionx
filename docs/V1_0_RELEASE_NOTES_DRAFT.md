# Arkheionx v1.0.0 Release Notes Draft

Arkheionx v1.0.0 is the first stable public release of the GitHub-native DeFi
Security Memory and Pre-Audit Readiness OS.

Short version: not an audit. A way to prepare for one.

## What Is Stable

- Local pre-audit readiness scanner.
- GitHub Action workflow.
- Markdown, JSON, SARIF, baseline, diff, issue checklist, and issue plan
  outputs.
- Launch Report, Pre-Audit Sprint Plan, Contest Readiness, Executive Summary,
  and Remediation Roadmap outputs.
- Semantic-lite evidence, optional local Slither enrichment, confidence
  calibration, negative evidence detection, and generated-artifact ignore
  safeguards.
- Security memory graph, finding knowledge map, rule calibration matrix, and
  local search helper.

## Added For v1.0.0

- Stable CLI reference.
- Stable GitHub Action input reference.
- JSON schemas for the main public outputs.
- Schema reference and compatibility policy.
- Output artifact naming guide.
- Documentation link checker.
- Version consistency checker.
- Safety wording checker.
- v1.0 release checklist.

## Safety Boundaries

Arkheionx remains local/static and defensive:

- no RPC or live-chain calls;
- no deployed-contract scanning;
- no transaction submission;
- no private key or mnemonic handling;
- no exploit automation;
- no bounty guarantee;
- no formal audit claim.

Generated findings are readiness signals and review prompts, not vulnerability
confirmations.

## Known Limitations

- Static and heuristic analysis only.
- Optional Slither enrichment depends on local installation or provided JSON.
- False positives and false negatives remain possible.
- Manual review remains required before production launch, formal audit, bug
  bounty, or contest intake.

## Suggested Release Command

Do not run until the release is approved from `main`:

```sh
git tag v1.0.0
git push origin v1.0.0
```
