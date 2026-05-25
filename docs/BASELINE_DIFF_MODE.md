# Baseline Diff Mode

Arkheionx v0.4.0 can write a compact baseline JSON file and compare future
scans against it.

Baseline diff mode helps teams track readiness improvement over time:

- new readiness gaps;
- resolved readiness gaps;
- unchanged readiness gaps;
- changed readiness gaps;
- suppressed readiness gaps.

This is a local/static comparison. It is not a formal audit.

## Create A Baseline

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/vault-risk-fixture \
  --protocol-type vault \
  --output examples/reports/vault-risk-fixture-pre-audit-report.md \
  --json-output examples/reports/vault-risk-fixture-pre-audit-report.json \
  --baseline-output examples/reports/vault-risk-fixture.baseline.json
```

The baseline contains stable finding fingerprints, IDs, titles, categories,
priorities, confidence, affected files, and tags.

## Compare Against A Baseline

```sh
python3 scripts/pre_audit_scan.py \
  --root examples/vault-risk-fixture \
  --protocol-type vault \
  --compare-baseline examples/reports/vault-risk-fixture.baseline.json \
  --output examples/reports/vault-risk-fixture-diff-report.md \
  --json-output examples/reports/vault-risk-fixture-diff-report.json \
  --diff-output examples/reports/vault-risk-fixture-diff.md \
  --diff-json-output examples/reports/vault-risk-fixture-diff.json
```

When a baseline is provided, the Markdown report, JSON report, summary, PR
comment body, and generated issue checklist include diff context.

## Fingerprints

Arkheionx fingerprints use:

- finding ID;
- category;
- normalized title;
- detected signals;
- affected files;
- protocol type.

They do not use timestamps, absolute paths, score, or generated output paths.

## CI Usage

For early teams, start with non-blocking diffs. Mature teams can later add
explicit gates such as:

```sh
--fail-on-new-high
--fail-score-below 70
--fail-on-unsuppressed-high
```

## How Not To Misuse It

- Do not treat an unchanged baseline as proof of safety.
- Do not suppress findings without a written reason.
- Do not use baseline diff mode as a substitute for manual review or formal
  audit.

## Limitations

- Fingerprints are stable for heuristic findings, not semantic program facts.
- Renaming files or changing terminology can change fingerprints.
- Resolved means "not detected by this scanner run," not "proven fixed."
