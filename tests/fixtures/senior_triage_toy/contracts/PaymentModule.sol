// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @title PaymentModule
/// @notice A value-bearing module that the scope note does not describe and that
///         no known issue or audit covers. Triage should park this until more
///         context arrives, rather than pursue or kill it blindly.
contract PaymentModule {
    IERC20 public asset;
    mapping(address => uint256) public funded;

    constructor(IERC20 asset_) {
        asset = asset_;
    }

    /// @notice Pull value in to fund a position.
    function fund(uint256 amount) external {
        require(asset.transferFrom(msg.sender, address(this), amount), "pull failed");
        funded[msg.sender] += amount;
    }
}
