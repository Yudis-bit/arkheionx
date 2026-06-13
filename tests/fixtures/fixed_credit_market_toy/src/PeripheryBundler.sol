// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Synthetic periphery bundler for Arkheionx fixture tests. Not real-protocol source.
// Models target-based bundle composition over a credit market: repay, collateral
// moves, and settlement to a target in assets or units, with caps and a referral
// fee. Illustrative only; cap/target dimensions are deliberately simple.

interface ICreditMarketLike {
    function repay(uint256 market, uint256 assets) external;
    function withdrawCollateral(uint256 market, uint256 amount) external;
    function supplyCollateral(uint256 market, uint256 amount) external;
}

contract PeripheryBundler {
    struct BundleParams {
        uint256 market;
        uint256 targetAssets;
        uint256 targetUnits;
        uint256 maxAssets;
        uint256 maxUnits;
        address receiver;
        address referral;
        uint256 fee;
        bool skipOnRevert;
    }

    ICreditMarketLike public market;

    constructor(address market_) {
        market = ICreditMarketLike(market_);
    }

    // Compose a bundle toward a target. Illustrative target accounting.
    function bundle(BundleParams calldata p, uint256 repayAssets, uint256 withdrawCollateralAmount) external {
        require(repayAssets <= p.maxAssets, "maxAssets");

        if (repayAssets > 0) {
            market.repay(p.market, repayAssets);
        }

        // Target completion check (illustrative: measured in assets here).
        uint256 progressed = repayAssets;
        bool targetMet = progressed >= p.targetAssets;

        if (withdrawCollateralAmount > 0) {
            // Collateral movement after the composed step.
            if (!targetMet && p.skipOnRevert) {
                return; // skip
            }
            market.withdrawCollateral(p.market, withdrawCollateralAmount);
        }

        if (p.fee > 0 && p.referral != address(0)) {
            // referral fee accounting (illustrative)
        }
    }
}
