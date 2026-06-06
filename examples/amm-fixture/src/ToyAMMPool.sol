// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract ToyAMMPool {
    IERC20Like public immutable token0;
    IERC20Like public immutable token1;

    uint256 public reserve0;
    uint256 public reserve1;
    uint256 public kLast;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    constructor(IERC20Like token0_, IERC20Like token1_) {
        token0 = token0_;
        token1 = token1_;
    }

    function getReserves() external view returns (uint256, uint256) {
        return (reserve0, reserve1);
    }

    function addLiquidity(uint256 amount0, uint256 amount1) external returns (uint256 shares) {
        token0.transferFrom(msg.sender, address(this), amount0);
        token1.transferFrom(msg.sender, address(this), amount1);

        if (totalSupply == 0) {
            shares = amount0 + amount1;
        } else {
            uint256 share0 = amount0 * totalSupply / reserve0;
            uint256 share1 = amount1 * totalSupply / reserve1;
            shares = share0 < share1 ? share0 : share1;
        }

        reserve0 += amount0;
        reserve1 += amount1;
        totalSupply += shares;
        balanceOf[msg.sender] += shares;
        kLast = reserve0 * reserve1;
    }

    function removeLiquidity(uint256 shares) external returns (uint256 amount0, uint256 amount1) {
        require(balanceOf[msg.sender] >= shares, "SHARES");
        amount0 = shares * reserve0 / totalSupply;
        amount1 = shares * reserve1 / totalSupply;
        balanceOf[msg.sender] -= shares;
        totalSupply -= shares;
        reserve0 -= amount0;
        reserve1 -= amount1;
        kLast = reserve0 * reserve1;
        token0.transfer(msg.sender, amount0);
        token1.transfer(msg.sender, amount1);
    }

    function getAmountOut(uint256 amountIn, bool zeroForOne) public view returns (uint256) {
        uint256 inputReserve = zeroForOne ? reserve0 : reserve1;
        uint256 outputReserve = zeroForOne ? reserve1 : reserve0;
        uint256 amountInWithFee = amountIn * 997;
        return amountInWithFee * outputReserve / (inputReserve * 1000 + amountInWithFee);
    }

    function swap(uint256 amountIn, bool zeroForOne) external returns (uint256 amountOut) {
        amountOut = getAmountOut(amountIn, zeroForOne);
        if (zeroForOne) {
            token0.transferFrom(msg.sender, address(this), amountIn);
            token1.transfer(msg.sender, amountOut);
            reserve0 += amountIn;
            reserve1 -= amountOut;
        } else {
            token1.transferFrom(msg.sender, address(this), amountIn);
            token0.transfer(msg.sender, amountOut);
            reserve1 += amountIn;
            reserve0 -= amountOut;
        }
        kLast = reserve0 * reserve1;
    }
}

