// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {LedgerCore} from "./LedgerCore.sol";

/// @title OfferBundler
/// @notice Periphery that bundles operations and routes them into LedgerCore.
/// It loops over items and is documented to skip a failing item (best effort)
/// rather than reverting the whole batch. Local/static demo only. Not production
/// code and not an exploit target.
contract OfferBundler {
    LedgerCore public immutable core;

    enum Kind { Supply, Borrow, Repay, Withdraw }

    struct Op {
        Kind kind;
        address account;
        uint256 amount;
    }

    event Skipped(uint256 index);

    constructor(LedgerCore core_) {
        core = core_;
    }

    /// @notice Execute a bundle of operations. Documented behavior: a malformed
    /// or failing item is skipped (best effort, continue-on-error); the rest of
    /// the batch still executes. A reviewer should confirm the skip path is
    /// actually reached and that pre-call computation does not revert earlier.
    function executeBundle(Op[] calldata ops) external {
        for (uint256 i = 0; i < ops.length; i++) {
            // Pre-call computation: an invalid amount here could revert before
            // the skip handler below is reached.
            uint256 amount = _normalize(ops[i].amount);
            try this.runOne(ops[i].kind, ops[i].account, amount) {
                continue;
            } catch {
                // Skip the failed item and continue with the next one.
                emit Skipped(i);
                continue;
            }
        }
    }

    /// @notice Run a single operation directly against the core. Used both by the
    /// bundle loop and as a direct-call equivalent for comparison.
    function runOne(Kind kind, address account, uint256 amount) external {
        require(msg.sender == address(this) || msg.sender == account, "not authorized");
        if (kind == Kind.Supply) {
            core.supply(account, amount);
        } else if (kind == Kind.Borrow) {
            core.borrow(account, amount);
        } else if (kind == Kind.Repay) {
            core.repay(account, amount);
        } else {
            core.withdraw(account, amount);
        }
    }

    /// @dev Reverts on a malformed (zero) amount. This runs before the try/catch
    /// skip handler in executeBundle.
    function _normalize(uint256 amount) internal pure returns (uint256) {
        require(amount != 0, "malformed amount");
        return amount;
    }
}
