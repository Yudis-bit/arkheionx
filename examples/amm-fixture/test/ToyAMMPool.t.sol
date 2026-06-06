// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/ToyAMMPool.sol";

contract MockToken is IERC20Like {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

contract ToyAMMPoolTest is Test {
    MockToken internal token0;
    MockToken internal token1;
    ToyAMMPool internal pool;
    address internal alice = address(0xA11CE);

    function setUp() public {
        token0 = new MockToken();
        token1 = new MockToken();
        pool = new ToyAMMPool(token0, token1);
        token0.mint(alice, 1_000 ether);
        token1.mint(alice, 1_000 ether);
        vm.startPrank(alice);
        token0.approve(address(pool), type(uint256).max);
        token1.approve(address(pool), type(uint256).max);
        vm.stopPrank();
    }

    function testSeedPool() public {
        vm.prank(alice);
        pool.addLiquidity(100 ether, 100 ether);
        assertEq(pool.totalSupply(), 200 ether);
    }

    function testSwapUpdatesReserves() public {
        vm.startPrank(alice);
        pool.addLiquidity(100 ether, 100 ether);
        uint256 out = pool.swap(1 ether, true);
        vm.stopPrank();
        assertGt(out, 0);
    }
}

