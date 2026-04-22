#!/usr/bin/env python3
"""
Autonomous PoC Factory
Synchronizes exploits from SunWeb3Sec/DeFiHackLabs and integrates them into EVM/test/
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REFERENCE_REPO = "https://github.com/SunWeb3Sec/DeFiHackLabs.git"
REFERENCE_DIR = Path(".reference_data")
EVM_DIR = Path("EVM")
TEST_DIR = EVM_DIR / "test"


def run_cmd(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def sync_reference_data():
    """Clone or pull DeFiHackLabs repository."""
    if REFERENCE_DIR.exists():
        print(f"[+] Updating {REFERENCE_DIR}...")
        run_cmd(["git", "pull"], cwd=REFERENCE_DIR)
    else:
        print(f"[+] Cloning {REFERENCE_REPO}...")
        run_cmd(["git", "clone", REFERENCE_REPO, str(REFERENCE_DIR)])
    print("[✓] Reference data synchronized")


def extract_date_protocol(folder_name: str) -> tuple[str, str]:
    """Extract YYYY-MM and protocol name from folder name like 2023-03-EulerFinance."""
    match = re.match(r"(\d{4}-\d{2})-.+", folder_name)
    if match:
        date = match.group(1)
        protocol = folder_name.replace(f"{date}-", "")
        return date, protocol
    return "", folder_name


def find_new_pocs() -> list[Path]:
    """Scan reference_data/src/test/ for PoCs not yet in EVM/test/."""
    ref_test_dir = REFERENCE_DIR / "src" / "test"
    if not ref_test_dir.exists():
        ref_test_dir = REFERENCE_DIR / "src" / "test"
        if not ref_test_dir.exists():
            print("[!] Could not find test directory in reference data")
            return []

    existing = set()
    for item in TEST_DIR.iterdir():
        if item.is_dir():
            existing.add(item.name)

    new_pocs = []
    for item in sorted(ref_test_dir.iterdir()):
        if item.is_dir() and item.name not in existing:
            new_pocs.append(item)

    return new_pocs


def normalize_contract_name(content: str, new_folder: str) -> str:
    """Replace main contract name with Exploit_YYYY_MM_ProtocolName format."""
    date, protocol = extract_date_protocol(new_folder)
    protocol_camel = "".join(word.capitalize() for word in re.split(r"[-_]", protocol))
    new_name = f"Exploit_{date.replace('-', '')}_{protocol_camel}"

    content = re.sub(
        r"(contract\s+)(\w+)(\s+is\s+(Test|BaseTest|BaseTestWithBalanceLog)\b)",
        rf"\1{new_name}\3",
        content,
        count=1
    )

    return content


def patch_pragma_solidity(content: str) -> str:
    """Replace any pragma solidity version with >=0.8.0 <0.9.0."""
    pattern = r"pragma\s+solidity\s+[\^~>=<0-9.]+;"
    replacement = "pragma solidity >=0.8.0 <0.9.0;"
    return re.sub(pattern, replacement, content)


def copy_common_helpers():
    """Copy interface.sol, basetest.sol, and tokenhelper.sol from .reference_data to EVM/src/ if not already present."""
    src_dir = EVM_DIR / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    ref_test_dir = REFERENCE_DIR / "src" / "test"
    helpers = ["interface.sol", "basetest.sol", "tokenhelper.sol"]
    copied = []

    for helper in helpers:
        ref_path = ref_test_dir / helper
        dest_path = src_dir / helper

        if ref_path.exists():
            if not dest_path.exists():
                shutil.copy(ref_path, dest_path)
                copied.append(helper)
            else:
                print(f"[=] {helper} already exists in EVM/src/")

    basetest_path = src_dir / "basetest.sol"
    if basetest_path.exists():
        content = basetest_path.read_text()
        new_content = content.replace('import "./tokenhelper.sol";', 'import "src/tokenhelper.sol";')
        if new_content != content:
            basetest_path.write_text(new_content)
            print("[+] Fixed import in basetest.sol")

    return copied


def fix_import_paths(content: str) -> str:
    """Replace relative import paths like '../../interface.sol' with clean imports like 'src/interface.sol'."""
    import re

    def replace_import(match):
        full_path = match.group(1)
        if full_path.startswith("../") or full_path.startswith("./"):
            parts = full_path.rstrip("/").split("/")
            filename = parts[-1]
            return f'import "src/{filename}";'
        return match.group(0)

    pattern = r'import\s+"([^"]+\.sol)";'
    return re.sub(pattern, replace_import, content)


def update_foundry_remappings():
    """Add src/ and lib/ remappings to foundry.toml if not present."""
    toml_path = EVM_DIR / "foundry.toml"
    content = toml_path.read_text()

    if "remappings" in content:
        return False

    new_section = "\nremappings = ['@src/=src/', '@lib/=lib/']\n"
    content = content.rstrip() + new_section

    toml_path.write_text(content)
    return True


def adapt_poc(source_dir: Path, target_dir: Path):
    """Copy and adapt PoC to EVM/test/ format."""
    target_dir.mkdir(parents=True, exist_ok=True)

    copy_common_helpers()

    for sol_file in source_dir.glob("*.sol"):
        content = sol_file.read_text()
        content = patch_pragma_solidity(content)
        content = normalize_contract_name(content, target_dir.name)
        content = fix_import_paths(content)
        target_name = f"Exploit_{target_dir.name}.t.sol"
        (target_dir / target_name).write_text(content)

    helpers_to_remove = ["interface.sol", "basetest.sol", "tokenhelper.sol"]
    for helper in helpers_to_remove:
        helper_path = target_dir / helper
        if helper_path.exists():
            helper_path.unlink()
            print(f"[-] Removed duplicate: {helper}")

    for md_file in source_dir.glob("WRITEUP.md"):
        shutil.copy(md_file, target_dir / "WRITEUP.md")

    for other in source_dir.iterdir():
        if other.is_dir() or other.suffix in (".sol", ".md"):
            continue
        shutil.copy(other, target_dir / other.name)

    print(f"[+] Adapted: {target_dir.name}")


def check_chain_compatibility(source_dir: Path) -> bool:
    """Check if .t.sol contains BSC/Polygon/Avax strings - skip non-Ethereum."""
    for sol_file in source_dir.glob("*.sol"):
        content = sol_file.read_text().lower()
        if "bsc" in content or "polygon" in content or "avax" in content:
            print(f"[=] Skipping {source_dir.name} - non-Ethereum chain detected")
            return False
    return True


def run_tests(folder_name: str) -> tuple[bool, str]:
    """Run forge test -vvv on the new PoC and return (success, output)."""
    print(f"[+] Running forge test -vvv on {folder_name}...")
    result = run_cmd(["forge", "test", "-vvv", "--match-path", f"test/{folder_name}/*.t.sol"], cwd=EVM_DIR)
    output = result.stdout + result.stderr
    return result.returncode == 0, output


def auto_commit_push(folder_name: str, success: bool):
    """Git add, commit, and push only if tests pass."""
    status = run_cmd(["git", "status", "--porcelain"], cwd=EVM_DIR)
    if not status.stdout.strip():
        print("[=] No changes to commit")
        return

    if not success:
        print(f"[!] Test failed - skipping commit/push for {folder_name}")
        return

    run_cmd(["git", "add", "."], cwd=EVM_DIR)
    msg = f"feat: add {folder_name} PoC"
    run_cmd(["git", "commit", "-m", msg], cwd=EVM_DIR)

    print(f"[✓] Committed: {msg}")

    remote = run_cmd(["git", "remote", "get-url", "origin"], cwd=EVM_DIR)
    if remote.returncode == 0 and remote.stdout:
        run_cmd(["git", "push"], cwd=EVM_DIR)
        print("[✓] Pushed to remote")


def main():
    print("=== Autonomous PoC Factory ===\n")

    sync_reference_data()
    copy_common_helpers()
    update_foundry_remappings()

    new_pocs = find_new_pocs()
    if not new_pocs:
        print("[=] No new PoCs found")
        sys.exit(0)

    print(f"[+] Found {len(new_pocs)} new PoC(s):")
    for poc in new_pocs:
        print(f"  - {poc.name}")

    for poc_dir in new_pocs:
        target_dir = TEST_DIR / poc_dir.name

        if not check_chain_compatibility(poc_dir):
            continue

        adapt_poc(poc_dir, target_dir)

        success, output = run_tests(poc_dir.name)
        if not success:
            print(f"[!] Test failed for {poc_dir.name}")
            lines = output.strip().split("\n")
            error_lines = [l for l in lines if "error" in l.lower() or "fail" in l.lower() or "revert" in l.lower() or "assert" in l.lower()]
            if error_lines:
                print("\n--- Error output ---")
                for line in error_lines[:10]:
                    print(line)
                print("------------------\n")
            else:
                print("\n--- Last 10 lines of test output ---")
                for line in lines[-10:]:
                    print(line)
                print("--------------------------------------\n")
            continue

        auto_commit_push(poc_dir.name, success=True)

    print("\n[✓] PoC Factory complete")


if __name__ == "__main__":
    main()