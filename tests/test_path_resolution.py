import unittest
from pathlib import Path


class PathResolutionTests(unittest.TestCase):
    def test_project_root_and_relative_display(self) -> None:
        from arkheionx.core.paths import display_path, project_root, repo_relative

        root = project_root()
        readme = root / "README.md"
        self.assertEqual(repo_relative(readme, root), "README.md")
        self.assertEqual(display_path(readme, root), "README.md")

    def test_runtime_data_resolution_falls_back_to_source_root(self) -> None:
        from arkheionx.core.paths import project_root, resolve_runtime_data_path

        root = project_root()
        missing = resolve_runtime_data_path("metadata", "does-not-exist.json", root=root)
        self.assertEqual(missing, root / "metadata" / "does-not-exist.json")

    def test_absolute_paths_are_preserved(self) -> None:
        from arkheionx.core.paths import resolve_input_path, resolve_output_path

        absolute = Path("/tmp/arkheionx-example.json")
        self.assertEqual(resolve_input_path(absolute), absolute)
        self.assertEqual(resolve_output_path(absolute), absolute)


if __name__ == "__main__":
    unittest.main()

