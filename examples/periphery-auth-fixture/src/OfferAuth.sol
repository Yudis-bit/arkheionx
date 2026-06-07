// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title OfferAuth
/// @notice Generic authorization surface for the local review-map demo fixture:
/// EIP-712 signed offers, a Merkle allowlist gate, and an explicit
/// authorization mapping. This is a synthetic, generic pattern used to exercise
/// ArkheionX authorization-surface detection. Local/static demo only. Not
/// production code, not a deployable recommendation, and not an exploit target.
library MerkleProof {
    function verify(bytes32[] memory proof, bytes32 root, bytes32 leaf) internal pure returns (bool) {
        bytes32 computed = leaf;
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 p = proof[i];
            computed = computed <= p
                ? keccak256(abi.encodePacked(computed, p))
                : keccak256(abi.encodePacked(p, computed));
        }
        return computed == root;
    }
}

contract OfferAuth {
    struct Offer {
        address maker;
        uint256 amount;
        uint256 nonce;
        uint256 deadline;
    }

    bytes32 public constant OFFER_TYPEHASH =
        keccak256("Offer(address maker,uint256 amount,uint256 nonce,uint256 deadline)");

    address public owner;
    bytes32 public merkleRoot;
    mapping(address => uint256) public nonces;
    mapping(address => bool) public authorization;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(bytes32 root_) {
        owner = msg.sender;
        merkleRoot = root_;
    }

    /// @notice The EIP-712 domain separator binds chain id and verifying contract.
    function domainSeparator() public view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("OfferAuth")),
                block.chainid,
                address(this)
            )
        );
    }

    /// @notice Verify a signed offer. The recovered signer must be the maker and
    /// the nonce and deadline must be in force. Authorization is bound here.
    function authorizeOffer(Offer calldata offer, uint8 v, bytes32 r, bytes32 s) external returns (bool) {
        require(block.timestamp <= offer.deadline, "expired deadline");
        require(offer.nonce == nonces[offer.maker], "bad nonce");
        bytes32 structHash =
            keccak256(abi.encode(OFFER_TYPEHASH, offer.maker, offer.amount, offer.nonce, offer.deadline));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", domainSeparator(), structHash));
        address signer = ecrecover(digest, v, r, s);
        require(signer != address(0) && signer == offer.maker, "bad signature");
        nonces[offer.maker] += 1;
        return true;
    }

    /// @notice Gate a claim behind a Merkle proof. The leaf must bind the claimer
    /// and amount, and the proof must verify against the current root.
    function claimWithProof(bytes32[] calldata proof, uint256 amount) external view returns (bool) {
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, amount));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "bad proof");
        return true;
    }

    /// @notice Privileged: set the explicit operator authorization mapping.
    function setAuthorization(address operator, bool allowed) external onlyOwner {
        authorization[operator] = allowed;
    }

    /// @notice Read whether an operator is authorized.
    function isAuthorized(address operator) external view returns (bool) {
        return authorization[operator];
    }

    /// @notice Privileged: rotate the Merkle root that gates claims.
    function setMerkleRoot(bytes32 root_) external onlyOwner {
        merkleRoot = root_;
    }
}
