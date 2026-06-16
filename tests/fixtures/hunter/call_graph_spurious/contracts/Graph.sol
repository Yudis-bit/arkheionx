// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

contract Graph {
    IERC20 public asset;
    uint256 public reportCount; // a variable that merely shares the word 'report'

    function settle(address to, uint256 amount) internal {
        asset.transfer(to, amount);
    }

    function process(address to, uint256 amount) external {
        // process calls settle directly (a real edge)
        settle(to, amount);
    }

    // audit mentions report in a comment and uses reportCount, but never calls report()
    function audit() external {
        // this function does not call report(); it only reads reportCount
        reportCount += 1;
    }

    function report() external view returns (uint256) {
        return reportCount;
    }
}
