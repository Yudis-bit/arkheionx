// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: an adapter credits the NOMINAL transferred amount
// instead of the actual balance delta. With a fee-on-transfer / rebasing token the
// contract receives less than `amount`, yet credits `amount`, so credited > actual
// received. Repeated deposits let a depositor withdraw more than was ever received,
// draining the shared token balance. No protocol/token name is encoded.

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

// A non-standard token that takes a transfer fee: the recipient receives less
// than the sent amount. Models fee-on-transfer / deflationary tokens.
contract FeeOnTransferToken {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public feeBps; // e.g. 100 = 1%

    function setFeeBps(uint256 bps) external {
        feeBps = bps;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(allowance[from][msg.sender] >= amount, "allowance");
        allowance[from][msg.sender] -= amount;
        require(balanceOf[from] >= amount, "balance");
        uint256 fee = (amount * feeBps) / 10000;
        uint256 received = amount - fee;
        balanceOf[from] -= amount;
        balanceOf[to] += received; // recipient gets `received`, NOT `amount`
        return true;
    }
}

contract CreditAdapter {
    FeeOnTransferToken public token;
    mapping(address => uint256) public credit;

    function deposit(uint256 amount) external {
        // BUG: the adapter pulls tokens in, then credits the NOMINAL `amount`
        // rather than measuring the actual balance delta (balanceOf before/after).
        // For a fee-on-transfer token the contract receives less than `amount`,
        // so `credit` over-states what was actually received.
        token.transferFrom(msg.sender, address(this), amount);
        credit[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        require(credit[msg.sender] >= amount, "credit");
        credit[msg.sender] -= amount;
        token.transfer(msg.sender, amount);
    }
}
