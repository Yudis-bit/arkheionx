# Public Feedback Guide

Arkheionx is a local-first DeFi value-flow workbench with security memory,
reports, test-plan generation, and advanced pre-audit readiness workflows.

Short version: Map the money flow. Find the missing tests.

This guide is for people trying Arkheionx from GitHub, LinkedIn, Discord, audit
or contest communities, or open-source security circles.

## Try It Safely

Use toy fixtures or repositories you own or are authorized to review.

Do not run Arkheionx as a way to target live protocols. The scanner is
local/static and does not need RPC, private keys, or live-chain access.

Start with:

- [`TRY_IN_5_MINUTES.md`](TRY_IN_5_MINUTES.md)
- [`PUBLIC_DEMO_WORKFLOW.md`](PUBLIC_DEMO_WORKFLOW.md)

## Best Feedback To Send

- Finding IDs that were useful.
- Finding IDs that were noisy.
- Missing readiness signals.
- Confusing report wording.
- GitHub Action setup friction.
- Score bands that felt too optimistic or too harsh.
- Sanitized examples of report output that should be clearer.

## How To Report False Positives

Use the `False positive report` issue template.

Include:

- Arkheionx version;
- finding ID;
- rule pack;
- evidence source if known;
- why the signal is noisy;
- expected downgrade or wording.

## How To Report False Negatives

Use the `False negative report` issue template.

Share a sanitized description of what Arkheionx missed. If the issue involves a
real unpatched vulnerability, do not disclose details publicly. Follow the
project, bounty, or program disclosure policy.

## How To Share Report Quality Feedback

Use the `Report quality feedback` template.

Tell us which output was confusing and who the intended reader was: builder,
auditor, researcher, founder, or ecosystem team.

## How To Share GitHub Action Issues

Use the `GitHub Action feedback` template.

Remove tokens, secrets, private repository names, and sensitive paths from any
workflow snippet.

## What Not To Disclose Publicly

- private keys, mnemonics, tokens, or RPC credentials;
- private repository contents without authorization;
- unpatched vulnerability details;
- exploit steps for live targets;
- unauthorized target details;
- bounty-sensitive details outside the program's disclosure process.

Feedback improves calibration. It does not create a formal audit relationship
or a security guarantee.
