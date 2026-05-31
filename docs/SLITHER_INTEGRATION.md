# Slither Integration

Arkheionx v0.6.0 and later can optionally enrich readiness findings with local Slither
output. Slither is not required, not installed automatically, and not used by
default.

The default Arkheionx scan remains local/static and dependency-free.

## Safety Model

- Slither integration is local only.
- Arkheionx does not call RPC endpoints.
- Arkheionx does not inspect deployed contracts.
- Arkheionx does not send source code to third-party services.
- If Slither is unavailable, Arkheionx continues unless `--slither-strict` is
  explicitly enabled.

## Run Slither Through Arkheionx

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --output ARKHEIONX_PRE_AUDIT_REPORT.md \
  --json-output arkheionx-report.json \
  --slither \
  --slither-output arkheionx-slither-summary.json
```

If `slither` is not on `PATH`, the report records a warning and continues.

## Use Existing Slither JSON

If your CI already produces Slither JSON, pass it directly:

```sh
python3 scripts/pre_audit_scan.py \
  --root . \
  --protocol-type auto \
  --json-output arkheionx-report.json \
  --slither-json slither-report.json
```

This avoids running Slither inside Arkheionx while still attaching local
detector evidence where it matches a readiness finding.

## GitHub Actions Example

Arkheionx does not install Slither automatically. Add your own install step if
you want Slither enrichment:

```yaml
steps:
  - uses: actions/checkout@v4
  - run: pipx install slither-analyzer
  - uses: Yudis-bit/DeFi-Exploit-PoCs/.github/actions/pre-audit@v2.2.0
    with:
      protocol-type: auto
      slither: "true"
      slither-output: arkheionx-slither-summary.json
```

Use the latest released Arkheionx tag for stable workflows. Use `@main` only
when intentionally testing unreleased development changes.

## How Arkheionx Uses Slither

Slither evidence can:

- add a `slither` detection source;
- improve affected file/function reporting;
- improve SARIF locations;
- support a confidence reason;
- enrich issue-plan evidence.

Slither output does not turn Arkheionx findings into confirmed
vulnerabilities. The result remains a defensive pre-audit readiness signal.

## Troubleshooting

- If Slither is missing, omit `--slither` or install it in your workflow.
- If Slither output is too noisy, provide a curated JSON file with
  `--slither-json`.
- If you need hard CI failure when Slither is unavailable, use
  `--slither-strict`; the default is graceful continuation.
