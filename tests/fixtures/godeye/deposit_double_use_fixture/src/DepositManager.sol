// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: a deposit consumed via an external transfer before
// its active flag is cleared (state write after external call), enabling a
// double-use / reentrancy window.

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract DepositManager {
    struct Deposit {
        address owner;
        uint256 amount;
        bool active;
    }

    mapping(bytes32 => Deposit) public deposits;
    IERC20 public token;

    function createDeposit(bytes32 key, uint256 amount) external {
        deposits[key] = Deposit(msg.sender, amount, true);
        token.transferFrom(msg.sender, address(this), amount);
    }

    function consume(bytes32 key) external {
        Deposit storage d = deposits[key];
        require(d.active, "inactive");
        // External interaction occurs before the effect (clearing `active`).
        token.transfer(d.owner, d.amount);
        d.active = false;
    }
}
