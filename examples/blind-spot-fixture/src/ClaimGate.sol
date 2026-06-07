// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ClaimGate
/// @notice Generic authorization surface for the local review-map demo fixture:
/// an EIP-712 signed claim, a Merkle allowlist gate, and nonce/deadline replay
/// protection. Synthetic, generic patterns used to exercise ArkheionX
/// authorization-surface detection. Local/static demo only. Not production code
/// and not an exploit target.
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

contract ClaimGate {
    struct Claim {
        address account;
        uint256 amount;
        uint256 nonce;
        uint256 deadline;
    }

    bytes32 public constant CLAIM_TYPEHASH =
        keccak256("Claim(address account,uint256 amount,uint256 nonce,uint256 deadline)");

    address public owner;
    bytes32 public merkleRoot;
    mapping(address => uint256) public nonces;

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
                keccak256(bytes("ClaimGate")),
                block.chainid,
                address(this)
            )
        );
    }

    /// @notice Verify a signed claim. The recovered signer must be the account and
    /// the nonce and deadline must be in force. The digest must bind every
    /// value-relevant field and the domain data.
    function verifySignedClaim(Claim calldata claim, uint8 v, bytes32 r, bytes32 s)
        external
        returns (bool)
    {
        require(block.timestamp <= claim.deadline, "expired deadline");
        require(claim.nonce == nonces[claim.account], "bad nonce");
        bytes32 structHash =
            keccak256(abi.encode(CLAIM_TYPEHASH, claim.account, claim.amount, claim.nonce, claim.deadline));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", domainSeparator(), structHash));
        address signer = ecrecover(digest, v, r, s);
        require(signer != address(0) && signer == claim.account, "bad signature");
        nonces[claim.account] += 1;
        return true;
    }

    /// @notice Gate a claim behind a Merkle proof. The leaf must bind the claimer
    /// and amount, and the proof must verify against the current root.
    function claimWithProof(bytes32[] calldata proof, uint256 amount) external view returns (bool) {
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, amount));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "bad proof");
        return true;
    }

    /// @notice Privileged: rotate the Merkle root that gates claims.
    function setMerkleRoot(bytes32 root_) external onlyOwner {
        merkleRoot = root_;
    }
}
