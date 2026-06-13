// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// @notice INVALID evidence example for the evidence judge.
/// It does not reference any in-scope contract or target function and makes no
/// assertion, so it cannot prove any task. The judge should grade it invalid.
contract ScratchScratchTest is Test {
    function testScratchArithmetic() public {
        uint256 z = 2 + 3;
        z = z * 2;
        // No assertion, no protocol target: this proves nothing.
    }
}
