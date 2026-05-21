#!/usr/bin/env python3
"""poc_factory — assist porting upstream PoCs into Arkheionx Vault.

Safe-by-default. Does NOT auto-commit, does NOT auto-push, does NOT modify
the working tree unless --apply is passed.

Default workflow:

  1.  python scripts/poc_factory.py --report
      Lists candidate PoCs from .reference_data/ that are not yet present
      under EVM/test/. Read-only.

  2.  python scripts/poc_factory.py --target <YYYY-MM-Protocol> --dry-run
      Shows the file plan for a single candidate. No writes.

  3.  python scripts/poc_factory.py --target <YYYY-MM-Protocol> --apply
      Writes the adapted PoC to EVM/test/<target>/. Still does not commit.
      Human review and `forge test` are required before committing.

Provenance: when --apply is used, the upstream commit SHA from
.reference_data/ is recorded in the PoC file header so the original author
is preserved.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_DIR = REPO_ROOT / ".reference_data"
EVM_DIR = REPO_ROOT / "EVM"
TEST_DIR = EVM_DIR / "test"
DEFAULT_SOURCE = "https://github.com/SunWeb3Sec/DeFiHackLabs.git"


@dataclass
class Candidate:
    folder: Path
    name: str  # e.g. "2023-03-EulerFinance"
    date: str  # "YYYY-MM"
    protocol: str


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def upstream_sha(ref_dir: Path) -> str | None:
    if not (ref_dir / ".git").exists():
        return None
    r = run(["git", "rev-parse", "HEAD"], cwd=ref_dir)
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def parse_folder(name: str) -> tuple[str, str] | None:
    m = re.match(r"^(\d{4}-\d{2})-(.+)$", name)
    if not m:
        return None
    return m.group(1), m.group(2)


def discover_candidates(ref_dir: Path) -> list[Candidate]:
    src_test = ref_dir / "src" / "test"
    if not src_test.exists():
        return []
    out: list[Candidate] = []
    for child in sorted(src_test.iterdir()):
        if not child.is_dir():
            continue
        parsed = parse_folder(child.name)
        if parsed is None:
            continue
        date, protocol = parsed
        out.append(Candidate(folder=child, name=child.name, date=date, protocol=protocol))
    return out


def existing_targets() -> set[str]:
    if not TEST_DIR.exists():
        return set()
    return {p.name for p in TEST_DIR.iterdir() if p.is_dir()}


def chain_hint(folder: Path) -> str:
    """Light heuristic: scan .sol files for chain mentions. Used for reporting,
    not for any automated decision. Human reviewer makes the call.
    """
    keywords = {
        "bsc": "bsc",
        "polygon": "polygon",
        "avax": "avalanche",
        "avalanche": "avalanche",
        "arbitrum": "arbitrum",
        "optimism": "optimism",
        "base": "base",
    }
    seen: set[str] = set()
    for p in folder.glob("*.sol"):
        text = p.read_text(errors="ignore").lower()
        for k, v in keywords.items():
            if k in text:
                seen.add(v)
    if not seen:
        return "ethereum?"
    return "+".join(sorted(seen))


def transform_sol(content: str, target_name: str, sha: str | None) -> str:
    parsed = parse_folder(target_name)
    if parsed is None:
        return content
    date, protocol = parsed
    pascal = "".join(part.capitalize() for part in re.split(r"[-_]", protocol))
    contract_name = f"Exploit_{date.replace('-', '_')}_{pascal}"

    content = re.sub(
        r"pragma\s+solidity\s+[\^~>=<0-9. ]+;",
        "pragma solidity >=0.8.0 <0.9.0;",
        content,
        count=1,
    )
    content = re.sub(
        r"(contract\s+)\w+(\s+is\s+(Test|BaseTest|BaseTestWithBalanceLog)\b)",
        rf"\1{contract_name}\2",
        content,
        count=1,
    )

    def fix_import(m: re.Match) -> str:
        path = m.group(1)
        if path.startswith("../") or path.startswith("./"):
            return f'import "src/{path.rsplit("/", 1)[-1]}";'
        return m.group(0)

    content = re.sub(r'import\s+"([^"]+\.sol)";', fix_import, content)

    provenance_lines = [
        "// Imported into Arkheionx Vault. Adapted for forge-std + pinned fork.",
        f"// Upstream source: {DEFAULT_SOURCE}",
    ]
    if sha:
        provenance_lines.append(f"// Upstream commit: {sha}")
    provenance = "\n".join(provenance_lines) + "\n\n"

    parts = content.splitlines(keepends=True)
    insert_at = 0
    for i, line in enumerate(parts[:5]):
        if line.startswith("pragma "):
            insert_at = i + 1
            break
    return "".join(parts[:insert_at]) + provenance + "".join(parts[insert_at:])


def plan_for(cand: Candidate) -> dict:
    sol_files = sorted(cand.folder.glob("*.sol"))
    target_dir = TEST_DIR / cand.name
    return {
        "candidate": cand.name,
        "chain_hint": chain_hint(cand.folder),
        "sol_files": [p.name for p in sol_files],
        "target_dir": str(target_dir.relative_to(REPO_ROOT)),
        "would_write": [
            f"{target_dir.relative_to(REPO_ROOT)}/Exploit_{cand.name}.t.sol"
        ] if sol_files else [],
    }


def apply_one(cand: Candidate) -> list[Path]:
    target_dir = TEST_DIR / cand.name
    target_dir.mkdir(parents=True, exist_ok=True)
    sha = upstream_sha(REFERENCE_DIR)
    written: list[Path] = []
    for sol in sorted(cand.folder.glob("*.sol")):
        content = sol.read_text()
        content = transform_sol(content, cand.name, sha)
        out_path = target_dir / f"Exploit_{cand.name}.t.sol"
        out_path.write_text(content)
        written.append(out_path)
        break  # one PoC file per candidate
    writeup = cand.folder / "WRITEUP.md"
    if writeup.exists():
        shutil.copy(writeup, target_dir / "WRITEUP.md")
        written.append(target_dir / "WRITEUP.md")
    return written


def cmd_report(args: argparse.Namespace) -> int:
    candidates = discover_candidates(REFERENCE_DIR)
    existing = existing_targets()
    new = [c for c in candidates if c.name not in existing]
    print(f"Reference directory: {REFERENCE_DIR.relative_to(REPO_ROOT)}")
    sha = upstream_sha(REFERENCE_DIR)
    print(f"Upstream commit:     {sha or '(not a git checkout)'}")
    print(f"Candidates total:    {len(candidates)}")
    print(f"Already imported:    {len(candidates) - len(new)}")
    print(f"Not yet imported:    {len(new)}")
    for c in new[:50]:
        print(f"  - {c.name} (chain hint: {chain_hint(c.folder)})")
    if len(new) > 50:
        print(f"  ... and {len(new) - 50} more")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    if not args.target:
        print("error: --target <YYYY-MM-Protocol> required for --dry-run", file=sys.stderr)
        return 2
    cand_path = REFERENCE_DIR / "src" / "test" / args.target
    if not cand_path.is_dir():
        print(f"error: candidate folder not found: {cand_path}", file=sys.stderr)
        return 1
    parsed = parse_folder(args.target)
    if parsed is None:
        print(f"error: target name does not match YYYY-MM-Protocol: {args.target}", file=sys.stderr)
        return 1
    date, protocol = parsed
    cand = Candidate(folder=cand_path, name=args.target, date=date, protocol=protocol)
    plan = plan_for(cand)
    print(f"Plan for {cand.name}:")
    for k, v in plan.items():
        print(f"  {k}: {v}")
    print("\nNo files written. Re-run with --apply to perform the import.")
    print("After --apply: review the diff, run forge test, add a metadata entry,")
    print("then commit. The factory does NOT commit or push.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    if not args.target:
        print("error: --target <YYYY-MM-Protocol> required for --apply", file=sys.stderr)
        return 2
    cand_path = REFERENCE_DIR / "src" / "test" / args.target
    if not cand_path.is_dir():
        print(f"error: candidate folder not found: {cand_path}", file=sys.stderr)
        return 1
    parsed = parse_folder(args.target)
    if parsed is None:
        return 1
    date, protocol = parsed
    cand = Candidate(folder=cand_path, name=args.target, date=date, protocol=protocol)
    written = apply_one(cand)
    if not written:
        print("error: no .sol files were written; nothing matched", file=sys.stderr)
        return 1
    print(f"Wrote {len(written)} file(s):")
    for p in written:
        print(f"  - {p.relative_to(REPO_ROOT)}")
    print("\nNext steps (manual):")
    print("  1. Review the imported file. Do not assume it builds.")
    print("  2. Run `forge build` and `forge test --match-path ...` from EVM/.")
    print("  3. Add a metadata entry in metadata/registry.json (see docs/METADATA_SCHEMA.md).")
    print("  4. Run `python scripts/validate_metadata.py` and `generate_registry.py`.")
    print("  5. Commit by hand. The factory does NOT commit or push.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Assist porting upstream PoCs into Arkheionx Vault. Safe by default.",
    )
    ap.add_argument("--report", action="store_true", help="List importable candidates. Read-only.")
    ap.add_argument("--dry-run", action="store_true", help="Show file plan for --target. No writes.")
    ap.add_argument("--apply", action="store_true", help="Write the imported PoC. Does NOT commit or push.")
    ap.add_argument("--target", help="Candidate folder name, e.g. 2023-03-EulerFinance.")
    args = ap.parse_args(argv)

    chosen = sum(bool(x) for x in (args.report, args.dry_run, args.apply))
    if chosen != 1:
        ap.error("exactly one of --report, --dry-run, --apply is required")

    if not REFERENCE_DIR.exists():
        print(f"error: reference directory missing: {REFERENCE_DIR}", file=sys.stderr)
        print(
            f"hint:  clone the upstream repository there manually, e.g.\n"
            f"       git clone {DEFAULT_SOURCE} {REFERENCE_DIR}",
            file=sys.stderr,
        )
        return 1

    if args.report:
        return cmd_report(args)
    if args.dry_run:
        return cmd_plan(args)
    return cmd_apply(args)


if __name__ == "__main__":
    sys.exit(main())

