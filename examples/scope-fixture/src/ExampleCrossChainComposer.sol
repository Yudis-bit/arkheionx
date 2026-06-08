// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ExampleComplianceList} from "./ExampleComplianceList.sol";

/// @title ExampleCrossChainComposer (synthetic)
/// @notice Generic cross-chain send/compose with refund + quarantine. Demo only.
contract ExampleCrossChainComposer {
    address public endpoint;
    ExampleComplianceList public compliance;

    struct Message {
        address to;
        uint256 amount;
        bool delivered;
        bool refunded;
        bool quarantined;
    }

    uint256 public nextNonce;
    mapping(uint256 => Message) public outbound;

    error NotEndpoint();
    error Blocked(address who);
    error AlreadyResolved();

    event Sent(uint256 indexed nonce, address indexed to, uint256 amount);
    event Delivered(uint256 indexed nonce);
    event Refunded(uint256 indexed nonce);
    event Quarantined(uint256 indexed nonce);

    modifier onlyEndpoint() {
        if (msg.sender != endpoint) revert NotEndpoint();
        _;
    }

    constructor(address endpoint_, address compliance_) {
        endpoint = endpoint_;
        compliance = ExampleComplianceList(compliance_);
    }

    /// @notice Initiate a cross-chain transfer. Compliance gate applies.
    function send(address to, uint256 amount) external returns (uint256 nonce) {
        if (compliance.isBlocked(to)) revert Blocked(to);
        nonce = nextNonce++;
        outbound[nonce] = Message(to, amount, false, false, false);
        emit Sent(nonce, to, amount);
    }

    /// @notice Endpoint confirms delivery on the destination chain.
    function lzReceive(uint256 nonce) external onlyEndpoint {
        Message storage m = outbound[nonce];
        if (m.delivered || m.refunded || m.quarantined) revert AlreadyResolved();
        m.delivered = true;
        emit Delivered(nonce);
    }

    /// @notice Refund a failed delivery (single resolution).
    function refund(uint256 nonce) external onlyEndpoint {
        Message storage m = outbound[nonce];
        if (m.delivered || m.refunded || m.quarantined) revert AlreadyResolved();
        m.refunded = true;
        emit Refunded(nonce);
    }

    /// @notice Quarantine a message that fails compliance on arrival.
    function quarantine(uint256 nonce) external onlyEndpoint {
        Message storage m = outbound[nonce];
        if (m.delivered || m.refunded || m.quarantined) revert AlreadyResolved();
        m.quarantined = true;
        emit Quarantined(nonce);
    }
}
