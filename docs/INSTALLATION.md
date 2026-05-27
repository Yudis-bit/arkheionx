# Installation

Arkheionx v2.0.0 prepares local editable installation for development and
authorized repository review.

```sh
python3 -m pip install -e .
arkheionx doctor
arkheionx scan .
```

This repository does not publish a PyPI package in v2.0.0. Install from the
source checkout you are working in.

If your system Python blocks editable installs because it is externally
managed, create a virtual environment first:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

## Requirements

- Python 3.11 or newer.
- No runtime Python dependencies.
- No RPC endpoint, private key, mnemonic, GitHub token, or hosted service.

## Local Workflow

```sh
arkheionx version
arkheionx validate-config --config examples/arkheionx.config.example.json
arkheionx search "oracle stale price"
```

Existing scripts still work:

```sh
python3 scripts/pre_audit_scan.py --root . --protocol-type auto
python3 scripts/generate_test_plan.py --check
```

## Safety

The installed CLI is local/static only. It does not perform live-chain calls,
transaction execution, deployed-contract scanning, remote cloning, or exploit
automation.
