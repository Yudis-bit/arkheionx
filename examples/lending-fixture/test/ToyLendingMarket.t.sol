// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/ToyLendingMarket.sol";

contract MockPriceFeed is IPriceFeed {
    int256 public answer = 2_000e18;

    function setAnswer(int256 nextAnswer) external {
        answer = nextAnswer;
    }

    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80) {
        return (1, answer, block.timestamp, block.timestamp, 1);
    }
}

contract ToyLendingMarketTest is Test {
    MockPriceFeed internal feed;
    ToyLendingMarket internal market;
    address internal alice = address(0xA11CE);

    function setUp() public {
        feed = new MockPriceFeed();
        market = new ToyLendingMarket(feed);
        vm.deal(alice, 10 ether);
    }

    function testBorrowAndRepay() public {
        vm.startPrank(alice);
        market.depositCollateral{value: 1 ether}();
        market.borrow(100 ether);
        market.repay(25 ether);
        vm.stopPrank();
        assertEq(market.debt(alice), 75 ether);
    }

    function testOwnerCanPause() public {
        market.pause(true);
        assertTrue(market.paused());
    }
}

