// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ExampleComplianceList} from "./ExampleComplianceList.sol";

/// @title ExampleStablecoin (synthetic)
/// @notice Generic stablecoin minted against backing. Synthetic demo only.
contract ExampleStablecoin {
    string public constant name = "Example USD";
    string public constant symbol = "exUSD";
    uint8 public constant decimals = 18;

    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    address public manager;
    ExampleComplianceList public compliance;

    error NotManager();
    error Blocked(address who);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Mint(address indexed to, uint256 value);
    event Redeem(address indexed from, uint256 value);

    modifier onlyManager() {
        if (msg.sender != manager) revert NotManager();
        _;
    }

    constructor(address manager_, address compliance_) {
        manager = manager_;
        compliance = ExampleComplianceList(compliance_);
    }

    /// @notice Mint stablecoin to a recipient. Manager-gated value entry.
    function mint(address to, uint256 amount) external onlyManager {
        if (compliance.isBlocked(to)) revert Blocked(to);
        totalSupply += amount;
        balanceOf[to] += amount;
        emit Mint(to, amount);
        emit Transfer(address(0), to, amount);
    }

    /// @notice Redeem (burn) stablecoin. Value exit.
    function redeem(address from, uint256 amount) external onlyManager {
        balanceOf[from] -= amount;
        totalSupply -= amount;
        emit Redeem(from, amount);
        emit Transfer(from, address(0), amount);
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        if (compliance.isBlocked(msg.sender)) revert Blocked(msg.sender);
        if (compliance.isBlocked(to)) revert Blocked(to);
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        if (compliance.isBlocked(from) || compliance.isBlocked(to)) revert Blocked(from);
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
        return true;
    }
}
