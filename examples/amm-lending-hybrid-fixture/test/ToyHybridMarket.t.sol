// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/ToyHybridMarket.sol";

contract ToyHybridMarketTest is Test {
    ToyReserveOracle internal pool;
    ToyHybridMarket internal market;
    address internal alice = address(0xA11CE);

    function setUp() public {
        pool = new ToyReserveOracle();
        market = new ToyHybridMarket(pool);
        vm.deal(alice, 10 ether);
    }

    function testBorrowUsesPoolQuote() public {
        vm.startPrank(alice);
        market.depositCollateral{value: 1 ether}();
        market.borrow(100 ether);
        vm.stopPrank();
        assertEq(market.debt(alice), 100 ether);
    }

    function testPoolSwapChangesQuote() public {
        uint256 out = pool.swap(10 ether);
        assertGt(out, 0);
    }
}
