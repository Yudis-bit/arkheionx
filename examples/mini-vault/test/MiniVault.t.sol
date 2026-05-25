// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/MiniVault.sol";

contract MockToken is IERC20 {
    string public name = "Mock Asset";
    string public symbol = "MOCK";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "BALANCE");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "BALANCE");
        require(allowance[from][msg.sender] >= amount, "ALLOWANCE");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

contract MiniVaultTest is Test {
    MockToken internal asset;
    MiniVault internal vault;
    address internal alice = address(0xA11CE);
    address internal treasury = address(0xBEEF);

    function setUp() public {
        asset = new MockToken();
        vault = new MiniVault(asset, treasury);
        asset.mint(alice, 100 ether);

        vm.prank(alice);
        asset.approve(address(vault), type(uint256).max);
    }

    function testDepositMintsShares() public {
        vm.prank(alice);
        uint256 shares = vault.deposit(10 ether, alice);

        assertEq(shares, 10 ether);
        assertEq(vault.balanceOf(alice), 10 ether);
        assertEq(vault.totalAssets(), 10 ether);
    }

    function testOwnerCanPause() public {
        vault.pause();

        assertTrue(vault.paused());
    }

    function testNonOwnerCannotSetFee() public {
        vm.prank(alice);
        vm.expectRevert("NOT_OWNER");
        vault.setFee(100);
    }
}
