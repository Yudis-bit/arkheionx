import unittest
from pathlib import Path


class PackageDataTests(unittest.TestCase):
    def test_runtime_data_paths_resolve_from_source_tree(self) -> None:
        from arkheionx.core.paths import (
            is_editable_source_tree,
            package_root,
            project_root,
            resolve_runtime_data_path,
        )

        root = project_root()
        self.assertTrue((root / "pyproject.toml").exists())
        self.assertTrue(package_root().name == "arkheionx")
        self.assertTrue(is_editable_source_tree(root))
        for parts in [
            ("metadata", "search_terms.json"),
            ("schemas", "pre-audit-report.schema.json"),
            ("templates", "invariant_skeletons", "amm_invariants.sol"),
        ]:
            path = resolve_runtime_data_path(*parts, root=root)
            self.assertTrue(path.exists(), str(path))

    def test_runtime_data_helpers_return_paths(self) -> None:
        from arkheionx.core.paths import resolve_input_path, resolve_output_path

        metadata = resolve_input_path("metadata/search_terms.json")
        self.assertTrue(metadata.exists(), str(metadata))
        output = resolve_output_path("reports/example.json", root=Path("/tmp"))
        self.assertEqual(output, Path("/tmp/reports/example.json"))


if __name__ == "__main__":
    unittest.main()

