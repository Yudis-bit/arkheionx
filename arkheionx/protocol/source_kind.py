"""Source-kind classification for files, contracts, and functions.

Used to keep default output focused on production-relevant code and to hide
interfaces, libraries, tests, invariants, mocks, fixtures, archives, generated
artifacts, and scripts unless the user passes --show-all.
"""
from __future__ import annotations

# Kinds that are structural noise for a money-flow review and always hidden by
# default regardless of whether production code exists.
STRUCTURAL_HIDDEN = {"interface", "library", "test", "invariant", "mock", "generated", "script", "archive"}
# Kinds hidden only when real production code is present in the same analysis.
SOFT_HIDDEN = {"fixture", "example"}

_GENERATED_DIRS = {"out", "cache", "node_modules", ".git", "artifacts", ".arkheionx", "lib", "broadcast", ".venv"}


def file_source_kind(rel_path: str) -> str | None:
    """Structural source kind inferred from a file path, or None to defer."""

    lower = rel_path.lower()
    parts = lower.split("/")
    if set(parts) & _GENERATED_DIRS:
        return "generated"
    if lower.endswith((".t.sol", ".test.sol")) or "test" in parts or "tests" in parts:
        return "test"
    if "invariant" in lower or "invariants" in parts:
        return "invariant"
    if "mock" in lower or "mocks" in parts:
        return "mock"
    if "fixture" in lower or "fixtures" in parts:
        return "fixture"
    if "example" in parts or "examples" in parts:
        return "example"
    if parts and parts[0] == "evm" or "exploit" in lower:
        return "archive"
    if "script" in parts or "scripts" in parts:
        return "script"
    if "templates" in parts:
        return "generated"
    return None


def contract_source_kind(contract: dict, file_kind: str | None) -> str:
    name = str(contract.get("name", ""))
    lname = name.lower()
    kind = str(contract.get("kind", "contract"))
    functions = contract.get("functions", []) or []
    if kind == "interface":
        return "interface"
    if kind == "library":
        return "library"
    if file_kind:
        return file_kind
    if any(tag in lname for tag in ("mock", "fake", "stub")):
        return "mock"
    if lname.endswith("test") or "harness" in lname:
        return "test"
    if "invariant" in lname:
        return "invariant"
    if name.startswith("I") and len(name) > 1 and name[1].isupper() and not functions:
        return "interface"
    return "production"


def function_source_kind(function: dict, contract_kind: str) -> str:
    if contract_kind in STRUCTURAL_HIDDEN or contract_kind in SOFT_HIDDEN:
        # Inherit the contract kind, but still flag test/invariant helpers.
        base = contract_kind
    else:
        base = "production"
    name = str(function.get("name", "")).lower()
    if name.startswith("invariant"):
        return "invariant"
    if name.startswith(("test", "prove", "echidna", "fuzz_")) or name in {"setup"}:
        return "test"
    return base


def hidden_category(source_kind: str) -> str:
    """Group a hidden source kind into a display bucket."""

    if source_kind in {"interface", "library"}:
        return "interfaces"
    if source_kind in {"test", "invariant"}:
        return "tests_invariants"
    if source_kind in {"mock", "fixture", "example"}:
        return "mocks_fixtures"
    if source_kind == "archive":
        return "archive"
    if source_kind == "script":
        return "scripts"
    return "generated"


_CATEGORY_LABELS = {
    "interfaces": "interfaces",
    "tests_invariants": "tests/invariants",
    "mocks_fixtures": "mocks/fixtures",
    "archive": "archive contracts",
    "scripts": "scripts",
    "generated": "generated",
}


def category_label(category: str) -> str:
    return _CATEGORY_LABELS.get(category, category)
