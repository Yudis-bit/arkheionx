#!/usr/bin/env python3
"""Validate Arkheionx local/static JSON config files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arkheionx.config.loader import load_and_validate_config  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an Arkheionx config file.")
    parser.add_argument("--config", default=".arkheionx.json", help="Config path to validate.")
    parser.add_argument("--json", action="store_true", help="Write machine-readable validation output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config).expanduser() if args.config else None
    result = load_and_validate_config(config_path, REPO_ROOT)
    payload = {
        "valid": result.valid,
        "source": result.source,
        "errors": result.errors,
        "warnings": result.warnings,
        "normalized_config": result.normalized_config,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        label = result.source or str(config_path or ".arkheionx.json")
        if result.valid:
            print(f"ok: Arkheionx config valid: {label}")
        else:
            print(f"error: Arkheionx config invalid: {label}", file=sys.stderr)
        for warning in result.warnings:
            print(f"warning: {warning}")
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
