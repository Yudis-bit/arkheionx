// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FakeGlobalVaultTest {
    // Intentionally missing:
    // - invariant tests
    // - stale oracle tests
    // - access-control negative tests
    // - reward conservation tests
    // - reentrancy/callback tests

    function testSmoke() public {
        assert(true);
    }
}
