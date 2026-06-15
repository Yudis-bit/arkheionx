"""Path filters for source and dependency discovery."""
from __future__ import annotations

DEFAULT_EXCLUDED = {
    ".git",
    ".arkheionx",
    "node_modules",
    "cache",
    "artifacts",
    "build",
    "out",
    "broadcast",
    "coverage",
    "typechain",
    "generated",
    "dist",
    "__pycache__",
    ".vscode",
    ".idea",
}

DEPENDENCY_DIRS = {"lib", "dependencies", "vendor", "external"}
TEST_DIRS = {"test", "tests"}
SCRIPT_DIRS = {"script", "scripts", "migrations"}


def exclusion_reason(parts, *, include_deps=False, include_tests=False, include_scripts=False):
    lowered = {part.lower() for part in parts}
    if lowered & DEFAULT_EXCLUDED:
        return "generated_or_build"
    if not include_deps and lowered & DEPENDENCY_DIRS:
        return "dependency"
    if not include_tests and lowered & TEST_DIRS:
        return "test"
    if not include_scripts and lowered & SCRIPT_DIRS:
        return "script"
    return ""
