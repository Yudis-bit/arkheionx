// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IExamplePayoutAsset {
    function transfer(address to, uint256 amount) external returns (bool);
}

/// @title ExampleWithdrawalNFT (synthetic)
/// @notice Transferable withdrawal-claim NFT backed by a funded queue. Demo only.
contract ExampleWithdrawalNFT {
    IExamplePayoutAsset public asset;
    address public manager;

    struct Claim {
        address owner;
        uint256 amount;
        bool consumed;
    }

    uint256 public nextId;
    uint256 public funded;
    mapping(uint256 => Claim) public claims;

    event ClaimCreated(uint256 indexed id, address indexed owner, uint256 amount);
    event ClaimTransferred(uint256 indexed id, address indexed from, address indexed to);
    event ClaimSettled(uint256 indexed id, address indexed to, uint256 amount);

    error NotManager();
    error NotOwner();
    error AlreadyConsumed();
    error Underfunded();

    modifier onlyManager() {
        if (msg.sender != manager) revert NotManager();
        _;
    }

    constructor(address asset_, address manager_) {
        asset = IExamplePayoutAsset(asset_);
        manager = manager_;
    }

    function fund(uint256 amount) external onlyManager {
        funded += amount;
    }

    /// @notice Create a deferred withdrawal claim for a user.
    function requestWithdrawal(address owner, uint256 amount) external onlyManager returns (uint256 id) {
        id = ++nextId;
        claims[id] = Claim({owner: owner, amount: amount, consumed: false});
        emit ClaimCreated(id, owner, amount);
    }

    /// @notice Transfer claim ownership (transferable claim NFT).
    function transferClaim(uint256 id, address to) external {
        Claim storage c = claims[id];
        if (c.owner != msg.sender) revert NotOwner();
        c.owner = to;
        emit ClaimTransferred(id, msg.sender, to);
    }

    /// @notice Settle a claim. Pays the current owner; single-use; bounded by funding.
    function settle(uint256 id) external returns (uint256 amount) {
        Claim storage c = claims[id];
        if (c.owner != msg.sender) revert NotOwner();
        if (c.consumed) revert AlreadyConsumed();
        amount = c.amount;
        if (amount > funded) revert Underfunded();
        c.consumed = true;
        funded -= amount;
        asset.transfer(c.owner, amount);
        emit ClaimSettled(id, c.owner, amount);
    }
}
