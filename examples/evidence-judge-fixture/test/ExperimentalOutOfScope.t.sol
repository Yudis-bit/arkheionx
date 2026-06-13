// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import {ExperimentalVault} from "../src/ExperimentalVault.sol";
import {MockToken} from "../src/MockToken.sol";

/// @notice OUT-OF-SCOPE evidence example for the evidence judge.
/// It targets ExperimentalVault.migrate, which `scope.json` marks out-of-scope
/// for the deployed snapshot. The judge should flag this as out-of-scope
/// regardless of the test's structure, so no finding is generated from it.
contract ExperimentalOutOfScopeTest is Test {
    ExperimentalVault internal experimental;
    MockToken internal asset;

    function setUp() public {
        asset = new MockToken();
        experimental = new ExperimentalVault(asset);
        asset.mint(address(this), 100 ether);
        asset.approve(address(experimental), 100 ether);
    }

    function test_migrate_records_deposit() public {
        uint256 pre = experimental.totalDeposited();
        experimental.migrate(10 ether);
        assertEq(experimental.totalDeposited(), pre + 10 ether);
    }
}
