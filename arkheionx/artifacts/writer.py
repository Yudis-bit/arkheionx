"""Deterministic local artifact writer for ArkheionX.

The writer is a small compatibility layer used by evidence, reporting, review
map, and CLI workflows. It only writes under a local artifacts root and never
performs network, RPC, live-chain, or subprocess actions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def default_artifacts_root(project_root: str | Path | None = None) -> Path:
    """Return the default local ArkheionX artifact root.

    When ``project_root`` is omitted, the current working directory is used.
    The returned path is ``<project>/.arkheionx/out``.
    """

    base = Path(project_root).expanduser() if project_root is not None else Path.cwd()
    return base / ".arkheionx" / "out"


class ArtifactWriter:
    """Write and read deterministic local ArkheionX artifacts.

    Parameters
    ----------
    project_root:
        Repository/project root by default. The artifact root becomes
        ``project_root/.arkheionx/out``.

        For compatibility, if the supplied path already looks like an artifact
        output directory, it is used directly.

    root:
        Explicit artifact root override.
    """

    def __init__(
        self,
        project_root: str | Path | None = None,
        *,
        root: str | Path | None = None,
    ) -> None:
        if root is not None:
            self.project_root = None
            self.root = Path(root).expanduser()
        elif project_root is None:
            self.project_root = Path.cwd()
            self.root = default_artifacts_root(self.project_root)
        else:
            candidate = Path(project_root).expanduser()
            self.project_root = candidate

            # Explicit artifact roots are respected. Ordinary repository roots
            # resolve to <repo>/.arkheionx/out.
            if (
                candidate.name == "out"
                and candidate.parent.name == ".arkheionx"
            ) or candidate.name in {"artifacts", "artifact-root"}:
                self.root = candidate
            else:
                self.root = default_artifacts_root(candidate)

        # Do not create the artifacts root during initialization.
        # No-write / pure JSON workflows must not leave .arkheionx/out behind.

    def __fspath__(self) -> str:
        return str(self.root)

    def __repr__(self) -> str:
        return f"ArtifactWriter(root={self.root!s})"

    def _safe_relative(self, relative_path: str | Path) -> Path:
        rel = Path(relative_path)

        if rel.is_absolute():
            raise ValueError(f"artifact path must be relative: {relative_path!s}")

        if any(part in {"", ".", ".."} for part in rel.parts):
            raise ValueError(f"unsafe artifact path: {relative_path!s}")

        return rel

    def path(self, relative_path: str | Path = "") -> Path:
        """Return a safe path under the artifact root."""

        if str(relative_path) == "":
            return self.root

        rel = self._safe_relative(relative_path)
        target = self.root / rel

        try:
            target.resolve().relative_to(self.root.resolve())
        except ValueError as exc:
            raise ValueError(f"artifact path escapes root: {relative_path!s}") from exc

        return target

    def ensure_dir(self, relative_path: str | Path = "") -> Path:
        """Create and return a directory under the artifact root."""

        target = self.path(relative_path)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def path_for(self, relative_path: str | Path = "") -> Path:
        """Compatibility alias returning a safe path under the artifact root."""

        return self.path(relative_path)

    def write_json(self, relative_path: str | Path, payload: Any) -> Path:
        """Write deterministic JSON and return the written path."""

        target = self.path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return target

    def read_json(self, relative_path: str | Path, default: Any = None) -> Any:
        """Read JSON from a local artifact path.

        If ``default`` is provided and the file is missing, the default is
        returned instead of raising ``FileNotFoundError``.
        """

        target = self.path(relative_path)
        if not target.exists() and default is not None:
            return default
        return json.loads(target.read_text(encoding="utf-8"))

    def write_text(self, relative_path: str | Path, text: str) -> Path:
        """Write text with a trailing newline and return the written path."""

        target = self.path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        body = text if text.endswith("\n") else text + "\n"
        target.write_text(body, encoding="utf-8")
        return target

    def read_text(self, relative_path: str | Path, default: str | None = None) -> str:
        """Read text from a local artifact path."""

        target = self.path(relative_path)
        if not target.exists() and default is not None:
            return default
        return target.read_text(encoding="utf-8")

    def exists(self, relative_path: str | Path) -> bool:
        """Return whether a local artifact exists."""

        return self.path(relative_path).exists()

    def glob(self, pattern: str) -> list[Path]:
        """Return sorted artifact paths matching a relative glob pattern."""

        if pattern.startswith("/") or ".." in Path(pattern).parts:
            raise ValueError(f"unsafe artifact glob: {pattern!s}")
        return sorted(self.root.glob(pattern))

    def iter_files(self, relative_path: str | Path = "") -> Iterable[Path]:
        """Yield files under a safe local artifact directory."""

        base = self.path(relative_path)
        if not base.exists():
            return []
        return sorted(path for path in base.rglob("*") if path.is_file())

    def write(self, relative_path: str | Path, payload: Any) -> Path:
        """Compatibility write helper.

        Strings are written as text. Other values are written as deterministic
        JSON.
        """

        if isinstance(payload, str):
            return self.write_text(relative_path, payload)
        return self.write_json(relative_path, payload)

    def write_artifact(
        self,
        group: str,
        name: str,
        payload: Any,
        *,
        suffix: str = ".json",
    ) -> Path:
        """Write an artifact under ``<group>/<name>``.

        ``suffix`` defaults to ``.json``. The name must remain relative and
        cannot escape the artifact root.
        """

        filename = name if Path(name).suffix else f"{name}{suffix}"
        relative = Path(group) / filename
        if suffix == ".json" and not isinstance(payload, str):
            return self.write_json(relative, payload)
        return self.write(relative, payload)

    def read_artifact(self, group: str, name: str, *, suffix: str = ".json") -> Any:
        """Read an artifact under ``<group>/<name>``."""

        filename = name if Path(name).suffix else f"{name}{suffix}"
        relative = Path(group) / filename
        if suffix == ".json":
            return self.read_json(relative)
        return self.read_text(relative)

    def list_artifacts(self, group: str = "", pattern: str = "*.json") -> list[Path]:
        """List artifacts under a group using a safe relative glob."""

        prefix = str(Path(group) / pattern) if group else pattern
        return self.glob(prefix)
