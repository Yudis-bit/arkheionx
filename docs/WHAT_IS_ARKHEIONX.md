# What ArkheionX Is

ArkheionX is local-first review infrastructure for smart contract security.

It turns a Solidity or Foundry repository into deterministic review context: value paths, roles, trust assumptions, reachable flows, missing tests, evidence, and unresolved review gaps.

It does not replace auditors. It gives auditors a better map.

## Core idea

Security review is not only asking whether existing tests pass. A reviewer needs to know what value can move, who can move it, what assumptions protect it, and which paths have weak or missing evidence.

ArkheionX organizes that context before final report writing.

## What ArkheionX helps map

- Value paths: where assets enter, move, and exit.
- Roles: owners, admins, keepers, distributors, guardians, routers, and privileged dependencies.
- Trust assumptions: oracle freshness, access control, share accounting, trusted roles, dependency behavior, paused states, and external integrations.
- Reachable flows: contract/function paths that deserve human attention.
- Missing tests: value-sensitive paths that appear weakly covered or uncovered.
- Evidence gaps: hypotheses that still need local proof or rejection.
- Review questions: unresolved items that should stay visible until a human closes them.

## What makes it local-first

Default ArkheionX workflows operate on local repository files and generated local artifacts.

The default workflow does not need:

- private keys;
- RPC URLs;
- live-chain calls;
- production credentials;
- external AI APIs;
- transaction broadcasting.

## How it fits with Foundry

Foundry tells reviewers whether the tests they wrote pass.

ArkheionX helps show what they may have forgotten to test.

The two tools are complementary. ArkheionX can point at a value path or missing evidence area; a reviewer still writes and runs the local test, interprets the result, and decides whether anything is reportable.

## Who should use it

- Security researchers preparing a focused review pass.
- Protocol teams preparing for an audit or contest.
- Audit teams that want a deterministic context pack before manual review.
- Maintainers who want repeatable review artifacts for internal security work.

## Current maturity

ArkheionX has a serious local review workflow, but it should not be treated as a mature replacement for external review.

The next credibility step is not random feature expansion. It is real-world usage on established DeFi protocols, external reviewer feedback, and case studies showing what the tool clarified during actual review work.

See [`EXTERNAL_VALIDATION.md`](EXTERNAL_VALIDATION.md), [`CASE_STUDIES.md`](CASE_STUDIES.md), and [`ROADMAP.md`](ROADMAP.md).
