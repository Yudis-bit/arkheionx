// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Illustrative fixture test exercising the collateral-withdrawal health guard with
// a negative path. It exists so Arkheionx's static evidence classifier has a test
// that references withdrawCollateral, collateral, and debt with an expectRevert.
// It is not run by the Python test suite and asserts nothing about any real protocol.

import "../src/CreditMarket.sol";
import "../src/MockLoanToken.sol";

interface Vm {
    function expectRevert(bytes calldata) external;
    function prank(address) external;
}

contract CollateralHealthTest {
    CreditMarket market;
    MockLoanToken loan;
    Vm vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    function setUp() public {
        market = new CreditMarket();
        loan = new MockLoanToken();
    }

    function test_withdrawCollateral_reverts_when_unsafe() public {
        market.supplyCollateral(0, 100);
        market.borrow(0, 90);
        // Withdrawing collateral that leaves debt unhealthy must revert.
        vm.expectRevert("unsafe");
        market.withdrawCollateral(0, 100);
        assertEq(market_debt(0, address(this)), 90);
    }

    function market_debt(uint256 m, address who) internal view returns (uint256 debt) {
        ( , debt, , , , , ) = market.positions(m, who);
    }

    function assertEq(uint256 a, uint256 b) internal pure {
        require(a == b, "assertEq");
    }
}
