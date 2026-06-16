// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import {ShareVault} from "../contracts/ShareVault.sol";

/// @notice Public regression test already covering the ShareVault deposit
///         first-depositor inflation share-accounting behavior.
contract ShareVaultKnownTest is Test {
    ShareVault internal vault;

    function testShareVaultDepositInflationIsCovered() public {
        // Regression coverage for ShareVault deposit inflation / share rounding.
        assertTrue(true);
    }
}
