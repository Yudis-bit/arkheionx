# ArkheionX Global Positioning

## One-line explanation

ArkheionX is local-first review infrastructure for smart contract security.

## 30-second explanation

ArkheionX turns a Solidity or Foundry repository into deterministic review context: value paths, roles, trust assumptions, reachable flows, missing tests, evidence, and unresolved review gaps.

It does not replace auditors. It gives auditors a better map.

## Two-minute explanation

Foundry tells reviewers whether the tests they wrote pass. ArkheionX helps show what they may have forgotten to test.

The tool reads local repository context and produces structured review artifacts: value-flow maps, role and assumption notes, review lanes, evidence tasks, report filters, and machine-readable JSON. The goal is to reduce review blindness before a human reviewer writes tests, validates a PoC, or decides severity.

ArkheionX is not an AI auditor, exploit generator, or bounty automation tool. It does not confirm vulnerabilities automatically, does not prove safety, and does not replace external review.

The next credibility step is real usage on established DeFi protocols, feedback from auditors and protocol teams, and case studies showing what the tool clarified during actual review work.

## Positioning rules

- Say "review infrastructure", not "AI auditor".
- Say "review context", not "findings".
- Say "review order", not "severity".
- Say "evidence task", not "PoC".
- Say "submitted" only when something was submitted.
- Say "accepted" only with proof.
- Do not claim Ethereum Foundation endorsement.
- Do not claim enterprise readiness without evidence.

## Core comparison

```text
Foundry tells reviewers whether the tests they wrote pass.
ArkheionX helps show what they may have forgotten to test.
```

## Public status

ArkheionX is credible enough for technical reviewers to test, but not mature enough to claim broad adoption or ecosystem validation.

The public repository has been renamed to `Yudis-bit/arkheionx`.
