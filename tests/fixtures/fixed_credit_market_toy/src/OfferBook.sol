// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Synthetic offer book for Arkheionx fixture tests. Not real-protocol source. Models
// settlement-time liquidity: makers post signed offer intent with a group budget;
// no maker capital is locked until settlement. Illustrative only.

interface ISettlementCallback {
    function onSettle(bytes32 offerId, uint256 assets, uint256 units, bytes calldata data) external;
}

contract OfferBook {
    struct Offer {
        address maker;
        bool buy;
        uint256 market;
        int256 tick;
        uint256 price;
        uint256 start;
        uint256 expiry;
        uint256 maxAssets;
        uint256 maxUnits;
        uint256 group;
        address ratifier;
        bool reduceOnly;
    }

    // maker => group => consumed budget across offers and markets
    mapping(address => mapping(uint256 => uint256)) public consumed;
    mapping(bytes32 => bool) public usedOffer;

    function offerId(Offer calldata o) public pure returns (bytes32) {
        return keccak256(abi.encode(o.maker, o.market, o.tick, o.price, o.start, o.expiry, o.group));
    }

    function settle(
        Offer calldata offer,
        address taker,
        uint256 assets,
        uint256 units,
        address receiver,
        bytes calldata ratifierData,
        address callback,
        bytes calldata callbackData
    ) external {
        require(block.timestamp >= offer.start && block.timestamp < offer.expiry, "window");
        require(assets <= offer.maxAssets, "maxAssets");
        require(units <= offer.maxUnits, "maxUnits");

        bytes32 id = offerId(offer);
        // Group exposure cap across offers and markets for this maker.
        consumed[offer.maker][offer.group] += assets;

        if (offer.ratifier != address(0)) {
            require(_ratify(offer, ratifierData), "ratifier");
        }

        // Settlement-time liquidity: payment must back the state change.
        // (Illustrative: a real implementation pulls funds before finalizing.)
        if (callback != address(0)) {
            ISettlementCallback(callback).onSettle(id, assets, units, callbackData);
        }

        require(_paid(taker, receiver, assets), "payment");
        usedOffer[id] = true;
    }

    function _ratify(Offer calldata, bytes calldata) internal pure returns (bool) {
        return true; // placeholder ratification check
    }

    function _paid(address, address, uint256) internal pure returns (bool) {
        return true; // placeholder payment check
    }
}
