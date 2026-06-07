# V5 Workflow — Blind Spot Intelligence

> Local/static heuristic review workflow. Nothing here claims a vulnerability,
> assigns severity, or runs live. Human review is required for every conclusion.

ArkheionX v5 keeps the stable v4 review-map workflow and adds a Blind Spot
Intelligence layer on top. The goal is **attention allocation**: spend limited
review time on high-impact surfaces with weak review evidence.

```text
arkheionx review-map .          # map the protocol (v4)
        |
arkheionx blind-spots .         # rank likely blind-spot candidates (v5)
        |
arkheionx criticality-map .     # map criticality potential / blast radius (v5)
        |
arkheionx counterfactuals .     # negate assumptions into research questions (v5)
        |
arkheionx research-pack . --out .arkheionx/research-pack   # bundle everything (v5)
        |
   human or AI agent writes local tests
        |
arkheionx hypothesis-log .      # track what was tested and rejected (v4.1)
        |
arkheionx case-study .          # sanitized research-session report (v4.1)
        |
   human decision               # the only place a finding is ever confirmed
```

## Step by step

### 1. `review-map` — map the protocol (v4)

Start here. The review map locates contracts, functions, value paths,
assumptions, and test gaps, and ranks an "inspect first" list. Everything v5
does is built on this map.

### 2. `blind-spots` — rank likely blind spots (v5)

Identifies high-impact surfaces with weak review evidence. Each candidate
carries a transparent blind spot score (impact + review-gap + complexity +
assumption), the reasons behind the score, a suggested counterfactual, a local
test direction, the evidence needed, and a do-not-claim note. Use it to decide
*where to look first*.

```bash
arkheionx blind-spots .
arkheionx blind-spots . --json
arkheionx blind-spots . --out .arkheionx/blind-spots --limit 15
```

### 3. `criticality-map` — map blast radius (v5)

Scores every surface by criticality potential (how bad it could be *if* a bug
existed) across dimensions such as value exit, accounting mutation,
authorization, oracle dependency, liquidation, callback, and periphery/core
boundary. It also shows where high criticality meets weak review density. This
is **not** severity.

```bash
arkheionx criticality-map .
arkheionx criticality-map . --json
```

### 4. `counterfactuals` — negate assumptions (v5)

Turns the protocol's guarding assumptions into testable research questions of
the form "what if this assumption is false?". Each counterfactual is a research
prompt with a local test idea, the evidence required, and a stop condition.
These are the questions to turn into local tests.

```bash
arkheionx counterfactuals .
arkheionx counterfactuals . --json
```

### 5. `research-pack` — bundle everything (v5, headline)

Generates a complete local research pack under `.arkheionx/research-pack/`: a
README, a review-map summary, the blind spot map, the criticality map, the
counterfactuals, an agent brief, a hypotheses template, an evidence-log
template, a do-not-claim file, a case-study template, and a JSON manifest. The
pack is model-agnostic and vendor-agnostic: hand it to a human reviewer or an AI
agent.

```bash
arkheionx research-pack .
arkheionx research-pack . --out .arkheionx/research-pack
arkheionx research-pack . --json
```

### 6. Write local tests (human or AI agent)

The pack tells a reviewer or agent which surfaces to inspect, which
counterfactuals to test, and what evidence would settle each one. Write local
Foundry tests for the highest-priority counterfactuals first.

### 7. `hypothesis-log` — track what was tested (v4.1)

Record each hypothesis, the test you ran, the result, and — if it held — the
rejection reason. A rejected hypothesis is useful research memory.

### 8. `case-study` — sanitized report (v4.1)

Generate a sanitized research-session report. `--from` incorporates the
hypothesis log's statuses.

### 9. Human decision

A finding is only ever confirmed by a person, only with independent local proof,
and only after human sign-off. ArkheionX never confirms a finding on its own.

## What each artifact is — and is not

| Output | Is | Is not |
| ------ | -- | ------ |
| Blind spot candidate | a high-impact, weakly-reviewed surface to inspect | a vulnerability |
| Criticality potential | heuristic blast radius if a bug existed | a severity |
| Counterfactual | a testable research question | a finding |
| Unknown surface | a surface lacking review evidence | a vulnerable surface |
| Hypothesis | a review prompt (status `open`) | a confirmed bug |
| Rejected hypothesis | research memory (an invariant held) | proof of safety |

## Safety

No RPC. No live-chain calls. No private keys or secrets. No exploit automation.
No transaction broadcasting. No auto-submit. No severity. No vulnerability
claims. Blind spot intelligence is a heuristic that allocates attention; a human
makes every security call.

See [`BLIND_SPOT_INTELLIGENCE.md`](BLIND_SPOT_INTELLIGENCE.md) for the model and
[`BUG_BOUNTY_WORKFLOW.md`](BUG_BOUNTY_WORKFLOW.md) for the bounty triage flow.
