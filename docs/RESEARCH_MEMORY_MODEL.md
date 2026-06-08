# Research Memory Model (v4.1)

> Local/static review guidance only. Not confirmed vulnerabilities. Human review
> required. Research memory does not assign severity and is not an audit.

ArkheionX v4.0 stabilized one workflow:

```text
repo → review-map → value paths → assumptions → test gaps → proof direction → human review
```

v4.1 extends that workflow into a **research memory** layer for AI-assisted
review:

```text
repo → review-map → agent brief → hypotheses → Foundry/manual tests
     → rejected/confirmed evidence → case study → human decision
```

The product line for v4.1:

> ArkheionX gives the map. The agent grinds the tests. The research memory keeps
> the evidence. The human makes the final call.

## 1. Why research memory exists

Security review is not only a list of confirmed findings. Most of the work in a
real bug bounty or pre-audit session is *deciding what to test, testing it, and
recording what held*.

- **Security research is mostly negative space.** For every confirmed issue,
  many plausible ideas are tested and rejected. A rejected idea means a tested
  invariant or behavior held under the attempted conditions. That is evidence,
  not wasted work.
- **AI-assisted review becomes noisy without a map.** A vague prompt such as
  "find bugs in this repo" produces unfocused output. A structured brief —
  value paths, accounting mutations, authorization surfaces, periphery/core
  flows, weakly covered paths — keeps an agent grinding on the surfaces that
  actually move value.
- **ArkheionX should preserve what was tested.** What looked dangerous, why it
  looked dangerous, what was tested, what held, what failed, what was rejected,
  what remains unresolved, and what deserves the next review pass. Without that
  memory, the next reviewer repeats work and may waste effort on a path someone
  already cleared.

Research memory is the structured record of that process. It is review context,
not a security judgment.

## 2. Core objects

### A. Surface

A protocol area worth review. ArkheionX derives surfaces statically and labels
each as heuristic. Surface kinds:

- accounting surface (debt / credit / share / collateral mutation)
- value-exit surface (value can leave the system)
- liquidation surface (health-factor / solvency / seizure paths)
- authorization surface (signature, Merkle, role, gate, ratifier, nonce, domain)
- oracle surface (price / staleness / decimals dependence)
- periphery surface (router / bundle / multicall / adapter / callback)
- callback / external-call surface (cross-contract calls, low-level calls)
- admin / control surface (privileged setters that steer value or trust)

A surface carries a **risk signal** (why it matters) and a **coverage signal**
(what local test evidence exists). Both are heuristic.

### B. Hypothesis

A testable idea generated from a surface. A hypothesis is **not** a finding. It
records:

- a possible root cause (bug class)
- the affected value path
- expected impact *if* it were true (described, never asserted)
- preconditions
- a suggested local test direction

Bug classes ArkheionX can suggest (heuristic, never confirmed):

accounting mismatch · share inflation / donation · withdrawal/redeem accounting
drift · liquidation boundary · reward double claim · oracle stale/wrong value ·
signature replay · Merkle proof shape confusion · authorization binding error ·
periphery/core mismatch · skip-on-revert behavior mismatch · callback
reentrancy / safety assumption · rounding / precision loss.

### C. Evidence

Any local artifact that supports or rejects a hypothesis:

- a source file / function and a `Source: <file>:<line>` reference
- a test file
- a saved command output
- a local Foundry test result (pass/fail), ingested via `arkheionx local-validate`
- an invariant result
- a rejection reason in the reviewer's own words

Evidence follows the existing ArkheionX evidence ladder: signals start at
`HEURISTIC` and only rise when connected to compiler/execution artifacts and,
finally, human review (`HUMAN_REVIEWED`).

### D. Status

Every hypothesis carries exactly one status:

- `open` — generated, not yet tested
- `testing` — a local test is being written or run
- `rejected` — the tested invariant/behavior held; the idea did not reproduce
- `confirmed` — independently reproduced locally **and** confirmed by a human
- `needs-human-review` — result is ambiguous and needs a human call

`confirmed` is never set by ArkheionX. Only a human sets `confirmed`, and only
with independent local proof.

### E. Case Study

A sanitized review-session artifact that summarizes what was tested: scope,
commands run, top surfaces, hypotheses tested, rejected hypotheses, confirmed
findings (if any and only if independently confirmed), what held, what was
noisy, and what remains unresolved. A case study is **not** an audit report and
does not claim protocol safety.

## 3. Safety rules

Research memory must never:

- claim a vulnerability without independent local proof and human confirmation
- produce live attack steps, transaction sequences, or live-chain instructions
- submit a bounty automatically
- assign final severity as truth
- imply it replaces an audit or guarantees protocol safety

