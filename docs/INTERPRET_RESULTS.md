# How to interpret ArkheionX results

ArkheionX output is **review guidance for a human**, not a verdict. This page
explains what each part of a review map means — and what it does not mean.

## The mental model

ArkheionX reads your local Solidity/Foundry source statically and organizes it
into a review map. Everything it produces is a prioritization and orientation
aid. It does not execute your contracts, call any chain, or confirm that a bug
exists.

## What each section means

- **Inspect first / review priority.** A ranked order of where to look first.
  Priority is *review order*, not severity. A HIGH item is not a finding; it is
  a function whose value behavior deserves early human attention.

- **Value paths.** Static, heuristic routes for how value enters, moves, and
  exits a contract (for example `deposit -> withdraw`). They are derived from
  function names and token-transfer calls, so they are a starting map, not a
  proven execution trace.

- **Assumptions.** Trust conditions a value path appears to depend on (oracle
  freshness, access control, share proportionality, no reentrancy, standard
  ERC20 behavior). These are prompts for a reviewer to confirm — they are
  unverified by definition.

- **Test gaps.** A value-sensitive function with no matching local test
  reference, or only an incidental one. A gap means *observed test coverage
  looks missing or weak*. It does **not** mean the function is exploitable, and
  the absence of a gap does not mean the function is safe. Each gap prints a
  `Source: <file>:<line>` reference so you can open the exact function; the line
  comes from the parsed source, not an invented number.

- **Proof suggestions / proof plans.** Local Foundry test *scaffolds* you can
  fill in. A scaffold is a starting point with `TODO`s and `vm.skip`; it is not
  a proof, and ArkheionX never asserts a test passed when it did not.

- **Coverage hints (`referenced` / `none`).** A weak heuristic: does the
  function name appear in a test file? `none` is a prompt to add a targeted
  test, not a measurement of branch coverage.

## How to use it

1. Run `arkheionx review-map .` and read the **Inspect first** list.
2. For each high-priority value exit, open the **value path** and its
   **assumptions**. Ask: is each assumption actually enforced in code?
3. Check the **test gaps**: is there a test that exercises this value path under
   adversarial conditions? If not, write one.
4. Optionally scaffold a local proof with `arkheionx prove . --target <T> --run`
   and review the result yourself.

## Research memory outputs (v4.1)

Three commands build on the review map for AI-assisted review. They are review
guidance, not findings:

- **Agent brief (`agent-brief`).** A focused, safe brief for an AI/security
  agent: repository summary, coverage weakness ranking, value movement,
  authorization surfaces, periphery/core surfaces, behavior-mismatch surfaces,
  and a set of `open` hypotheses. It replaces a vague "find bugs" prompt; it does
  not claim any bug.
- **Hypothesis log (`hypothesis-log`).** A tracker where every hypothesis starts
  `open`. A human (or an agent under human review) records the test command,
  result, and a `rejected` / `confirmed` / `needs-human-review` status after a
  local test. A **rejected** hypothesis is useful evidence: it means a tested
  invariant or behavior held.
- **Case study (`case-study`).** A sanitized research-session summary: what was
  tested, what was rejected, what held, what was noisy, and what remains
  unresolved. It is not an audit report and makes no vulnerability claim unless a
  finding is independently confirmed.

Authorization, periphery/core, and behavior-mismatch surfaces are **heuristic
review prompts** detected statically from names, signatures, and code patterns.
"Potential behavior-mismatch review surface" means *look here*, never *bug here*.

See [`V4_1_RESEARCH_WORKFLOW.md`](V4_1_RESEARCH_WORKFLOW.md) and
[`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md).

## What it does not tell you

ArkheionX does not assign final severity, does not confirm or rule out
vulnerabilities, and does not prove safety. Treat its output as a structured
second opinion that helps you spend review time where value moves. The security
judgment is always yours.

See also: [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md) and
[`REVIEW_MAP.md`](REVIEW_MAP.md).
