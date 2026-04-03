# DeFi-Exploit-PoCs

Deterministic Proof-of-Concept exploits for high-severity DeFi vulnerabilities.

Maintained by **Arkheionx** ([@Yudis-bit](https://github.com/Yudis-bit)).

---

## ☢️ Vulnerability Registry

| ID | Date | Protocol | Vulnerability Vector | Severity | PoC |
|----|------|----------|---------------------|----------|-----|
| 01 | 2022-10 | Illuminate / APWine | DoS via 1 wei Donation | 🔴 High | [`test/2022-10-Illuminate.t.sol`](./test/2022-10-Illuminate.t.sol) |
| 02 | 2023-03 | Euler Finance | Logic Error (Donation) | 🔴 Critical | [`test/2023-03-EulerFinance.t.sol`](./test/2023-03-EulerFinance.t.sol) |

---

## 🛠️ Environment

```
Foundry (Forge)
Solidity ^0.8.x
Ethereum Mainnet Fork
```

### Dependencies

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

---

## Execution

### Run All Exploits

```bash
forge test --fork-url $ETH_RPC_URL -vvvv
```

### Run Single Exploit

```bash
forge test \
  --fork-url $ETH_RPC_URL \
  --match-path test/2022-10-Illuminate.t.sol \
  -vvvv
```

Replace `$ETH_RPC_URL` with an archival RPC endpoint (Alchemy, Infura, or local node). Forked block numbers are pinned inside each test file.

---

## The Arkheionx Standard

Every PoC in this repository is constructed under a fixed methodology. No exceptions.

### 1. Isolation

- One exploit per file. Zero shared state across tests.
- Each file is a self-contained reproduction: fork block, target contracts, attacker setup, and exploit sequence.

### 2. Deterministic Verification

- Every exploit terminates with hard assertions — not console output, not events, not "it looks right."
- `assertEq`, `assertGt`, `assertLt` against concrete post-exploit state.
- Passing test = confirmed vulnerability. Failing test = broken invariant assumption.

### 3. Call Trace Transparency

- All tests are designed for `-vvvv` inspection.
- Full call traces expose: calldata manipulation, state transitions, storage collisions, and internal delegatecall paths.
- If the trace doesn't make the vulnerability obvious, the PoC is rewritten.

### 4. Mainnet Forking

- Every exploit forks mainnet at a pinned block number documented in the test file header.
- No mocks. No simulated contracts. Real deployed bytecode, real storage slots, real state.

---

## File Naming Convention

```
test/YYYY-MM-ProtocolName.t.sol
```

| Component | Rule |
|-----------|------|
| `YYYY-MM` | Disclosure or discovery date |
| `ProtocolName` | PascalCase, canonical protocol name |
| `.t.sol` | Foundry test file suffix |

Examples:

```
test/2022-10-Illuminate.t.sol
test/2023-03-EulerFinance.t.sol
test/2024-01-SomeProtocol.t.sol
```

---

## PoC File Structure

Each `.t.sol` file follows this layout:

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.x;

import "forge-std/Test.sol";

/*
 * VULNERABILITY: [Short title]
 * PROTOCOL:      [Name]
 * SEVERITY:      [Critical | High | Medium]
 * FORK BLOCK:    [Block number]
 * DESCRIPTION:   [1-2 sentences. State transition exploited, invariant broken.]
 */

contract Exploit_YYYY_MM_ProtocolName is Test {

    // --- Target Contracts ---

    // --- Constants ---

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        // Contract bindings, attacker setup, initial state
    }

    function test_exploit() public {
        // Pre-exploit state snapshot
        // Attack sequence
        // Post-exploit assertions (deterministic)
    }
}
```

---

## Severity Classification

| Level | Definition |
|-------|-----------|
| 🔴 Critical | Direct, unconditional loss of funds or protocol takeover |
| 🔴 High | Loss of funds under specific but realistic conditions, or permanent DoS of core functionality |
| 🟡 Medium | Conditional fund risk, governance manipulation, or reversible DoS |

---

## Disclaimer

All exploits target vulnerabilities that have been publicly disclosed, patched, or are part of sanctioned audit/bounty programs. This repository exists for defensive research and auditor training. Reproducing these exploits against live, unpatched contracts is illegal and unethical.

---

## Contact

**Arkheionx** — [GitHub](https://github.com/Yudis-bit)
