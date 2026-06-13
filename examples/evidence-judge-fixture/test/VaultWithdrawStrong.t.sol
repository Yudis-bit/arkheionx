// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import {Vault} from "../src/Vault.sol";
import {MockToken} from "../src/MockToken.sol";

/// @notice STRONG evidence example for the evidence judge.
/// It targets Vault.withdraw, records pre/post balances and the totalShares
/// state delta, separates attacker and victim, exercises a dust boundary, and
/// includes a negative path (must-revert). This is review evidence, not a finding.
contract VaultWithdrawStrongTest is Test {
    Vault internal vault;
    MockToken internal asset;
    address internal victim;
    address internal attacker;

    function setUp() public {
        asset = new MockToken();
        vault = new Vault(asset);
        victim = makeAddr("victim");
        attacker = makeAddr("attacker");
        asset.mint(victim, 1_000 ether);
        asset.mint(attacker, 1_000 ether);
    }

    function test_withdraw_conserves_value() public {
        vm.startPrank(victim);
        asset.approve(address(vault), 100 ether);
        uint256 minted = vault.deposit(100 ether);

        uint256 preAssets = asset.balanceOf(victim);
        uint256 preShares = vault.shares(victim);
        uint256 preSupply = vault.totalShares();

        uint256 out = vault.withdraw(minted);

        uint256 postAssets = asset.balanceOf(victim);
        uint256 postShares = vault.shares(victim);
        uint256 postSupply = vault.totalShares();
        vm.stopPrank();

        // Pre/post balance and state-delta assertions on a value exit.
        assertEq(postAssets, preAssets + out, "asset balance delta");
        assertEq(preShares - postShares, minted, "share burn delta");
        assertEq(preSupply - postSupply, minted, "totalShares delta");
        assertLe(out, 100 ether, "cannot withdraw more than deposited");
    }

    function test_withdraw_dust_boundary() public {
        vm.startPrank(victim);
        asset.approve(address(vault), 1 ether);
        uint256 minted = vault.deposit(1 ether);
        uint256 out = vault.withdraw(1 wei);
        assertLe(out, 1 ether, "dust withdraw bounded");
        vm.stopPrank();
        assertGt(minted, 0);
    }

    function test_withdraw_insufficient_reverts() public {
        // Negative path: an attacker with no shares cannot withdraw.
        vm.prank(attacker);
        vm.expectRevert(Vault.InsufficientShares.selector);
        vault.withdraw(1 ether);
    }
}
