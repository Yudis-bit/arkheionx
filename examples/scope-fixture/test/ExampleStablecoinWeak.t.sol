// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ExampleStablecoin} from "../src/ExampleStablecoin.sol";
import {ExampleComplianceList} from "../src/ExampleComplianceList.sol";

/// @notice WEAK example: it acts and asserts, but has no pre/post accounting delta,
/// no negative path, and no boundary case. The judge should grade this weak.
contract ExampleStablecoinWeakTest {
    function test_transfer_returns_true() public {
        ExampleComplianceList compliance = new ExampleComplianceList(address(this));
        ExampleStablecoin coin = new ExampleStablecoin(address(this), address(compliance));
        coin.mint(address(this), 100);
        bool ok = coin.transfer(address(0xCAFE), 10);
        assertTrue(ok);
    }

    function assertTrue(bool c) internal pure { require(c, "false"); }
}
