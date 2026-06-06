# Arkheionx Generated Issue Checklist

Generated from: pre-audit readiness scan
Protocol type: `vault`
Score: `73/100`

## Existing Findings From Baseline

- [ ] ARK-VLT-001 - Add Foundry invariants for share/accounting conservation across deposit, withdraw, donation, fee, and emergency scenarios.
- [ ] ARK-VLT-007 - Add deposit, withdrawal, management, and performance fee tests where relevant.
- [ ] ARK-ACC-003 - Document who can change critical configuration and whether controls use a multisig, timelock, guardian, or single owner.
- [ ] ARK-REENT-001 - Review state ordering and add local reentrant receiver tests around every value-flow path.
- [ ] ARK-REENT-004 - Document state-update ordering, callback assumptions, and why any unguarded external calls are safe by design.

## Documentation Tasks

- [ ] Document admin role boundaries.
- [ ] Document oracle and pricing assumptions.
- [ ] Document known limitations and formal audit scope.

## Convert This Checklist Into GitHub Issues

No issue plan path was provided for this run.

## Notes

This checklist is generated from static/local readiness signals. It is not a formal audit.
