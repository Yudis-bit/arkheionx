"""Real Protocol Fixture Set 1 registry (v3.9, additive, internal-only).

A pure, deterministic registry of the local/static illustrative fixtures under
``tests/fixtures/fixture_harness/set1/`` (an ERC20-like token, a lending vault,
and a staking/reward shape). It builds fixture metadata and source artifact
references using the fixture harness model only -- it reads no fixture file,
computes no checksum, runs no fixture, accesses no filesystem or network, and
executes no benchmark. The relative paths are recorded as strings only.

These fixtures are review-surface inputs for deterministic fixture/benchmark
coverage. A fixture passing the harness never proves the source is safe and a
fixture failing never proves a vulnerability. Every record keeps
``manual_review_required`` true and ``ready_for_submission`` false. Importing this
module has no side effects.
"""
from __future__ import annotations

from .ids import fixture_artifact_id
from .model import (
    BENCHMARK_DIMENSION_CROSSREF_OUTCOMES,
    BENCHMARK_DIMENSION_GRAPH_COUNTS,
    BENCHMARK_DIMENSION_ID_STABILITY,
    BENCHMARK_DIMENSION_JSON_STABILITY,
    BENCHMARK_DIMENSION_NO_OVERCLAIM,
    BENCHMARK_DIMENSION_REVIEW_CONTEXT,
    FIXTURE_ARTIFACT_EVIDENCE,
    FIXTURE_ARTIFACT_PROTOCOL_GRAPH,
    FIXTURE_ARTIFACT_PROTOCOL_MODEL,
    FIXTURE_ARTIFACT_REPORT,
    FIXTURE_ARTIFACT_REVIEW_PACKAGE,
    FIXTURE_ARTIFACT_SOURCE,
    FIXTURE_CATEGORY_ERC20,
    FIXTURE_CATEGORY_LENDING_VAULT,
    FIXTURE_CATEGORY_STAKING_REWARD,
    FIXTURE_CATEGORY_AMM_SWAP,
    FIXTURE_CATEGORY_ORACLE_DEPENDENT,
    FIXTURE_CATEGORY_UPGRADEABLE_PROXY,
    FIXTURE_CATEGORY_BRIDGE_MESSAGE,
    FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY,
    FIXTURE_CATEGORY_MISC,
    FixtureArtifactRef,
    ProtocolFixture,
    FixtureSuite,
    build_fixture_suite,
    build_protocol_fixture,
)

SET1_SUITE_NAME = "fixture-harness-set1"
SET1_ROOT = "tests/fixtures/fixture_harness/set1"

# Benchmark dimensions every Set 1 fixture participates in.
_SET1_BENCHMARK_DIMENSIONS = (
    BENCHMARK_DIMENSION_ID_STABILITY,
    BENCHMARK_DIMENSION_JSON_STABILITY,
    BENCHMARK_DIMENSION_GRAPH_COUNTS,
    BENCHMARK_DIMENSION_CROSSREF_OUTCOMES,
    BENCHMARK_DIMENSION_NO_OVERCLAIM,
    BENCHMARK_DIMENSION_REVIEW_CONTEXT,
)

# Artifact kinds the core is expected to be able to derive for each fixture.
_SET1_EXPECTED_ARTIFACT_KINDS = (
    FIXTURE_ARTIFACT_SOURCE,
    FIXTURE_ARTIFACT_PROTOCOL_MODEL,
    FIXTURE_ARTIFACT_PROTOCOL_GRAPH,
    FIXTURE_ARTIFACT_EVIDENCE,
    FIXTURE_ARTIFACT_REPORT,
    FIXTURE_ARTIFACT_REVIEW_PACKAGE,
)

_SET1_TAGS = ("set1", "local-static", "illustrative")

# (name, category, source relative path, description). Strings only; no file read.
_SET1_SPECS: tuple[tuple[str, str, str, str], ...] = (
    (
        "erc20_like",
        FIXTURE_CATEGORY_ERC20,
        f"{SET1_ROOT}/erc20_like/ERC20Like.sol",
        "Local/static illustrative ERC20-like token shape (transfer / approve / "
        "transferFrom / mint / burn / pause).",
    ),
    (
        "lending_vault",
        FIXTURE_CATEGORY_LENDING_VAULT,
        f"{SET1_ROOT}/lending_vault/LendingVault.sol",
        "Local/static illustrative lending vault shape (deposit / withdraw / "
        "borrow / repay / liquidate / oracle-dependent liquidity).",
    ),
    (
        "staking_reward",
        FIXTURE_CATEGORY_STAKING_REWARD,
        f"{SET1_ROOT}/staking_reward/StakingReward.sol",
        "Local/static illustrative staking/reward shape (stake / withdraw / "
        "claimReward / notifyRewardAmount / pause).",
    ),
)


