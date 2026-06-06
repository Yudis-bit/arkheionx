// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Local/static illustrative fixture for the Arkheionx fixture harness (v3.9).
// This is NOT an audited contract, NOT deployment-ready, and NOT a vulnerability
// report. It requires no network, no RPC, no fork, no private keys,
// no seed phrases, and no live chain. It exists only as static review-surface
// text for deterministic role / value-path / graph coverage. Manual review is
// required.

contract ERC20Like {
    string public name = "Fixture Token";
    string public symbol = "FIX";
    uint8 public decimals = 18;

    uint256 public totalSupply;
    address public owner;
    bool public paused;

    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "paused");
        _;
    }

    // View-like accessors (VIEW_PURE role coverage).
    function balanceOf(address account) external view returns (uint256) {
        return _balances[account];
    }

    function allowance(address account, address spender) external view returns (uint256) {
        return _allowances[account][spender];
    }

    // Approve / transfer / transferFrom (accounting + value movement coverage).
    function approve(address spender, uint256 amount) external returns (bool) {
        _allowances[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external whenNotPaused returns (bool) {
        _balances[msg.sender] -= amount;
        _balances[to] += amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external whenNotPaused returns (bool) {
        _allowances[from][msg.sender] -= amount;
        _balances[from] -= amount;
        _balances[to] += amount;
        return true;
    }

    // Mint / burn (MINT_BURN + accounting mutation coverage).
    function mint(address to, uint256 amount) external onlyOwner {
        totalSupply += amount;
        _balances[to] += amount;
    }

    function burn(uint256 amount) external {
        _balances[msg.sender] -= amount;
        totalSupply -= amount;
    }

    // Emergency pause controls (ACCESS_CONTROL / PAUSE_EMERGENCY coverage).
    function pause() external onlyOwner {
        paused = true;
    }

    function unpause() external onlyOwner {
        paused = false;
    }
}
