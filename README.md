# ArkheionX

Local-first review infrastructure for smart contract security.

ArkheionX turns a Solidity or Foundry repository into deterministic review context: value paths, roles, trust assumptions, reachable flows, missing tests, evidence, and unresolved review gaps.

It does not replace auditors.
It gives auditors a better map.

## What it does

ArkheionX reads an authorized local repository and builds review artifacts that help a human understand where to spend attention first:

- value paths and asset movement;
- roles, permissions, and trust assumptions;
- reachable flows and interaction surfaces;
- missing or weak test areas;
- evidence tasks and kill conditions;
- unresolved review questions;
- machine-readable JSON and human-readable Markdown review packs.

Foundry tells reviewers whether the tests they wrote pass. ArkheionX helps show what they may have forgotten to test.

## What it is not

Not an audit.

ArkheionX does not automatically find vulnerabilities, replace auditors, confirm severity, prove safety, guarantee bounty outcomes, or act as an exploit generator.

No severity guarantee.

It does not claim endorsement from the Ethereum Foundation or any ecosystem grant program. Human review, local PoC validation, and protocol-specific judgment remain required.

## Who it is for

- Smart contract security researchers who need a deterministic map before deep review.
- Protocol teams preparing for an audit, contest, or internal security review.
- Auditors and audit firms that want structured context before manual analysis.
- Ecosystem grant reviewers evaluating whether the project is credible, honest, and useful enough to test.

## Why it exists

Large Solidity repositories are easy to review randomly. Reviewers need to know where value enters, moves, exits, and depends on assumptions before they decide what to test.

ArkheionX exists to reduce review blindness. It makes context explicit, repeatable, and local-first so a human reviewer can reason from evidence instead of a loose prompt.

## Quickstart

```bash
python3 -m pip install -e .
arkheionx version
arkheionx doctor
arkheionx review . --scope-file scope.md --out .arkheionx/review
```

No API key, private key, RPC URL, or token is required for the default workflow.

For source installation details, see [`docs/INSTALLATION.md`](docs/INSTALLATION.md) and [`docs/INSTALLER.md`](docs/INSTALLER.md). The source installer remains available with `sh install.sh`.

## Example workflow

```bash
# Inspect CLI and environment truth.
arkheionx version
arkheionx doctor

# Build the primary review pack.
arkheionx review . --scope-file scope.md --out .arkheionx/review

# Build the older focused map when you want a compact first read.
arkheionx review-map .

# Try a bundled demo.
arkheionx demo --list
arkheionx review-map examples/vault-strategy-oracle-fixture
```

See [`docs/CORE_WORKFLOW.md`](docs/CORE_WORKFLOW.md), [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md), and [`docs/DEMO_WORKFLOW.md`](docs/DEMO_WORKFLOW.md).

For the repository layout and generated-output boundaries, see [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md).

## Documentation

Start with [`docs/START_HERE.md`](docs/START_HERE.md), [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md), [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md), [`docs/CASE_STUDIES.md`](docs/CASE_STUDIES.md), and [`docs/EXTERNAL_VALIDATION.md`](docs/EXTERNAL_VALIDATION.md).

## Outputs

The primary review pack is written under `.arkheionx/` and is intended to stay local. It includes run context, scope map, value-flow map, interaction map, assumptions, review lanes, evidence tasks, report filter, agent input, `review.json`, and `manifest.json`.

Outputs are review context, not final truth. A relevant local Foundry test executed is evidence, but still not a final security judgment.

See [`docs/OUTPUT_ARTIFACTS.md`](docs/OUTPUT_ARTIFACTS.md), [`docs/EVIDENCE_PACKAGE.md`](docs/EVIDENCE_PACKAGE.md), and [`docs/INTERPRET_RESULTS.md`](docs/INTERPRET_RESULTS.md).

## Case studies

ArkheionX needs real review evidence, not adoption theater. The case-study layer records what question was asked, what value path was mapped, what evidence was produced, what a human validated, and what ArkheionX did not decide. Start with [`docs/CASE_STUDIES.md`](docs/CASE_STUDIES.md).

## Current status

Latest stable release: **v8.0.1**.

This checkout may include unreleased development work beyond the latest stable release. Use [`docs/VERSIONING.md`](docs/VERSIONING.md) for package, release, milestone, and experimental/internal status.

The public repository has been renamed to `Yudis-bit/arkheionx`. New users should use <https://github.com/Yudis-bit/arkheionx>. The old `DeFi-Exploit-PoCs` slug may remain in historical documents, archived material, generated artifacts, or compatibility notes. See [`docs/REPO_IDENTITY_MIGRATION.md`](docs/REPO_IDENTITY_MIGRATION.md).

The stable command surface is tracked in [`docs/PUBLIC_SURFACE.md`](docs/PUBLIC_SURFACE.md).

## Limitations

- Static/local context can miss important behavior, and missing-test signals can be noisy.
- Value paths are review maps, not proven execution traces.
- Evidence tasks require human judgment, PoC validation, and protocol-specific review.
- Severity decisions are not automatic, and a clean run does not prove a protocol safe.

## Safety boundaries

Local repository analysis only. No RPC by default. No live-chain mutation. No private keys or secrets. No automated exploitation. No auto-submit. Not an audit, certification, or replacement for manual review. No severity guarantee.

No RPC. No live-chain scanning. No auto-submit. Human review required.

## External feedback

Feedback from ecosystem grant review indicated that ArkheionX should strengthen real-world usage, external reviewer feedback, and case studies before pursuing broader ecosystem support. That feedback is directionally useful: the next stage is credibility, real usage on established DeFi protocols, reviewer feedback, and clear case studies.

See [`docs/EXTERNAL_VALIDATION.md`](docs/EXTERNAL_VALIDATION.md) and [`docs/PUBLIC_FEEDBACK_GUIDE.md`](docs/PUBLIC_FEEDBACK_GUIDE.md).

## Contributing

Contributions are useful when they improve deterministic review context, reduce noise, clarify outputs, strengthen fixtures, or improve documentation accuracy.

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

## Security and ethics

Use ArkheionX only on repositories you own or are authorized to review.

No live-chain mutation, private keys, production credentials, exploit automation, auto-submit, or unsupported vulnerability claims belong in the default workflow.

Security policy: [`SECURITY.md`](SECURITY.md). License: [`LICENSE`](LICENSE).