def set1_fixture_definitions() -> list[ProtocolFixture]:
    """Return the three Set 1 fixtures with deterministic IDs (pure, no I/O)."""

    fixtures: list[ProtocolFixture] = []
    for name, category, source_path, description in _SET1_SPECS:
        fixtures.append(build_protocol_fixture(
            name,
            category,
            relative_path=source_path,
            description=description,
            source_files=[source_path],
            expected_artifact_kinds=list(_SET1_EXPECTED_ARTIFACT_KINDS),
            benchmark_dimensions=list(_SET1_BENCHMARK_DIMENSIONS),
            tags=list(_SET1_TAGS),
        ))
    return fixtures


def set1_fixture_artifacts() -> list[FixtureArtifactRef]:
    """Return one source artifact reference per Set 1 fixture source file.

    Checksums and sizes are intentionally left empty/zero here; a later agent
    computes them. Reads no file.
    """

    artifacts: list[FixtureArtifactRef] = []
    for fixture in set1_fixture_definitions():
        source_path = fixture.relative_path
        artifacts.append(FixtureArtifactRef(
            artifact_id=fixture_artifact_id(fixture.fixture_id, FIXTURE_ARTIFACT_SOURCE, source_path),
            fixture_id=fixture.fixture_id,
            artifact_kind=FIXTURE_ARTIFACT_SOURCE,
            relative_path=source_path,
            checksum_sha256="",
            size_bytes=0,
            manual_review_required=True,
            ready_for_submission=False,
        ))
    return artifacts


def build_set1_fixture_suite() -> FixtureSuite:
    """Build the deterministic Set 1 fixture suite (definitions + source artifacts).

    No runs, results, or snapshots are attached at this stage. Reads no file and
    executes no benchmark.
    """

    return build_fixture_suite(
        SET1_SUITE_NAME,
        fixtures=set1_fixture_definitions(),
        artifact_refs=set1_fixture_artifacts(),
    )


# --- Real Protocol Fixture Set 2 (AMM / oracle-dependent / upgradeable proxy) ---

SET2_SUITE_NAME = "fixture-harness-set2"
SET2_ROOT = "tests/fixtures/fixture_harness/set2"

_SET2_TAGS = ("set2", "local-static", "illustrative")

# (name, category, source relative path, description). Strings only; no file read.
_SET2_SPECS: tuple[tuple[str, str, str, str], ...] = (
    (
        "amm_swap",
        FIXTURE_CATEGORY_AMM_SWAP,
        f"{SET2_ROOT}/amm_swap/AMMSwap.sol",
        "Local/static illustrative AMM / swap shape (addLiquidity / removeLiquidity "
        "/ swapExactTokensForTokens / getAmountOut / sync / setFeeBps / pause).",
    ),
    (
        "oracle_dependent",
        FIXTURE_CATEGORY_ORACLE_DEPENDENT,
        f"{SET2_ROOT}/oracle_dependent/OracleDependentVault.sol",
        "Local/static illustrative oracle-dependent vault shape (deposit / withdraw "
        "/ borrow / repay / getHealthFactor / liquidate / updateOracle / "
        "setRiskParameter).",
    ),
    (
        "upgradeable_proxy",
        FIXTURE_CATEGORY_UPGRADEABLE_PROXY,
        f"{SET2_ROOT}/upgradeable_proxy/UpgradeableProxyShape.sol",
        "Local/static illustrative upgradeable proxy shape (implementation / admin "
        "/ upgradeTo / changeAdmin / delegateToImplementation placeholder / pause).",
    ),
)


def set2_fixture_definitions() -> list[ProtocolFixture]:
    """Return the three Set 2 fixtures with deterministic IDs (pure, no I/O)."""

    fixtures: list[ProtocolFixture] = []
    for name, category, source_path, description in _SET2_SPECS:
        fixtures.append(build_protocol_fixture(
            name,
            category,
            relative_path=source_path,
            description=description,
            source_files=[source_path],
            expected_artifact_kinds=list(_SET1_EXPECTED_ARTIFACT_KINDS),
            benchmark_dimensions=list(_SET1_BENCHMARK_DIMENSIONS),
            tags=list(_SET2_TAGS),
        ))
    return fixtures


def set2_fixture_artifacts() -> list[FixtureArtifactRef]:
    """Return one source artifact reference per Set 2 fixture source file.

    Checksums and sizes are intentionally left empty/zero here; a later agent
    computes them. Reads no file.
    """

    artifacts: list[FixtureArtifactRef] = []
    for fixture in set2_fixture_definitions():
        source_path = fixture.relative_path
        artifacts.append(FixtureArtifactRef(
            artifact_id=fixture_artifact_id(fixture.fixture_id, FIXTURE_ARTIFACT_SOURCE, source_path),
            fixture_id=fixture.fixture_id,
            artifact_kind=FIXTURE_ARTIFACT_SOURCE,
            relative_path=source_path,
            checksum_sha256="",
            size_bytes=0,
            manual_review_required=True,
            ready_for_submission=False,
        ))
    return artifacts


def build_set2_fixture_suite() -> FixtureSuite:
    """Build the deterministic Set 2 fixture suite (definitions + source artifacts).

    No runs, results, or snapshots are attached at this stage. Reads no file and
    executes no benchmark.
    """

    return build_fixture_suite(
        SET2_SUITE_NAME,
        fixtures=set2_fixture_definitions(),
        artifact_refs=set2_fixture_artifacts(),
    )


