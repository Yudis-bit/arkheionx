"""Tests for the v7.5 protocol-lens registry."""
import os
import subprocess
import unittest
from pathlib import Path

import arkheionx.protocol_lens as pl
from arkheionx.protocol_lens.base import ProtocolLens

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str):
    env = dict(os.environ)
    env["ARKHEIONX_COLOR"] = "never"
    return subprocess.run(["python3", "-m", "arkheionx.cli.main", *args],
                          cwd=REPO_ROOT, text=True, capture_output=True, env=env)


class ProtocolLensRegistryTests(unittest.TestCase):
    def test_registry_finds_fixed_credit_market(self) -> None:
        self.assertTrue(pl.is_registered("fixed-credit-market"))
        self.assertIn("fixed-credit-market", pl.lens_ids())
        lens = pl.get_lens("fixed-credit-market")
        self.assertIsInstance(lens, ProtocolLens)
        self.assertEqual(lens.lens_id, "fixed-credit-market")
        self.assertEqual(lens.display_name, "Fixed Credit Market Protocol Lens")

    def test_unknown_lens_raises_keyerror(self) -> None:
        with self.assertRaises(KeyError):
            pl.get_lens("does-not-exist")

    def test_available_lenses_and_planned(self) -> None:
        lenses = pl.available_lenses()
        self.assertTrue(any(l.lens_id == "fixed-credit-market" for l in lenses))
        planned_ids = {pid for pid, _ in pl.PLANNED_LENSES}
        # Planned lenses are advertised but must NOT be registered/implemented.
        for pid in planned_ids:
            self.assertFalse(pl.is_registered(pid), pid)
        for expected in ("generic-erc4626", "generic-lending", "generic-amm", "generic-staking"):
            self.assertIn(expected, planned_ids)

    def test_lens_list_cli_lists_fixed_credit_market(self) -> None:
        result = run_cli("lens-list")
        self.assertIn(result.returncode, (0, 1), result.stderr)
        self.assertIn("fixed-credit-market", result.stdout)
        self.assertIn("lens-list", run_cli("--help").stdout)


if __name__ == "__main__":
    unittest.main()
