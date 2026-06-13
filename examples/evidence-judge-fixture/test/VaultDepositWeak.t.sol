// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import {Vault} from "../src/Vault.sol";
import {MockToken} from "../src/MockToken.sol";

/// @notice WEAK evidence example for the evidence judge.
/// It targets Vault.deposit but only makes one shallow assertion (that some
/// shares were minted). It records no pre/post balance or state delta, no
/// negative path, and no attacker/victim separation, so it does not close the
/// value-conservation question. This is intentionally weak fixture evidence.
contract VaultDepositWeakTest is Test {
    Vault internal vault;
    MockToken internal asset;

    function setUp() public {
        asset = new MockToken();
        vault = new Vault(asset);
        asset.mint(address(this), 1_000 ether);
        asset.approve(address(vault), 1_000 ether);
    }

    function test_deposit_mints_some_shares() public {
        uint256 minted = vault.deposit(100 ether);
        // Shallow assertion only: no pre/post balance delta, no supply delta.
        assertGt(minted, 0);
    }
}
