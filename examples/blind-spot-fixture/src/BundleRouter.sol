// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {CreditVault} from "./CreditVault.sol";

/// @title BundleRouter
/// @notice Periphery that bundles operations and routes them into CreditVault. It
/// loops over items and is documented to skip a failing item (best effort,
/// continue-on-error) rather than reverting the whole batch, and exposes a
/// callback. A reviewer should confirm the periphery path matches the direct
/// core path, that the skip handler is actually reached, and that the callback
/// cannot reorder state. Local/static demo only. Not production code and not an
/// exploit target.
contract BundleRouter {
    CreditVault public immutable core;

    enum Kind { Deposit, Borrow, Repay, Withdraw }

    struct Op {
        Kind kind;
        address account;
        uint256 amount;
    }

    event Skipped(uint256 index);

    constructor(CreditVault core_) {
        core = core_;
    }

    /// @notice Execute a bundle of operations. Documented behavior: a malformed or
    /// failing item is skipped (best effort); the rest of the batch still runs. A
    /// reviewer should confirm the skip path is reached and that pre-call
    /// computation does not revert earlier than the documented skip handler.
    function executeBatch(Op[] calldata ops) external {
        for (uint256 i = 0; i < ops.length; i++) {
            uint256 amount = _normalize(ops[i].amount);
            try this.runOne(ops[i].kind, ops[i].account, amount) {
                continue;
            } catch {
                emit Skipped(i);
                continue;
            }
        }
    }

    /// @notice Run a single operation directly against the core. Used both by the
    /// batch loop and as a direct-call equivalent for comparison.
    function runOne(Kind kind, address account, uint256 amount) external {
        require(msg.sender == address(this) || msg.sender == account, "not authorized");
        if (kind == Kind.Borrow) {
            core.borrow(account, amount);
        } else if (kind == Kind.Repay) {
            core.repay(account, amount);
        } else {
            // Deposit/Withdraw are routed by the account directly in this demo.
            revert("unsupported in batch");
        }
    }

    /// @notice Callback surface. A reviewer should confirm the caller and state
    /// ordering assumptions hold and that this cannot re-enter unsafe state.
    function onSettlementCallback(address account, uint256 amount) external {
        require(msg.sender == address(core), "unexpected caller");
        // Best-effort hook; intentionally minimal in this generic demo.
    }

    /// @dev Reverts on a malformed (zero) amount. This runs before the try/catch
    /// skip handler in executeBatch.
    function _normalize(uint256 amount) internal pure returns (uint256) {
        require(amount != 0, "malformed amount");
        return amount;
    }
}
