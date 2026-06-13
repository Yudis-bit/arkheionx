"""Tests for the hunter source-recovery engine."""
import unittest
from pathlib import Path

from arkheionx.hunter import models as M
from arkheionx.hunter.pack import build_hunter_pack

REPO_ROOT = Path(__file__).resolve().parents[1]
FX = REPO_ROOT / "tests" / "fixtures" / "hunter"


def exact_fetcher(address, chain_id, name):
    return {
        "origin": "sourcify_exact", "match_type": "exact_match", "compiler_version": "0.8.20",
        "file_count": 3, "metadata_hash": "0xabc123", "source_path": "sourcify://" + address,
    }


def abi_fetcher(address, chain_id, name):
    return {"origin": "abi", "match_type": "abi_only", "file_count": 0}


class SourceRecoveryTests(unittest.TestCase):
    def test_local_source(self) -> None:
        b = FX / "fresh_state_machine_value_flow"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"), write=False)
        self.assertEqual(res["pack"].source_provenance.overall_status, M.SOURCE_LOCAL)

    def test_source_missing_without_fetcher(self) -> None:
        b = FX / "source_recovery_mock"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                addresses_file=str(b / "addresses.json"), write=False)
        self.assertEqual(res["pack"].source_provenance.overall_status, M.SOURCE_MISSING)

    def test_source_missing_caps_source_level_lead(self) -> None:
        b = FX / "source_recovery_mock"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                addresses_file=str(b / "addresses.json"), write=False)
        gaps = [l for l in res["pack"].leads if l.lead_type == M.SOURCE_RECOVERY_GAP]
        self.assertTrue(gaps, "expected a SOURCE_RECOVERY_GAP lead when source is missing")
        for lead in gaps:
            self.assertEqual(lead.decision, M.PARK_SOURCE, lead.lead_id)

    def test_exact_match_improves_source_confidence(self) -> None:
        b = FX / "source_recovery_mock"
        missing = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                    addresses_file=str(b / "addresses.json"), write=False)
        exact = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                  addresses_file=str(b / "addresses.json"),
                                  source_fetcher=exact_fetcher, write=False)
        self.assertEqual(missing["pack"].source_provenance.overall_status, M.SOURCE_MISSING)
        self.assertEqual(exact["pack"].source_provenance.overall_status, M.SOURCE_SOURCIFY_EXACT)
        self.assertTrue(exact["pack"].source_provenance.network_recovery_attempted)

    def test_abi_only_is_inadequate(self) -> None:
        b = FX / "source_recovery_mock"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                addresses_file=str(b / "addresses.json"),
                                source_fetcher=abi_fetcher, write=False)
        self.assertEqual(res["pack"].source_provenance.overall_status, M.SOURCE_ABI_ONLY)

    def test_no_source_recovery_mode_skips_network(self) -> None:
        b = FX / "source_recovery_mock"
        res = build_hunter_pack(b, scope_file=str(b / "scope.md"),
                                addresses_file=str(b / "addresses.json"),
                                source_recovery_mode="none", source_fetcher=exact_fetcher, write=False)
        self.assertEqual(res["pack"].source_provenance.overall_status, M.SOURCE_MISSING)
        self.assertFalse(res["pack"].source_provenance.network_recovery_attempted)


if __name__ == "__main__":
    unittest.main()
