# Arkheionx Output Profiles

Arkheionx v1.8.0 supports report profiles that tune Markdown report verbosity
without changing the defensive/static scanner model.

Profiles are configured with `output_profile` in `.arkheionx.json`.

| Profile | Use When | Behavior |
|---|---|---|
| `concise` | Founder or first-pass review | Short summary, Fix First, top gaps, minimal evidence. |
| `standard` | Default local review | Balanced evidence, grouping, related knowledge, and suggested tests. |
| `full` | Deep pre-audit prep | More evidence, all findings, detailed related knowledge, and scan context. |
| `ci` | CI artifact or PR workflow | Compact output with score, Fix First, active findings, and generated artifacts. |

Example:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --config examples/configs/ci.config.json \
  --output reports/ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output reports/arkheionx-report.json
```

Profiles only affect presentation. Findings remain readiness signals and manual
review remains required.
