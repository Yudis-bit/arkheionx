// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ExampleOracle} from "../src/ExampleOracle.sol";

/// @notice INVALID example: it calls the target but never asserts an outcome
/// (it only shows the call did not revert). The judge should grade this invalid.
contract ExampleOracleInvalidTest {
    function test_setPrice_does_not_revert() public {
        ExampleOracle oracle = new ExampleOracle(address(this));
        oracle.setPrice(1e8);
        oracle.price();
        // No assertion: this does not prove anything about the intended behaviour.
    }
}
