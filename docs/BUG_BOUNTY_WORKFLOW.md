# Bug bounty workflow (triage and hypothesis)

ArkheionX is a **triage and hypothesis workbench** for bug bounty work on
DeFi smart-contract repositories. It helps you decide *where to look first* and
*what to test by hand*. It is **not** an exploit finder, a severity oracle, or a
submission tool, and it does **not** confirm vulnerabilities.

Use it to answer five questions before you start manual review:

1. Where is value moving?
2. Which value paths are least tested?
3. Which assumptions are protecting those paths?
4. What should I manually review first?
5. What proof direction should I try by hand?

## What ArkheionX does and does not do here

ArkheionX **does**:

- Map contracts, value paths, assumptions, and test gaps locally and statically.
- Rank value-sensitive functions in review order (not severity order).
- Point each test gap at a `Source: <file>:<line>` so you can open the code.
- Suggest a local Foundry proof scaffold direction you fill in yourself.

ArkheionX **does not**:

- It does not confirm vulnerabilities or prove a bug exists.
- It does not assign severity, impact, or exploitability.
- It does not run exploits, attacks, or transaction broadcasting.
- It does not call RPC endpoints or read deployed/live-chain contracts.
- It does not submit reports or interact with any bounty platform.
- It does not handle private keys, seed phrases, or production credentials.

A HIGH review priority is a prompt for human attention, never a finding.

## Authorization first

Only run ArkheionX on code you own or are explicitly authorized to review under
a published bounty scope or program rules. Do not point any workflow at live
systems, third-party infrastructure, or out-of-scope targets. ArkheionX never
performs network or live-chain actions, but *you* are still responsible for
staying inside the program's authorized scope.

## Safe command flow

Run from a local checkout of the in-scope repository:

```sh
arkheionx doctor
arkheionx review-map .
arkheionx value-paths .
arkheionx assumptions .
arkheionx test-gap-map .
arkheionx proof-plan .
```

Then work the output by hand:

1. **Start with `review-map`.** Read the **Inspect first** list. It is your
   review order, not a ranking of severity.
2. **Prioritize money-moving, externally dependent, and untested paths.** In
   `value-paths`, look for value exits with `coverage none`. Those are where an
   accounting or access-control mistake would matter most.
3. **Use `assumptions` to choose your review angle.** Each assumption (oracle
   freshness, access control, share proportionality, no-reentrancy, standard
   ERC20) is a question to answer in the code: *is this actually enforced?*
4. **Use `test-gap-map` to write local tests.** Open the `Source: <file>:<line>`
   for each gap and write a targeted Foundry test that exercises the path under
   adversarial inputs.
5. **Use `proof-plan` as a starting outline.** It gives an objective, setup,
   action, and assertions to fill in. It is a scaffold, never a result.
6. **Validate manually.** Run your own tests, read the code, and reach your own
   conclusion. ArkheionX output is review context only.

## Turning a test gap into a manual proof idea

For each gap, ask the questions the category implies, then write the test:

| Gap category | Manual review question | Local test idea |
|---|---|---|
| Value exit (`withdraw`, `divest`) | Can value leave beyond the caller's entitlement? | Deposit, then attempt an oversized or repeated exit; assert accounting holds. |
| Admin setter (`setOracle`, `setPrice`) | Is the privileged action bounded and validated? | Call as non-owner (expect revert); set adversarial values; assert downstream behavior. |
| Oracle-dependent (`harvest`) | Does stale or manipulated price corrupt accounting? | Drive a stale/extreme price through a mock; assert the guard rejects it. |

These are **hypotheses to test**, not confirmed issues.

## AI-assisted review with research memory (v4.1)

Do not hand an AI agent a vague prompt like "find bugs in this repo" — that
creates noise. Use ArkheionX to produce a structured handoff first.

> ArkheionX gives the map. The agent grinds the tests. The research memory keeps
> the evidence. The human makes the final call.

```sh
arkheionx review-map .
arkheionx agent-brief .       # focused brief for the agent
arkheionx hypothesis-log .    # track what you test and reject
arkheionx case-study .        # write the research-session memory
```

1. **Generate the agent brief.** `agent-brief` focuses the agent on value paths,
   accounting mutations, authorization surfaces (signature/Merkle/role/gate),
   periphery/core flows, weakly-covered surfaces, and a set of `open`
   hypotheses. Hand the agent the brief and ask it to write *local Foundry
   tests* for the top hypotheses.
2. **Track hypotheses.** `hypothesis-log` writes a log where every hypothesis
   starts `open`. As you test, set the status to `testing`, then `rejected`,
   `confirmed`, or `needs-human-review`, and fill in the test command, result,
   and rejection/confirmation notes.
3. **Rejected hypotheses are evidence.** A rejected hypothesis means the tested
   invariant or behavior held under the attempted conditions. That is research
   memory, not wasted work — it records what was checked so later reviewers do
   not duplicate effort.
4. **Write the case study.** `case-study --from .arkheionx/research` summarizes
   what was tested, what was rejected (with evidence), what held, what was noisy,
   and what remains unresolved. It makes no vulnerability claim unless a finding
   is independently confirmed.

