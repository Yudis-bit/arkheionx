// SPDX-License-Identifier: MIT OR Apache-2.0
pragma solidity ^0.8.20;

import {TestBase} from "../../src/Test.sol";

// The purpose of this contract is to benchmark compilation time to avoid accidentally introducing
// a change that results in very long compilation times with via-ir. See https://github.com/foundry-rs/forge-std/issues/207
contract CompilationTestBase is TestBase {}