Every research-memory artifact must clearly distinguish **hypothesis**,
**evidence**, **rejection**, **confirmation**, and **manual review required**.
All test suggestions are *local test directions*, never live steps. ArkheionX
requires no RPC, private keys, seed phrases, or production targets.

## 4. Output paths

Research-memory artifacts are written under `.arkheionx/research/` (generated,
local, gitignored — not source truth):

- `.arkheionx/research/agent-brief.md`
- `.arkheionx/research/agent-brief.json`
- `.arkheionx/research/hypotheses.md`
- `.arkheionx/research/hypotheses.json`
- `.arkheionx/research/case-study.md`
- `.arkheionx/research/case-study.json`

These sit beside the v4.0 review-map artifacts under `.arkheionx/out/` and are
regenerated deterministically from the same static analysis.

## 5. JSON schema plan

Three schemas back the JSON outputs (see `schemas/`):

### agent-brief.schema.json

- `schema_version`, `generated_at`, `repo_path`, `mode`
- `repository` summary: contracts, functions, test files, source files
- `review_priority`: top inspect-first surfaces, weak/strong coverage paths,
  unresolved assumptions
- `value_movement`: entries, exits, accounting mutations
- `test_gaps`: id, function, source, why it matters, suggested local test
- `authorization_surfaces`: contract, function, source, signal, why, local tests
- `periphery_surfaces`: function, target, source, interaction type, why, tests
- `behavior_mismatch_surfaces`: function, source, signal, why, suggested test
- `coverage_ranking`: surface, risk signal, coverage signal, priority, reason
- `hypotheses`: id, surface, bug class, why, local test direction, evidence
  required, status, human-review flag
- `do_not_claim`: explicit safety boundaries
- `safety`: disclaimer + boundaries

### hypothesis-log.schema.json

- `schema_version`, `generated_at`, `repo_path`, `mode`, `summary`
- `hypotheses[]`: `id` (HYP-001…), `status`, `surface`, `contract`, `function`,
  `source`, `value_path`, `bug_class`, `why_it_matters`, `suggested_local_test`,
  `evidence_required`, `test_command`, `result`, `rejection_reason`,
  `confirmation_notes`, `human_decision`
- `notes`: "rejected findings are evidence" guidance

### case-study.schema.json

- `schema_version`, `generated_at`, `repo_path`, `mode`
- `target`, `scope_note`, `commands_run`
- `review_map_summary`, `top_value_paths`, `top_assumptions`, `top_test_gaps`
- `authorization_surfaces`, `periphery_surfaces`
- `hypotheses_tested`, `rejected_hypotheses`, `confirmed_findings`
- `what_held`, `what_was_noisy`, `unresolved`, `next_review_areas`
- `safety_note`

## 6. Status transitions (human-driven)

```text
open ──► testing ──► rejected        (invariant/behavior held)
                └──► needs-human-review (ambiguous)
                └──► confirmed         (independent local proof + human sign-off)
```

ArkheionX only ever emits `open` hypotheses. Every later transition is recorded
by a human or by an agent acting under human review, after a local test.

## See also

- [`V4_1_RESEARCH_WORKFLOW.md`](V4_1_RESEARCH_WORKFLOW.md) — the end-to-end workflow
- [`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) — the v5 blind-spot layer built on these surfaces
- [`V5_WORKFLOW.md`](V5_WORKFLOW.md) — the v5 attention-allocation workflow
- [`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) — bug bounty triage
- [`PRE_AUDIT_WORKFLOW.md`](PRE_AUDIT_WORKFLOW.md) — pre-audit readiness
- [`REVIEW_MAP.md`](REVIEW_MAP.md) — the v4.0 review-map surface
- [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md) — how to read ArkheionX output


## How research memory feeds the V6 evidence graph

The v6 [Evidence Graph](EVIDENCE_GRAPH.md) reads local research memory to assign
its two strongest states. A surface is only marked `rejected-with-evidence` or
`confirmed-candidate` when a local `hypotheses.json` (under
`.arkheionx/research/`) records that status alongside a recorded local test —
never from scoring alone. In a default static run those states are absent, which
is the honest result.

This closes the loop: `hypothesis-log` captures what you tested and rejected, and
`evidence-graph` reflects it back so the unresolved surfaces shrink as your
research memory grows. A `confirmed-candidate` is still **not** a confirmed
vulnerability — a human makes the final call with independent local proof. See
[`V6_WORKFLOW.md`](V6_WORKFLOW.md).
