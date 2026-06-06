# Contributing

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
arkheionx doctor
```

## Running Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Running Validation

```bash
python3 scripts/check_docs_links.py --check
python3 scripts/check_safety_wording.py --strict
python3 scripts/check_version_consistency.py --check
python3 scripts/check_release_readiness.py --check
make validate
```

## Determinism Rules

- Keep fixture outputs deterministic.
- Update benchmark snapshots only when source or expected behavior changes.
- Keep source fingerprints stable and reviewable.
- Avoid network-dependent validation in default tests.

## Safety Wording Rules

- Do not claim automatic vulnerability confirmation.
- Do not claim an audit result or safety proof.
- Do not claim final severity.
- Do not claim bounty outcomes.
- Keep human review requirements explicit.

## No Secrets

Do not commit private keys, seed phrases, RPC credentials, passwords, bearer
tokens, wallet material, or recovery phrases. Local review fixtures must not
require secrets.

## RPC, Live-Chain, and Exploit-Automation Rules

ArkheionX defaults to local/static review. New RPC, live-chain, transaction,
or exploit-automation behavior must not be added without an explicit reviewed
design, narrow scope, and safety tests.

## Pull Request Checklist

- Tests pass.
- Documentation links pass.
- Strict safety wording passes.
- Version consistency passes.
- Release readiness passes.
- No secrets or private material are introduced.
- Public docs remain accurate, technical, and human-review oriented.
