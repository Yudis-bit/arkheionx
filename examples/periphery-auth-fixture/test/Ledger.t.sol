// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {LedgerCore, IERC20} from "../src/LedgerCore.sol";
import {MockToken} from "../src/MockToken.sol";

/// @notice Local/static demo test. Covers the supply entry path only and
/// deliberately leaves borrow/repay/withdraw, the bundler, and the
/// authorization surfaces untested so ArkheionX surfaces them as gaps.
contract LedgerCoreTest {
    LedgerCore core;
    MockToken token;

    function setUp() public {
        token = new MockToken();
        core = new LedgerCore(IERC20(address(token)));
    }

    function test_supply_credits_account() public {
        token.mint(address(this), 100);
        token.approve(address(core), 100);
        core.supply(address(this), 100);
        assert(core.credit(address(this)) == 100);
    }
}
