from pathlib import Path

from arkheionx.warrun.orchestrator import (
    _SCOPE_NO_MATCH_SENTINEL,
    _normalize_scope_include_paths,
)


def test_scope_path_equal_to_target_root_includes_whole_target(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    target = workspace / "repos" / "generic-protocol"
    other = workspace / "repos" / "other-protocol"
    target.mkdir(parents=True)
    other.mkdir(parents=True)

    monkeypatch.chdir(workspace)

    assert _normalize_scope_include_paths(
        Path("repos/generic-protocol"),
        ["repos/generic-protocol", "repos/other-protocol"],
    ) is None


def test_scope_path_parent_of_target_includes_whole_target(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    target = workspace / "repos" / "generic-protocol"
    target.mkdir(parents=True)

    monkeypatch.chdir(workspace)

    assert _normalize_scope_include_paths(
        Path("repos/generic-protocol"),
        ["repos"],
    ) is None


def test_scope_path_child_of_target_becomes_target_relative(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    target = workspace / "repos" / "generic-protocol"
    contracts = target / "contracts"
    contracts.mkdir(parents=True)

    monkeypatch.chdir(workspace)

    assert _normalize_scope_include_paths(
        Path("repos/generic-protocol"),
        ["repos/generic-protocol/contracts"],
    ) == ["contracts"]


def test_unmatched_scope_path_matches_nothing(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    target = workspace / "repos" / "generic-protocol"
    other = workspace / "repos" / "other-protocol"
    target.mkdir(parents=True)
    other.mkdir(parents=True)

    monkeypatch.chdir(workspace)

    assert _normalize_scope_include_paths(
        Path("repos/generic-protocol"),
        ["repos/other-protocol"],
    ) == [_SCOPE_NO_MATCH_SENTINEL]
