// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {CreditVault, IERC20} from "../src/CreditVault.sol";
import {PriceOracle} from "../src/PriceOracle.sol";
import {MockToken} from "../src/MockToken.sol";

/// @notice Local/static demo test. Covers the deposit entry path only and
/// deliberately leaves withdraw, borrow, repay, liquidate, the oracle setter,
/// the ClaimGate authorization surfaces (signature + Merkle), and the
/// BundleRouter periphery batch untested so ArkheionX surfaces them as likely
/// blind spots. Not an exploit target.
contract CreditVaultTest {
    CreditVault vault;
    PriceOracle oracle;
    MockToken token;

    function setUp() public {
        token = new MockToken();
        oracle = new PriceOracle();
        vault = new CreditVault(IERC20(address(token)), oracle);
    }

    function test_deposit_mints_shares() public {
        token.mint(address(this), 100);
        token.approve(address(vault), 100);
        uint256 minted = vault.deposit(100);
        assert(minted == 100);
        assert(vault.shares(address(this)) == 100);
    }
}
