// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../src/Vault.sol";
import "../src/MockToken.sol";
import "../src/PriceOracle.sol";

/// @notice Partial, illustrative test suite for the review-map demo fixture.
///
/// It covers the deposit entry path and a basic oracle price sanity check. It
/// deliberately leaves the value-exit and admin paths untested so Arkheionx can
/// surface them as test gaps. This is the whole point of the demo: a passing
/// test run that still has uncovered value paths.
contract VaultDepositTest {
    function test_depositMintsSharesOneToOne() public {
        MockToken token = new MockToken();
        PriceOracle priceSource = new PriceOracle(2000e18);
        Vault vault = new Vault(IERC20(address(token)), IOracle(address(priceSource)));

        token.mint(address(this), 100e18);
        token.approve(address(vault), 100e18);
        uint256 shares = vault.deposit(100e18);

        assert(shares == 100e18);
        assert(vault.totalShares() == 100e18);
    }

    function test_oracleGetPriceIsPositive() public {
        PriceOracle priceSource = new PriceOracle(2000e18);
        assert(priceSource.getPrice() == 2000e18);
    }
}