# --- Real Protocol Fixture Set 3 (bridge / liquidation / governance-timelock) ---

SET3_SUITE_NAME = "fixture-harness-set3"
SET3_ROOT = "tests/fixtures/fixture_harness/set3"

_SET3_TAGS = ("set3", "local-static", "illustrative")

# (name, category, source relative path, description). Strings only; no file read.
# The governance/timelock shape has no dedicated controlled category, so it is
# registered under FIXTURE_CATEGORY_MISC (a known category, so it does not warn).
_SET3_SPECS: tuple[tuple[str, str, str, str], ...] = (
    (
        "bridge_message",
        FIXTURE_CATEGORY_BRIDGE_MESSAGE,
        f"{SET3_ROOT}/bridge_message/BridgeMessageShape.sol",
        "Local/static illustrative bridge / message shape (sendMessage / "
        "receiveMessage / verifyMessage / markMessageProcessed / setMessageVerifier "
        "/ nonce tracking / pause).",
    ),
    (
        "liquidation_engine",
        FIXTURE_CATEGORY_LIQUIDATION_BORROW_REPAY,
        f"{SET3_ROOT}/liquidation_engine/LiquidationEngineShape.sol",
        "Local/static illustrative liquidation / borrow-repay shape "
        "(depositCollateral / withdrawCollateral / borrow / repay / "
        "getAccountLiquidity / isLiquidatable / liquidate / setLiquidationBonus / "
        "setCloseFactor / oracle).",
    ),
    (
        "governance_timelock",
        FIXTURE_CATEGORY_MISC,
        f"{SET3_ROOT}/governance_timelock/GovernanceTimelockShape.sol",
        "Local/static illustrative governance / timelock shape (propose / queue / "
        "execute / cancel / setDelay / grantRole / revokeRole / getProposalState).",
    ),
)


def set3_fixture_definitions() -> list[ProtocolFixture]:
    """Return the three Set 3 fixtures with deterministic IDs (pure, no I/O)."""

    fixtures: list[ProtocolFixture] = []
    for name, category, source_path, description in _SET3_SPECS:
        fixtures.append(build_protocol_fixture(
            name,
            category,
            relative_path=source_path,
            description=description,
            source_files=[source_path],
            expected_artifact_kinds=list(_SET1_EXPECTED_ARTIFACT_KINDS),
            benchmark_dimensions=list(_SET1_BENCHMARK_DIMENSIONS),
            tags=list(_SET3_TAGS),
        ))
    return fixtures


def set3_fixture_artifacts() -> list[FixtureArtifactRef]:
    """Return one source artifact reference per Set 3 fixture source file.

    Checksums and sizes are intentionally left empty/zero here; a later agent
    computes them. Reads no file.
    """

    artifacts: list[FixtureArtifactRef] = []
    for fixture in set3_fixture_definitions():
        source_path = fixture.relative_path
        artifacts.append(FixtureArtifactRef(
            artifact_id=fixture_artifact_id(fixture.fixture_id, FIXTURE_ARTIFACT_SOURCE, source_path),
            fixture_id=fixture.fixture_id,
            artifact_kind=FIXTURE_ARTIFACT_SOURCE,
            relative_path=source_path,
            checksum_sha256="",
            size_bytes=0,
            manual_review_required=True,
            ready_for_submission=False,
        ))
    return artifacts


def build_set3_fixture_suite() -> FixtureSuite:
    """Build the deterministic Set 3 fixture suite (definitions + source artifacts).

    No runs, results, or snapshots are attached at this stage. Reads no file and
    executes no benchmark.
    """

    return build_fixture_suite(
        SET3_SUITE_NAME,
        fixtures=set3_fixture_definitions(),
        artifact_refs=set3_fixture_artifacts(),
    )


# --- Combined all-fixtures registry (Set 1 + Set 2 + Set 3) -------------------

ALL_SUITE_NAME = "fixture-harness-all"


def all_fixture_definitions() -> list[ProtocolFixture]:
    """Return every registered fixture in deterministic set order (set1, set2, set3).

    Nine fixtures total. Pure, no I/O. The per-set order and the cross-set order
    are both fixed, so the combined list is deterministic across calls.
    """

    return (
        set1_fixture_definitions()
        + set2_fixture_definitions()
        + set3_fixture_definitions()
    )


def all_fixture_artifacts() -> list[FixtureArtifactRef]:
    """Return every registered source artifact in set order (set1, set2, set3).

    Nine source artifacts total. Pure, no I/O.
    """

    return (
        set1_fixture_artifacts()
        + set2_fixture_artifacts()
        + set3_fixture_artifacts()
    )


def build_all_fixture_suite() -> FixtureSuite:
    """Build the deterministic combined all-fixtures suite (9 fixtures, 9 artifacts).

    No runs, results, or snapshots are attached at this stage. The suite ID is
    order-independent (derived from sorted fixture IDs). Reads no file and executes
    no benchmark.
    """

    return build_fixture_suite(
        ALL_SUITE_NAME,
        fixtures=all_fixture_definitions(),
        artifact_refs=all_fixture_artifacts(),
    )
