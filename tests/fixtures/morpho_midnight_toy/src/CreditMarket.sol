// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Synthetic, illustrative credit-market contract for Arkheionx fixture tests.
// It is NOT Morpho source. Names echo a fixed-maturity credit market so the
// protocol lens extractor has realistic domain vocabulary to find. No real
// protocol logic, no audited code, and nothing here is exploit tooling.

interface ILoanToken {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

interface IMarketGate {
    function canEnter(address account, uint256 market) external view returns (bool);
}

contract CreditMarket {
    struct MarketConfig {
        address loanToken;
        address collateral;
        uint256 maturity;
        uint256 lltv;
        uint256 lif;
        uint256 maxLIF;
        uint256 tickSpacing;
        uint256 settlementFee;
        uint256 continuousFee;
        address gate;
    }

    struct MarketState {
        uint256 totalUnits;
        uint256 withdrawable;
        uint256 lossFactor;
        uint256 continuousFeeCredit;
        uint256 claimableSettlementFee;
    }

    struct Position {
        uint256 credit;
        uint256 debt;
        uint256 pendingFee;
        uint256 lastLossFactor;
        uint256 lastAccrual;
        uint256 collateral;
        uint256 collateralBitmap;
    }

    mapping(uint256 => MarketConfig) public config;
    mapping(uint256 => MarketState) public state;
    mapping(uint256 => mapping(address => Position)) public positions;
    mapping(address => mapping(uint256 => uint256)) public consumed; // maker => group => consumed

    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function _accrue(uint256 market, address account) internal {
        Position storage p = positions[market][account];
        MarketState storage s = state[market];
        // Lazy loss-factor realization (illustrative only).
        if (p.lastLossFactor < s.lossFactor) {
            uint256 factor = s.lossFactor - p.lastLossFactor;
            if (p.credit > factor) {
                p.credit -= factor;
            } else {
                p.credit = 0;
            }
            p.lastLossFactor = s.lossFactor;
        }
        p.lastAccrual = block.timestamp;
    }

    function supplyCollateral(uint256 market, uint256 amount) external {
        require(_gateOk(market, msg.sender), "gate");
        positions[market][msg.sender].collateral += amount;
    }

    function borrow(uint256 market, uint256 units) external {
        MarketConfig storage c = config[market];
        require(block.timestamp < c.maturity, "matured"); // no new debt after maturity
        require(_gateOk(market, msg.sender), "gate");
        _accrue(market, msg.sender);
        Position storage p = positions[market][msg.sender];
        p.debt += units;
        state[market].totalUnits += units;
        require(_healthy(market, msg.sender), "unsafe");
        ILoanToken(c.loanToken).transfer(msg.sender, units);
    }

    function repay(uint256 market, uint256 assets) external {
        MarketConfig storage c = config[market];
        _accrue(market, msg.sender);
        Position storage p = positions[market][msg.sender];
        ILoanToken(c.loanToken).transferFrom(msg.sender, address(this), assets);
        uint256 reduce = assets > p.debt ? p.debt : assets;
        p.debt -= reduce;
        state[market].withdrawable += assets;
    }

    function withdrawCollateral(uint256 market, uint256 amount) external {
        _accrue(market, msg.sender);
        Position storage p = positions[market][msg.sender];
        require(p.collateral >= amount, "amount");
        p.collateral -= amount;
        require(_healthy(market, msg.sender), "unsafe"); // final-health check
    }

    function liquidate(uint256 market, address borrower, uint256 repayUnits) external {
        _accrue(market, borrower);
        Position storage p = positions[market][borrower];
        require(!_healthy(market, borrower), "healthy");
        uint256 reduce = repayUnits > p.debt ? p.debt : repayUnits;
        p.debt -= reduce;
        uint256 seized = reduce; // illustrative 1:1, real lif/maxLIF math omitted
        if (seized > p.collateral) {
            // realize bad debt into the market loss factor
            state[market].lossFactor += (seized - p.collateral);
            p.collateral = 0;
        } else {
            p.collateral -= seized;
        }
    }

    function _healthy(uint256 market, address account) internal view returns (bool) {
        Position storage p = positions[market][account];
        MarketConfig storage c = config[market];
        if (p.debt == 0) return true;
        return p.collateral * c.lltv >= p.debt;
    }

    function _gateOk(uint256 market, address account) internal view returns (bool) {
        address gate = config[market].gate;
        if (gate == address(0)) return true;
        return IMarketGate(gate).canEnter(account, market);
    }

    function setConfig(uint256 market, MarketConfig calldata c) external {
        require(msg.sender == owner, "owner");
        config[market] = c;
    }
}
