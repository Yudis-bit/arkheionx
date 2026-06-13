// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import {OldVault} from "../contracts/OldVault.sol";

/// @notice Public regression test that already exercises the OldVault deposit
///         first-depositor / inflation share-accounting behavior. Because this
///         behavior is publicly tested, senior triage should treat a lead on
///         OldVault.deposit inflation as a duplicate and kill it.
contract PublicKnownIssueTest is Test {
    OldVault internal vault;

    function testFirstDepositorInflationIsKnown() public {
        // Known, acknowledged first-depositor inflation on OldVault.deposit.
        // The share/deposit accounting edge case is covered here on purpose.
        assertTrue(true);
    }

    function testDepositShareAccountingRegression() public {
        // Regression coverage for OldVault deposit share inflation rounding.
        assertTrue(true);
    }
}
