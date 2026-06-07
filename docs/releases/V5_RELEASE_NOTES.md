# Arkheionx v5.0.0 — Blind Spot Intelligence

**Status: release metadata finalized locally; pending founder push, tag, GitHub
release, and site deploy.** The package version is `5.0.0`. The last published
tag remains `v4.0.0`, and the source installers and the GitHub Action still pin
to the last actually-tagged stable release, `v3.1.0`. Nothing here is published
to PyPI.

## 1. What V5 adds

V5 adds a **Blind Spot Intelligence** layer on top of the stable v4 review-map
workflow and the v4.1 research-memory commands. It is the first major step beyond
mapping:

- **V4** maps the protocol — where value moves, the assumptions that guard each
  path, and which paths have no tests.
- **V5** maps where research attention is weakest relative to how much could go
  wrong if a bug existed there.

## 2. Why V5 exists

A reviewer's scarcest resource is attention. V5 is an attention-allocation engine:
it ranks high-impact surfaces with weak review evidence, estimates criticality
potential (blast radius), and turns guarding assumptions into testable
counterfactuals, so a human or an AI agent spends limited time where it matters.

## 3. New commands

- `arkheionx blind-spots` — likely blind-spot candidates with a transparent
  additive score (impact + review-gap + complexity + assumption).
- `arkheionx criticality-map` — criticality potential (heuristic blast radius,
  not severity) across surfaces.
- `arkheionx counterfactuals` — "what if this assumption is false?" research
  prompts with local test directions and stop conditions.
- `arkheionx research-pack` — a complete local, vendor-agnostic research pack
  (headline). Writes by default.

## 4. Compatibility

`review-map` and its focused views (`value-paths`, `assumptions`, `test-gap-map`,
`proof-plan`) and the v4.1 research-memory commands (`agent-brief`,
`hypothesis-log`, `case-study`) are unchanged. The v5 commands build directly on
`review-map` output.

## 5. Quickstart

```sh
python3 -m pip install -e .
arkheionx review-map      examples/blind-spot-fixture
arkheionx blind-spots     examples/blind-spot-fixture
arkheionx criticality-map examples/blind-spot-fixture
arkheionx counterfactuals examples/blind-spot-fixture
arkheionx research-pack   examples/blind-spot-fixture --out .arkheionx/research-pack
```

## 6. V5 demo

`examples/blind-spot-fixture` is a small generic protocol — `PriceOracle`,
`CreditVault`, `ClaimGate`, `BundleRouter`, `MockToken` — whose test covers only
`deposit`. The value exit, the oracle/debt path, liquidation, the signature and
Merkle authorization surfaces, and the periphery batch are deliberately untested,
so ArkheionX surfaces them as likely blind spots. No planted vulnerabilities.

## 7. JSON schemas

`schemas/blind-spots.schema.json`, `schemas/criticality-map.schema.json`,
`schemas/counterfactuals.schema.json`, and
`schemas/research-pack-manifest.schema.json`. Every JSON output is parseable and
schema-validated by the test suite.

## 8. Safety boundaries

Local and static only. No RPC, no live-chain calls, no exploit automation, no
private-key handling, no auto-submit. Blind spot candidates are not
vulnerabilities; criticality potential is not severity; counterfactuals are
research prompts, not findings. ArkheionX does not confirm vulnerabilities,
assign final severity, prove protocol safety, or replace an audit. Human review
is required.

## 9. Known limitations

- Heuristic and static; blind spot detection is not perfect.
- No bug prediction, no severity, no probability.
- Real-protocol validation is still required
  ([`../REAL_PROTOCOL_PROOF_PLAN.md`](../REAL_PROTOCOL_PROOF_PLAN.md)).
- A finding is only ever confirmed by a human with independent local proof.

## 10. Validation matrix

Docs links, safety wording, version consistency, release readiness, the full
unit-test suite, `make validate`, the package build (`python -m build` +
`twine check`), and the website build all pass.

## 11. Documentation

- [`../BLIND_SPOT_INTELLIGENCE.md`](../BLIND_SPOT_INTELLIGENCE.md) — the model.
- [`../V5_WORKFLOW.md`](../V5_WORKFLOW.md) — the end-to-end workflow.
- [`../CLI_REFERENCE.md`](../CLI_REFERENCE.md) — command reference.
- [`../BUG_BOUNTY_WORKFLOW.md`](../BUG_BOUNTY_WORKFLOW.md) — bounty triage flow.

## 12. GitHub release draft

> **Arkheionx v5.0.0 — Blind Spot Intelligence.** V5 adds a local/static layer
> that prioritizes high-impact surfaces with weak review evidence, generates
> counterfactual research prompts, and packages the result into an AI/human-ready
> research pack. It builds on the stable `review-map` workflow. No RPC, no
> exploit automation, no severity, no bug claims; human review required.

## 13. Founder release commands

The package version is already finalized at `5.0.0` in this tree. To release:

```sh
git status --short --branch
make validate
git push origin main
git tag -a v5.0.0 -m "Arkheionx v5.0.0 — Blind Spot Intelligence"
git push origin v5.0.0
gh release create v5.0.0 \
  --title "Arkheionx v5.0.0 — Blind Spot Intelligence" \
  --notes-file docs/releases/V5_RELEASE_NOTES.md \
  dist/arkheionx-5.0.0-py3-none-any.whl \
  dist/arkheionx-5.0.0.tar.gz
```

The last tagged stable release stays `v3.1.0` (the installer/action pin) until a
new stable tag is cut.
