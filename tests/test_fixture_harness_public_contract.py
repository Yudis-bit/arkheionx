"""Public-contract QA for the fixture harness (v3.9): no CLI/schema/metadata change."""
from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path

import arkheionx.fixture_harness as fh
from arkheionx.cli.main import build_parser

REPO_ROOT = Path(__file__).resolve().parents[1]


def _cli_commands() -> list[str]:
    parser = build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return sorted(action.choices.keys())
    return []


class CliContractTests(unittest.TestCase):
    def test_fixture_harness_adds_no_cli_command(self) -> None:
        commands = _cli_commands()
        self.assertTrue(commands)  # the CLI still has commands
        for command in commands:
            self.assertNotIn("fixture", command.lower(), command)

    def test_fixture_harness_not_wired_into_cli_module(self) -> None:
        cli_main = Path(REPO_ROOT / "arkheionx" / "cli" / "main.py").read_text(encoding="utf-8")
        self.assertNotIn("fixture_harness", cli_main)

    def test_fixture_harness_not_imported_by_cli_commands(self) -> None:
        commands_src = Path(REPO_ROOT / "arkheionx" / "cli" / "commands.py").read_text(encoding="utf-8")
        self.assertNotIn("fixture_harness", commands_src)


class ExportContractTests(unittest.TestCase):
    def test_all_exports_importable(self) -> None:
        self.assertTrue(fh.__all__)
        for name in fh.__all__:
            self.assertTrue(hasattr(fh, name), name)

    def test_all_exports_unique(self) -> None:
        self.assertEqual(len(fh.__all__), len(set(fh.__all__)))

    def test_core_public_names_present(self) -> None:
        for name in (
            "ProtocolFixture", "FixtureArtifactRef", "FixtureRun", "FixtureResult",
            "FixtureSuite", "FixtureSafetyBoundary", "fixture_harness_to_dict",
            "build_set1_fixture_suite", "build_set2_fixture_suite",
            "build_set3_fixture_suite", "build_all_fixture_suite",
            "build_fixture_source_fingerprints",
            "run_fixture_benchmark", "run_fixture_benchmark_suite",
            "benchmark_set1_fixture_suite", "benchmark_all_fixture_suite",
            "build_set1_benchmark_snapshot", "build_all_benchmark_snapshot",
            "compare_set1_benchmark_snapshot", "compare_all_benchmark_snapshot",
            "build_set1_fixture_crossref", "build_all_fixture_crossref",
        ):
            self.assertIn(name, fh.__all__, name)


class LightweightPublicApiTests(unittest.TestCase):
    def test_all_fixture_benchmark_snapshot_and_safety_flags(self) -> None:
        suite = fh.benchmark_all_fixture_suite()
        comparison = fh.compare_all_benchmark_snapshot()
        blob = json.dumps(fh.fixture_harness_to_dict(suite), sort_keys=True)

        self.assertEqual(suite.fixture_count, 9)
        self.assertEqual(suite.drift_count, 0)
        self.assertIs(comparison["matches"], True)
        self.assertEqual(comparison["drift_count"], 0)
        self.assertIs(suite.manual_review_required, True)
        self.assertIs(suite.ready_for_submission, False)
        self.assertIs(comparison["manual_review_required"], True)
        self.assertIs(comparison["ready_for_submission"], False)
        self.assertNotIn("HUMAN_REVIEWED", blob)
        for token in ("confirmed vulnerability", "final severity", "audit passed",
                      "bounty eligible", "proves safety", "proves a vulnerability"):
            self.assertNotIn(token, blob.lower(), token)


class SchemaAndMetadataContractTests(unittest.TestCase):
    def test_no_fixture_schema_added(self) -> None:
        schemas_dir = REPO_ROOT / "schemas"
        if schemas_dir.is_dir():
            fixture_schemas = [p.name for p in schemas_dir.glob("*fixture*")]
            self.assertEqual(fixture_schemas, [], fixture_schemas)

    def test_version_metadata_unchanged(self) -> None:
        from arkheionx.version import CURRENT_MILESTONE, NEXT_MILESTONE, STABLE_RELEASE, __version__
        self.assertEqual(__version__, "7.0.0")
        self.assertEqual(STABLE_RELEASE, "v7.0.0")
        self.assertEqual(CURRENT_MILESTONE, "v7.0.0")
        self.assertEqual(NEXT_MILESTONE, "v7.1.0")

    def test_fixture_harness_is_internal_only(self) -> None:
        # The harness package exposes no `main`/`cli`/`build_parser` entry point.
        for name in ("main", "cli", "build_parser", "app"):
            self.assertNotIn(name, fh.__all__, name)


if __name__ == "__main__":
    unittest.main()
