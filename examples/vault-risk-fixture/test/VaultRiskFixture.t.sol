// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/VaultRiskFixture.sol";

contract MockAsset is IERC20 {
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

contract MockFeed is IPriceFeed {
    function latestRoundData() external pure returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) {
        return (1, 1e8, 1, 1, 1);
    }
}

contract VaultRiskFixtureTest is Test {
    MockAsset internal asset;
    MockFeed internal feed;
    VaultRiskFixture internal vault;
    address internal alice = address(0xA11CE);
    address internal treasury = address(0xBEEF);

    function setUp() public {
        asset = new MockAsset();
        feed = new MockFeed();
        vault = new VaultRiskFixture(asset, treasury, feed);
        asset.mint(alice, 100 ether);

        vm.prank(alice);
        asset.approve(address(vault), type(uint256).max);
    }

    function testDepositUpdatesSharesAndAssets() public {
        vm.prank(alice);
        uint256 shares = vault.deposit(10 ether, alice);

        assertEq(shares, 10 ether);
        assertEq(vault.totalAssets(), 10 ether);
        assertEq(vault.balanceOf(alice), 10 ether);
    }

    function testWithdrawReturnsAssets() public {
        vm.startPrank(alice);
        vault.deposit(10 ether, alice);
        uint256 shares = vault.withdraw(5 ether, alice, alice);
        vm.stopPrank();

        assertEq(shares, 5 ether);
        assertEq(vault.balanceOf(alice), 5 ether);
    }
}
