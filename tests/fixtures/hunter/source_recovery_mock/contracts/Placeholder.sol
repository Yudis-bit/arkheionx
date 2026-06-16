// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// The in-scope RemoteVault has no local source; only this unrelated helper is local.
contract Placeholder {
    uint256 public x;
    function set(uint256 v) external { x = v; }
}
