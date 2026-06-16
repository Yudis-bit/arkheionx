// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract OracleRate {
    IERC20 public asset;
    address public oracle;
    uint256 public rate;

    modifier onlyOracle() {
        require(msg.sender == oracle, "ONLY_ORACLE");
        _;
    }

    function updateRate(uint256 newRate) external onlyOracle {
        rate = newRate;
    }

    function pushPayout(address to, uint256 amount) external onlyOracle {
        asset.transfer(to, amount);
    }
}
