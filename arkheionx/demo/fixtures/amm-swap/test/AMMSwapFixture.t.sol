// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../src/AMMSwapFixture.sol";

contract AMMSwapFixtureTest {
    function test_placeholderGetAmountOutShape() public pure {
        uint256 amountIn = 1_000;
        uint256 reserveIn = 1_000_000;
        uint256 reserveOut = 1_000_000;
        uint256 amountInWithFee = amountIn * (10000 - 30);
        uint256 out = (amountInWithFee * reserveOut) / (reserveIn * 10000 + amountInWithFee);

        assert(out > 0);
        assert(out < amountIn);
    }

    function test_placeholderFeeBound() public pure {
        uint256 feeBps = 30;

        assert(feeBps <= 1000);
    }
}
