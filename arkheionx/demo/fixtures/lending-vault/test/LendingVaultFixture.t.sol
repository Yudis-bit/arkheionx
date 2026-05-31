// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../src/LendingVaultFixture.sol";

contract LendingVaultFixtureTest {
    function test_placeholderHealthFactorShape() public pure {
        uint256 collateralValue = 1_000e18;
        uint256 collateralFactorBps = 7500;
        uint256 debt = 500e18;
        uint256 maxDebt = (collateralValue * collateralFactorBps) / 10000;
        uint256 health = (maxDebt * 1e18) / debt;

        assert(health >= 1e18);
    }

    function test_placeholderCollateralFactorBound() public pure {
        uint256 collateralFactorBps = 7500;

        assert(collateralFactorBps <= 10000);
    }
}