`confirmed` is never set by ArkheionX. Only a human sets it, and only with
independent local proof. See
[`V4_1_RESEARCH_WORKFLOW.md`](archive/versions/V4_1_RESEARCH_WORKFLOW.md) and
[`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md).

## Prioritize with Blind Spot Intelligence (v5)

V4.1 gives you the map and the hypotheses. V5 tells you **where to spend time
first** — high-impact surfaces with weak review evidence:

```bash
arkheionx blind-spots .            # likely blind-spot candidates, ranked
arkheionx criticality-map .        # criticality potential (blast radius), not severity
arkheionx counterfactuals .        # "what if this assumption is false?" prompts to test
arkheionx research-pack . --out .arkheionx/research-pack   # bundle everything
```

A bounty-efficient flow: run `blind-spots` to pick the top few surfaces, run
`counterfactuals` to turn the guarding assumptions on those surfaces into local
tests, then record results in `hypothesis-log`. Hand `research-pack`'s
`05-agent-brief.md` and `04-counterfactuals.md` to an AI agent or a teammate.

Blind spot candidates are not vulnerabilities and criticality potential is not
severity. They allocate attention; a human still makes every call. See
[`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) and
[`V5_WORKFLOW.md`](archive/versions/V5_WORKFLOW.md).

## What good ArkheionX bounty output looks like

This is **demo/heuristic** output from the bundled
[`vault-strategy-oracle-fixture`](../examples/vault-strategy-oracle-fixture/README.md),
not a real finding:

```text
Top Test Gaps
  1. PriceOracle.setPrice [high; medium; admin]
     Source: src/PriceOracle.sol:27
     Proof suggestion: yes (proof-priceoracle-setprice)
  2. Strategy.divest [high; medium; exit]
     Source: src/Strategy.sol:44
     Proof suggestion: yes (proof-strategy-divest)
  3. Vault.emergencyWithdraw [high; medium; exit]
     Source: src/Vault.sol:72
     Proof suggestion: yes (proof-vault-emergencywithdraw)
```

Read this as: "the value exits and the admin setters are untested; open those
files, confirm the assumptions, and write tests." The covered `deposit` path is
deliberately **not** listed — the map tracks observed coverage, not guesses.

## Before you submit

- Independently confirm impact with your own analysis and tests.
- Do **not** submit ArkheionX output as a vulnerability by itself; a test gap or
  a HIGH review priority is not evidence of a bug.
- Follow the program's responsible-disclosure rules.
- Keep the security judgment yours; ArkheionX organizes context, it does not
  decide.

## Related

- [`V4_1_RESEARCH_WORKFLOW.md`](archive/versions/V4_1_RESEARCH_WORKFLOW.md) — AI-assisted research memory workflow.
- [`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md) — the research memory object model.
- [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md) — what each output section means.
- [`WHAT_ARKHEIONX_IS_NOT.md`](WHAT_ARKHEIONX_IS_NOT.md) — the boundaries.
- [`SECURITY.md`](../SECURITY.md) — reporting issues in ArkheionX itself.
- [`ETHICS.md`](ETHICS.md) — authorized-use expectations.


## V6 in triage: classify evidence, then close the unknowns

After ranking blind spots, use the v6 layer to make the unknowns explicit before
you submit anything:

```bash
arkheionx evidence-graph .       # which surfaces are tested, unresolved, or just look tested?
arkheionx interaction-matrix .   # which dangerous combinations lack tests?
arkheionx unresolved-map .       # what must be checked before ending review?
arkheionx complete-review . --out .arkheionx/complete-review
```

Then hand `08-agent-input.md` from the package to a review agent, write local
tests for the unresolved surfaces and interactions, and record the outcome. A
`confirmed-candidate` is **not** a confirmed vulnerability and an interaction
priority is **not** a severity — do not submit either as a finding. Validate
manually, keep it local, and only review repositories you are authorized to
review. See [`V6_WORKFLOW.md`](archive/versions/V6_WORKFLOW.md).

## Scope-aware contest triage (v7)

For an authorized audit contest or bug bounty with a written scope, start from the
scope instead of a vague "find bugs" prompt:

```bash
arkheionx scope-pack <repo> --scope-file <scope.md> --out .arkheionx/scope-pack
```

This produces a scope map, review lanes, precise scope tasks, a do-not-waste-time
filter (known issues, accepted risks, trusted roles, out-of-scope and low-only
patterns), an evidence template and rubric, a report-filter checklist, and
model-agnostic agent input. Write local tests per task, then grade and filter:

```bash
arkheionx evidence-judge <repo> --scope-file <scope.md>
arkheionx report-filter  <repo> --scope-file <scope.md>
```

`evidence-judge` grades whether a local test actually proves the task (it does not
confirm vulnerabilities; candidate-with-evidence is not a confirmed vulnerability).
`report-filter` classifies each candidate against the scope before you spend a
submission, and is not final triage. Keep private scope notes in local, gitignored
files under `.arkheionx/private/`; a built-in leak guard keeps target names out of
public files. See [`V7_WORKFLOW.md`](archive/versions/V7_WORKFLOW.md) and
[`SCOPE_ORCHESTRATION.md`](SCOPE_ORCHESTRATION.md). A human always makes the final
call.
