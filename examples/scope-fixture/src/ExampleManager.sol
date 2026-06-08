// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ExampleStablecoin} from "./ExampleStablecoin.sol";

/// @title ExampleManager (synthetic)
/// @notice Custodial signed-mint manager with replay protection and admin powers.
contract ExampleManager {
    ExampleStablecoin public stablecoin;
    address public admin;
    address public signer;
    bool public paused;

    mapping(bytes32 => bool) public usedReference;
    mapping(address => uint256) public nonces;

    bytes32 public immutable DOMAIN_SEPARATOR;
    bytes32 public constant MINT_TYPEHASH =
        keccak256("Mint(address to,uint256 amount,uint256 nonce,uint256 deadline)");

    error NotAdmin();
    error Paused();
    error BadSignature();
    error Expired();
    error ReplayedReference();

    modifier onlyAdmin() {
        if (msg.sender != admin) revert NotAdmin();
        _;
    }

    constructor(address stablecoin_, address admin_, address signer_) {
        stablecoin = ExampleStablecoin(stablecoin_);
        admin = admin_;
        signer = signer_;
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(keccak256("EIP712Domain(uint256 chainId,address verifyingContract)"),
                       block.chainid, address(this)));
    }

    /// @notice Mint via a trusted custodian signature. Replay-protected by nonce + deadline.
    function signedMint(address to, uint256 amount, uint256 deadline, uint8 v, bytes32 r, bytes32 s) external {
        if (paused) revert Paused();
        if (block.timestamp > deadline) revert Expired();
        uint256 nonce = nonces[to];
        bytes32 structHash = keccak256(abi.encode(MINT_TYPEHASH, to, amount, nonce, deadline));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
        if (ecrecover(digest, v, r, s) != signer) revert BadSignature();
        nonces[to] = nonce + 1;
        stablecoin.mint(to, amount);
    }

    /// @notice Batched signed mints (intended design).
    function batchSignedMint(
        address[] calldata to, uint256[] calldata amount,
        uint256[] calldata deadline, uint8[] calldata v, bytes32[] calldata r, bytes32[] calldata s
    ) external {
        for (uint256 i = 0; i < to.length; i++) {
            this.signedMint(to[i], amount[i], deadline[i], v[i], r[i], s[i]);
        }
    }

    function redeemFor(address from, uint256 amount) external onlyAdmin {
        stablecoin.redeem(from, amount);
    }

    /// @notice Admin emergency pause (accepted centralization).
    function setPaused(bool p) external onlyAdmin {
        paused = p;
    }

    function setSigner(address newSigner) external onlyAdmin {
        signer = newSigner;
    }
}
