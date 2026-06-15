# V10.1 Reality Engine Upgrade Plan

## Baseline

- Branch: `private/v10-godeye-war-engine`
- Base commit: `210905a2e3b5e52791be2d78c84da0daad15a502`
- Dirty files at start: V10.1 source, test, fixture, and note files were already
  present as uncommitted work. They were treated as existing work-in-progress
  and stabilized in place.
- Test command requested: `python -m pytest -q`
- Test status: blocked by environment because `python` is unavailable
- Alternate test command: `python3 -m pytest -q`
- Alternate test status: blocked by environment because `pytest` is not installed
- Temporary test environment: `/tmp/arkheionx-v10-test-venv`
- Baseline full-suite status before compatibility fixes:
  `2 failed, 2932 passed, 7 skipped, 6 errors, 112 subtests passed`
- Current full-suite status after compatibility fixes:
  `2934 passed, 7 skipped, 112 subtests passed`

## Planned Changes

1. Add semantic root-cause normalization, family classification, deterministic
   fingerprinting, and backward-compatible memory persistence.
2. Add a bounty reality model and gate that separates code validity from
   submission relevance.
3. Add framework detection, configurable Solidity discovery, explicit exclusion
   accounting, and zero-contract warnings.
4. Add safe compiler artifact and build-info discovery that enriches source
   parsing without making artifacts mandatory.
5. Add authorization analysis for signed-operation binding, replay domains,
   threshold checks, delegated execution, and factory initialization.
6. Integrate ingestion, authorization, memory, reality verdicts, and new quality
   gates into `war-run`.
7. Add generic fixtures, targeted regression tests, command-line smoke tests,
   and technical documentation.
8. Create local commits only after coherent test-passing milestones.

## Risks

- Regex-based fallback analysis can infer likely bindings but cannot replace a
  compiler AST for all Solidity syntax.
- Existing candidate families use older names; compatibility aliases are needed
  so stored memory and severity behavior remain stable.
- Artifact formats vary. Malformed or partial JSON must reduce confidence rather
  than terminate analysis.
- Reality-gate inputs are often incomplete. Missing economic facts must produce
  `NEEDS_MORE_PROOF` or `HUMAN_REVIEW_REQUIRED`, not an unsupported submit label.
- Existing tests may rely on current artifact names and console text. New output
  must be additive where possible.

## Acceptance Criteria

- Every new memory entry has a non-empty family and semantic fingerprint hash.
- Known generic root-cause examples classify into the required families.
- Previously rejected, duplicate, dust-only, no-profit, opt-in, trusted-role,
  off-chain validation, key-reuse, forced-transfer-only, gas-only, and policy
  carve-out cases cannot retain a submit label.
- Solidity repositories with common and generic layouts index contracts without
  requiring the default source directory.
- A zero-contract run emits an explicit warning and quality-gate result.
- Artifact ingestion safely enriches source analysis and always retains fallback
  parsing.
- Authorization analysis distinguishes dangerous unbound execution fields and
  threshold bypasses from key-reuse-only replay and non-bypass malleability.
- `war-run` emits ingestion, bounty reality, and authorization artifacts.
- Targeted tests, full available tests, and generic command-line smoke tests pass.
- No network, RPC, transaction, signing, website, release, tag, or push action is
  performed.
