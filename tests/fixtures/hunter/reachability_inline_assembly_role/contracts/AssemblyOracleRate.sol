// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract AssemblyOracleRate {
    bytes32 internal constant ORACLE_SLOT = keccak256("ark.test.oracle");
    uint256 public rate;

    function oracle() public view returns (address oracle_) {
        bytes32 slot = ORACLE_SLOT;
        assembly {
            oracle_ := sload(slot)
        }
    }

    modifier onlyOracle() {
        require(msg.sender == oracle(), "ONLY_ORACLE");
        _;
    }

    function updateRate(uint256 newRate) external onlyOracle {
        rate = newRate;
    }
}
