# Analysis: Illuminate PT Redemption DoS

### Vulnerability
The contract uses `pt.balanceOf(address(this))` directly to validate redemptions. This state is manipulatable via direct ERC20 transfers (donations).

### Attack Flow
1. Attacker sends 1 wei PT directly to the Redeemer.
2. `pt.balanceOf(address(this))` > `fyt.balanceOf(address(this))`.
3. `redeem()` invariably fails, locking all user funds.

### Proof of Concept
\`\`\`bash
forge test --match-contract IlluminateAPWineDoSPoC -vvvv
\`\`\`
