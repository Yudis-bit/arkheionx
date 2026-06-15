import tempfile
import unittest
from pathlib import Path

from arkheionx.ingest import discover_solidity


class DependencyExclusionTest(unittest.TestCase):
    def test_dependency_directories_are_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "contracts").mkdir()
            (root / "node_modules" / "dependency").mkdir(parents=True)
            (root / "vendor").mkdir()
            (root / "contracts" / "Main.sol").write_text("contract Main {}", encoding="utf-8")
            (root / "node_modules" / "dependency" / "Dependency.sol").write_text(
                "contract Dependency {}", encoding="utf-8"
            )
            (root / "vendor" / "Vendored.sol").write_text("contract Vendored {}", encoding="utf-8")
            result = discover_solidity(root)
            self.assertEqual([source.rel for source in result.sources], ["contracts/Main.sol"])
            self.assertEqual(result.excluded_dependency_files, 1)
            self.assertEqual(result.excluded_generated_files, 1)


if __name__ == "__main__":
    unittest.main()
