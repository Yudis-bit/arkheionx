"""Tests for the v2.7.0 guided demo workflow.

Local-only: no network, no RPC, no private keys. Foundry is not required.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"

# demo id -> (recommended target, category)
DEMOS = {
    "oracle-staking": ("OracleRewardFixture.stake", "staking"),
    "amm-swap": ("AMMSwapFixture.swapAForB", "amm"),
    "lending-vault": ("LendingVaultFixture.borrow", "lending"),
}


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "-m", "arkheionx.cli.main", *args],
        cwd=REPO_ROOT, text=True, capture_output=True,
    )


class DemoCommandTests(unittest.TestCase):
    def test_demo_in_help(self) -> None:
        result = run_cli("--help")
        self.assertIn("demo", result.stdout)

    def test_list(self) -> None:
        result = run_cli("demo", "--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARKHEIONX DEMOS", result.stdout)
        for demo_id, (_target, category) in DEMOS.items():
            self.assertIn(demo_id, result.stdout)
            self.assertIn(f"[{category}]", result.stdout)

    def test_list_json(self) -> None:
        import json

        result = run_cli("demo", "--list", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        ids = {d["id"] for d in payload}
        for demo_id in DEMOS:
            self.assertIn(demo_id, ids)
        # metadata present
        for d in payload:
            self.assertIn("category", d)
            self.assertIn("risk_theme", d)

    def test_show(self) -> None:
        for demo_id, (target, category) in DEMOS.items():
            result = run_cli("demo", "--show", demo_id)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(target, result.stdout)
            self.assertIn(f"Category: {category}", result.stdout)
            self.assertIn("Risk theme:", result.stdout)
            self.assertIn("Safety:", result.stdout)
            self.assertIn("no RPC", result.stdout)

    def test_commands(self) -> None:
        for demo_id, (target, _category) in DEMOS.items():
            result = run_cli("demo", "--commands", demo_id)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Heuristic workflow", result.stdout)
            self.assertIn("Foundry-backed workflow", result.stdout)
            self.assertIn(f"--target {target} --run", result.stdout)

    def test_unknown_id_fails_with_options(self) -> None:
        result = run_cli("demo", "--show", "does-not-exist")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown demo", result.stderr)
        self.assertIn("oracle-staking", result.stderr)

    def test_copy_copies_source_only(self) -> None:
        for demo_id in DEMOS:
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "arkheionx-demo"
                result = run_cli("demo", "--copy", demo_id, str(dest))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((dest / "README.md").exists(), demo_id)
                self.assertTrue((dest / "foundry.toml").exists(), demo_id)
                self.assertTrue(list((dest / "src").glob("*.sol")), demo_id)
                self.assertTrue(list((dest / "test").glob("*.sol")), demo_id)
                # Generated build artifacts must NOT be copied.
                self.assertFalse((dest / "out").exists(), demo_id)
                self.assertFalse((dest / "cache").exists(), demo_id)

    def test_copy_refuses_non_empty_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "arkheionx-demo"
            dest.mkdir()
            (dest / "keep.txt").write_text("x", encoding="utf-8")
            result = run_cli("demo", "--copy", "oracle-staking", str(dest))
            self.assertEqual(result.returncode, 2)
            self.assertIn("not empty", result.stderr)
            self.assertTrue((dest / "keep.txt").exists())

    def test_copy_force_into_non_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "arkheionx-demo"
            dest.mkdir()
            (dest / "keep.txt").write_text("x", encoding="utf-8")
            result = run_cli("demo", "--copy", "oracle-staking", str(dest), "--force")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest / "src" / "OracleRewardFixture.sol").exists())

    def test_copy_does_not_write_outside_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            dest = parent / "nested" / "arkheionx-demo"
            result = run_cli("demo", "--copy", "oracle-staking", str(dest))
            self.assertEqual(result.returncode, 0, result.stderr)
            # Only the destination tree should exist under parent/nested.
            self.assertEqual([p.name for p in (parent / "nested").iterdir()], ["arkheionx-demo"])

    def test_copied_demo_opens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "arkheionx-demo"
            run_cli("demo", "--copy", "oracle-staking", str(dest))
            result = run_cli("open", str(dest), "--no-artifacts")
            # 0 (compiler/exec) or 1 (heuristic) are both acceptable; must not crash (2).
            self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
            self.assertIn("ARKHEIONX OPEN", result.stdout)


class DemoFixtureSafetyTests(unittest.TestCase):
    def test_fixture_and_readme_exist(self) -> None:
        self.assertTrue(FIXTURE.is_dir())
        self.assertTrue((FIXTURE / "README.md").exists())
        self.assertTrue((FIXTURE / "src" / "OracleRewardFixture.sol").exists())

    def test_fixture_has_no_secrets_or_rpc(self) -> None:
        banned = [
            "rpc", "mnemonic", "private key", "privatekey", "private_key",
            "http://", "https://", "createselectfork", "fork-url", "secret",
        ]
        for path in FIXTURE.rglob("*"):
            if not path.is_file() or path.suffix not in {".sol", ".toml", ".md"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for phrase in banned:
                self.assertNotIn(phrase, text, f"{path.name} contains '{phrase}'")

    def test_only_source_entries_tracked(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files", "examples/oracle-staking-fixture"],
            cwd=REPO_ROOT, text=True, capture_output=True,
        ).stdout.split()
        for entry in tracked:
            self.assertFalse(
                entry.startswith("examples/oracle-staking-fixture/out/")
                or entry.startswith("examples/oracle-staking-fixture/cache/"),
                f"generated artifact tracked: {entry}",
            )


class DemoDocsAndMetadataTests(unittest.TestCase):
    def test_demo_workflow_doc_exists(self) -> None:
        doc = (REPO_ROOT / "docs" / "DEMO_WORKFLOW.md")
        self.assertTrue(doc.exists())
        text = doc.read_text(encoding="utf-8")
        for demo_id in DEMOS:
            self.assertIn(demo_id, text)

    def test_readme_concise_and_mentions_demo(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(len(readme.splitlines()), 650)  # v3 launch README bound (300-650)
        self.assertIn("arkheionx demo", readme)
        self.assertIn("docs/DEMO_WORKFLOW.md", readme)

    def test_changelog_and_release_notes(self) -> None:
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## v2.7.0", changelog)
        self.assertNotIn("## v2.7.0 - Unreleased", changelog)
        self.assertTrue((REPO_ROOT / "release-notes" / "v2.7.0.md").exists())

    def test_version_metadata(self) -> None:
        from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, STABLE_RELEASE, __version__

        self.assertEqual(__version__, "5.0.0")
        self.assertEqual(STABLE_RELEASE, "v3.1.0")
        self.assertEqual(CURRENT_MILESTONE, "v5.0.0")
        self.assertEqual(NEXT_MILESTONE, "v5.1.0")


if __name__ == "__main__":
    unittest.main()
