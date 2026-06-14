// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: a lending market computes collateral value from an
// oracle price but hardcodes 1e18 scaling and ignores the feed's `decimals()` and
// the token's `decimals()`. When the feed reports, say, 8 decimals, the computed
// borrow limit is off by orders of magnitude, letting an unprivileged borrower
// borrow far beyond the safe value of their collateral. No protocol/token name is
// encoded; this is a generic decimal-normalization shape.

interface IERC20 {
    function balanceOf(address who) external view returns (uint256);
    function decimals() external view returns (uint8);
}

contract PriceOracle {
    int256 public answer;
    uint8 public oracleDecimals; // e.g. 8 for a Chainlink-style USD feed
    uint256 public updatedAt;

    function setAnswer(int256 a, uint8 dec) external {
        answer = a;
        oracleDecimals = dec;
        updatedAt = block.timestamp;
    }

    function latestRoundData()
        external
        view
        returns (uint80, int256, uint256, uint256, uint80)
    {
        return (1, answer, updatedAt, updatedAt, 1);
    }

    function decimals() external view returns (uint8) {
        return oracleDecimals;
    }
}

contract CollateralToken {
    uint8 public tokenDecimals; // e.g. 18
    mapping(address => uint256) public balanceOf;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function decimals() external view returns (uint8) {
        return tokenDecimals;
    }
}

contract OracleLoanMarket {
    CollateralToken public collateral;
    PriceOracle public oracle;
    mapping(address => uint256) public debt;

    function maxBorrow(address user) public view returns (uint256) {
        (, int256 price,,,) = oracle.latestRoundData();
        uint256 bal = collateral.balanceOf(user);
        // BUG: assumes `price` is already scaled to 1e18 and ignores both the feed's
        // decimals() and the token's decimals(). The borrow limit is mis-scaled.
        return (bal * uint256(price)) / 1e18;
    }

    function borrow(uint256 amount) external {
        require(amount <= maxBorrow(msg.sender), "exceeds max");
        debt[msg.sender] += amount;
    }
}
