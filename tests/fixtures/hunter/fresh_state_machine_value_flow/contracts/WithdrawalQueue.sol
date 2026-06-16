// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address a) external view returns (uint256);
}

/// @notice Withdrawal queue with a request -> claimable -> claimed state machine.
contract WithdrawalQueue {
    IERC20 public asset;
    enum Status { None, Requested, Claimable, Claimed }
    struct Request { address owner; uint256 amount; Status status; }
    mapping(uint256 => Request) public requests;
    uint256 public cursor;
    uint256 public queueIndex;

    function requestWithdrawal(uint256 amount) external returns (uint256 id) {
        id = queueIndex++;
        requests[id] = Request(msg.sender, amount, Status.Requested);
    }

    function markClaimable(uint256 id) external {
        requests[id].status = Status.Claimable;
    }

    function claimWithdrawal(uint256 id) external {
        Request storage r = requests[id];
        require(r.status == Status.Claimable, "not claimable");
        asset.transfer(r.owner, r.amount);
        r.status = Status.Claimed;
        cursor++;
    }
}
