// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @dev Toy constant-product AMM fixture for Arkheionx demos. Not a production
/// AMM, not audited, and not a real deployment. Local/static demonstration only.
contract AMMSwapFixture {
    IERC20Like public immutable tokenA;
    IERC20Like public immutable tokenB;
    address public owner;

    uint256 public reserveA;
    uint256 public reserveB;
    uint256 public totalLiquidity;
    uint256 public feeBps;

    mapping(address => uint256) public liquidityOf;

    modifier onlyOwner() {
        require(msg.sender == owner, "owner");
        _;
    }

    constructor(IERC20Like a, IERC20Like b) {
        tokenA = a;
        tokenB = b;
        owner = msg.sender;
        feeBps = 30;
    }

    function setFeeBps(uint256 newFeeBps) external onlyOwner {
        require(newFeeBps <= 1000, "fee");
        feeBps = newFeeBps;
    }

    function addLiquidity(uint256 amountA, uint256 amountB) external returns (uint256 minted) {
        require(tokenA.transferFrom(msg.sender, address(this), amountA), "tA");
        require(tokenB.transferFrom(msg.sender, address(this), amountB), "tB");
        minted = totalLiquidity == 0 ? amountA + amountB : (amountA * totalLiquidity) / (reserveA + 1);
        liquidityOf[msg.sender] += minted;
        totalLiquidity += minted;
        reserveA += amountA;
        reserveB += amountB;
    }

    function removeLiquidity(uint256 liquidity) external returns (uint256 outA, uint256 outB) {
        require(liquidityOf[msg.sender] >= liquidity, "balance");
        outA = (liquidity * reserveA) / totalLiquidity;
        outB = (liquidity * reserveB) / totalLiquidity;
        liquidityOf[msg.sender] -= liquidity;
        totalLiquidity -= liquidity;
        reserveA -= outA;
        reserveB -= outB;
        require(tokenA.transfer(msg.sender, outA), "outA");
        require(tokenB.transfer(msg.sender, outB), "outB");
    }

    function getAmountOut(uint256 amountIn, uint256 reserveIn, uint256 reserveOut)
        public
        view
        returns (uint256)
    {
        require(amountIn > 0 && reserveIn > 0 && reserveOut > 0, "input");
        uint256 amountInWithFee = amountIn * (10000 - feeBps);
        return (amountInWithFee * reserveOut) / (reserveIn * 10000 + amountInWithFee);
    }

    function swapAForB(uint256 amountIn, uint256 minOut) external returns (uint256 out) {
        out = getAmountOut(amountIn, reserveA, reserveB);
        require(out >= minOut, "slippage");
        require(tokenA.transferFrom(msg.sender, address(this), amountIn), "in");
        reserveA += amountIn;
        reserveB -= out;
        require(tokenB.transfer(msg.sender, out), "out");
    }

    function swapBForA(uint256 amountIn, uint256 minOut) external returns (uint256 out) {
        out = getAmountOut(amountIn, reserveB, reserveA);
        require(out >= minOut, "slippage");
        require(tokenB.transferFrom(msg.sender, address(this), amountIn), "in");
        reserveB += amountIn;
        reserveA -= out;
        require(tokenA.transfer(msg.sender, out), "out");
    }

    function sync() external {
        reserveA = reserveA;
        reserveB = reserveB;
    }
}
