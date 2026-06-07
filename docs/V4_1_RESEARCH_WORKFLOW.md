# V4.1 Research Workflow (AI-assisted review)

> Local/static review guidance only. Hypotheses are not vulnerabilities. Rejected
> hypotheses are useful evidence. No live-chain attack. No bounty submission
> without independent proof. Human review required.

ArkheionX v4.1 adds a **research memory** layer on top of the stable v4.0
review-map workflow, designed for AI-assisted bug bounty and pre-audit review.

> ArkheionX gives the map. The agent grinds the tests. The research memory keeps
> the evidence. The human makes the final call.

## The v4.0 stable workflow still holds

```text
repo → review-map → value paths → assumptions → test gaps → proof direction → human review
```

Nothing here changes. `review-map`, `value-paths`, `assumptions`,
`test-gap-map`, and `proof-plan` work exactly as before.

## What v4.1 adds

```text
review-map → agent brief → hypotheses → Foundry/manual tests
          → rejected/confirmed evidence → case study → human decision
```

Three new commands:

| Command | Purpose | Default artifact |
| --- | --- | --- |
| `arkheionx agent-brief <path>` | A focused, safe brief for an AI/security agent | `.arkheionx/research/agent-brief.md` |
| `arkheionx hypothesis-log <path>` | A structured hypothesis tracker / rejected-finding memory | `.arkheionx/research/hypotheses.md` |
| `arkheionx case-study <path>` | A sanitized review-session report template | `.arkheionx/research/case-study.md` |

All three emit human Markdown by default, `--json` for machine-readable output,
and accept `--out <dir>` to choose the artifact directory.

## How to use ArkheionX before asking an AI agent to review

The point is to **not** ask an agent a vague prompt like "find bugs in this
repo." Instead:

1. **Map the protocol.**

   ```bash
   arkheionx review-map .
   ```

2. **Generate the agent brief.**

   ```bash
   arkheionx agent-brief .
   ```

   The brief focuses the agent on value paths, accounting mutations,
   authorization surfaces, periphery/core flows, weakly covered paths, and a set
   of `open` hypotheses — instead of an open-ended hunt.

3. **Hand the brief to the agent.** Ask it to write *local Foundry tests* for
   the top hypotheses and to record results. The brief explicitly tells the
   agent not to claim bugs without proof.

4. **Track hypotheses.**

   ```bash
   arkheionx hypothesis-log .
   ```

   Fill in `Test command`, `Result`, and either `Rejection reason` or
   `Confirmation notes` as you test. A rejected hypothesis means the tested
   invariant or behavior held — that is research memory, not wasted work.

5. **Validate locally.** Use Foundry to validate or reject each hypothesis. You
   can ingest saved Foundry output with `arkheionx local-validate` to raise the
   evidence level from heuristic toward execution-confirmed.

6. **Write the research memory.**

   ```bash
   arkheionx case-study .
   ```

   The case study summarizes what was tested, what was rejected (with evidence),
   what held, what was noisy, and what remains unresolved.

7. **Human decides.** A human makes the final severity and duplicate call. No
   command in ArkheionX assigns severity or submits a report.

## Status model

Every hypothesis carries one status: `open`, `testing`, `rejected`,
`confirmed`, or `needs-human-review`. ArkheionX only ever emits `open`. Every
later transition is recorded by a human (or an agent under human review) after a
local test. `confirmed` requires independent local proof and a human sign-off.

See [`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md) for the full object
model and JSON schema plan.

## Safety

- Hypotheses are not vulnerabilities. They are review prompts.
- Rejected hypotheses are useful evidence (a held invariant).
- ArkheionX performs no RPC, live-chain, or transaction execution and requires
  no private keys or secrets.
- ArkheionX does not automate exploitation and does not submit bounties.
- Do not submit ArkheionX output as a vulnerability by itself. Validate
  manually, and only run it on repositories you are authorized to review.
- Human review is required for every conclusion.

## See also

- [`RESEARCH_MEMORY_MODEL.md`](RESEARCH_MEMORY_MODEL.md)
- [`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md)
- [`PRE_AUDIT_WORKFLOW.md`](PRE_AUDIT_WORKFLOW.md)
- [`CLI_REFERENCE.md`](CLI_REFERENCE.md)
- [`INTERPRET_RESULTS.md`](INTERPRET_RESULTS.md)
