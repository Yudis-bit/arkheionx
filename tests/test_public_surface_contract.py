"""Public command surface contract + common error-message tests.

Guards docs/PUBLIC_SURFACE.md (and the stability/readiness docs) against drift
from the actual argparse command surface, and checks that common CLI errors are
clean and actionable.
"""
import argparse
import os
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def public_commands() -> list[str]:
    from arkheionx.cli.main import build_parser

    parser = build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return list(action.choices.keys())
    return []


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8", errors="ignore")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env=env,
    )


class PublicSurfaceContractTests(unittest.TestCase):
    def test_readiness_docs_exist(self) -> None:
        for doc in ("docs/PUBLIC_SURFACE.md", "docs/STABILITY_CONTRACT.md", "docs/V3_READINESS.md"):
            self.assertTrue((REPO_ROOT / doc).is_file(), doc)

    def test_every_command_is_documented(self) -> None:
        surface = read("docs/PUBLIC_SURFACE.md")
        commands = public_commands()
        self.assertIn("hunt", commands)  # sanity: parser introspection worked
        for command in commands:
            self.assertIn(f"`arkheionx {command}`", surface, f"undocumented command: {command}")

    def test_scripts_are_documented(self) -> None:
        surface = read("docs/PUBLIC_SURFACE.md")
        for script in ("install.sh", "uninstall.sh", "arkup"):
            self.assertIn(f"`{script}`", surface, f"undocumented script: {script}")

    def test_readme_links_readiness_docs(self) -> None:
        readme = read("README.md")
        for doc in ("docs/PUBLIC_SURFACE.md", "docs/STABILITY_CONTRACT.md", "docs/V3_READINESS.md"):
            self.assertIn(f"]({doc})", readme, doc)

    def test_cli_reference_links_public_surface(self) -> None:
        self.assertIn("PUBLIC_SURFACE.md", read("docs/CLI_REFERENCE.md"))

    def test_local_validate_is_public_and_documented(self) -> None:
        self.assertIn("local-validate", public_commands())
        self.assertIn("`arkheionx local-validate`", read("docs/PUBLIC_SURFACE.md"))
        self.assertIn("local-validate", read("docs/CLI_REFERENCE.md"))


class ErrorMessageTests(unittest.TestCase):
    def test_unknown_demo_lists_available(self) -> None:
        result = run_cli("demo", "--show", "does-not-exist")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown demo", result.stderr)
        self.assertIn("Available demos:", result.stderr)
        for demo in ("oracle-staking", "amm-swap", "lending-vault"):
            self.assertIn(demo, result.stderr)
        self.assertIn("arkheionx demo --list", result.stderr)

    def test_missing_target_points_to_hunt(self) -> None:
        result = run_cli("prove", "examples/oracle-staking-fixture")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--target", result.stdout + result.stderr)
        self.assertIn("hunt", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
