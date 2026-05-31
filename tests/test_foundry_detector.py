import tempfile
import unittest
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.protocol import foundry as foundry_mod

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"


class FoundryDetectorTests(unittest.TestCase):
    def test_unavailable_without_foundry_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = foundry_mod.detect_foundry(Path(tmp))
            self.assertEqual(status.status, foundry_mod.UNAVAILABLE)
            self.assertFalse(status.has_foundry_toml)

    def test_detect_on_fixture_does_not_raise(self) -> None:
        status = foundry_mod.detect_foundry(FIXTURE)
        self.assertIn(status.status, {foundry_mod.UNAVAILABLE, foundry_mod.AVAILABLE_NOT_BUILT})
        self.assertTrue(status.has_foundry_toml)  # fixture ships a foundry.toml

    def test_build_and_confirm_falls_back_without_forge(self) -> None:
        # build_and_confirm must never raise and must return a status + string.
        with tempfile.TemporaryDirectory() as tmp:
            status, output = foundry_mod.build_and_confirm(Path(tmp))
            self.assertEqual(status.status, foundry_mod.UNAVAILABLE)
            self.assertEqual(output, "")

    def test_collect_compiled_contracts_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(foundry_mod.collect_compiled_contracts(Path(tmp)), [])


class ArtifactWriterTests(unittest.TestCase):
    def test_writes_under_arkheionx_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            path = writer.write_text("map.json", "{}")
            self.assertTrue(path.exists())
            self.assertEqual(path.parent, Path(tmp) / ".arkheionx" / "out")
            self.assertTrue(path.read_text(encoding="utf-8").endswith("\n"))

    def test_nested_paths_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            writer = ArtifactWriter(Path(tmp))
            path = writer.write_text("proof/Vault_withdraw/proof.json", "{}")
            self.assertTrue(path.exists())
            self.assertIn("proof/Vault_withdraw", path.as_posix())


if __name__ == "__main__":
    unittest.main()
