// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DocsOnlyPlanning {
    string public note = "oracle reward vault reentrancy planning terms only";

    function readNote() external view returns (string memory) {
        return note;
    }
}

