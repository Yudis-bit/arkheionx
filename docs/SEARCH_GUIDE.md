# Search Guide

Arkheionx is designed to be searchable through GitHub. The repository is the
product interface: README, docs, metadata, reports, examples, issue templates,
and generated indexes all carry searchable security language.

Use GitHub search, local `rg`, or the generated index at
[`reports/search_index.md`](../reports/search_index.md).

## Search By Exploit Primitive

Examples:

```text
oracle manipulation
flash loan price manipulation
reentrancy
unsafe external call
initialization bug
upgradeability
governance attack
bridge validation
AMM invariant manipulation
lending liquidation
```

## Search By Broken Invariant

Examples:

```text
vault accounting
ERC4626
share price manipulation
totalAssets consistency
convertToShares
convertToAssets
deposit withdraw roundtrip
share inflation
donation risk class
reward conservation
no overclaim
interest index monotonicity
collateralization invariant
liquidity proportionality
cross-chain message validation
```

## Search By Failed Assumption

Examples:

```text
oracle freshness
spot price assumption
admin role assumption
initializer assumption
rounding assumption
reward index assumption
liquidation assumption
bridge endpoint assumption
external callback assumption
```

## Search By Assertion Family

Examples:

```text
attacker profit assertion
victim loss assertion
state damage assertion
access control assertion
invariant assertion
roundtrip assertion
conservation assertion
authorization assertion
```

## Search By Protocol Type

Examples:

```text
vault
ERC4626
AMM
lending
staking
oracle
bridge
governance
```

## Search By Chain Or VM

Examples:

```text
ethereum
base
EVM
Foundry
SVM
Anchor scaffold
MoveVM
Aptos scaffold
```

Current truth: EVM/Foundry is active. SVM/Anchor and MoveVM/Aptos are scaffolds
only unless future registry entries prove otherwise.

## Search By Severity Or Status

Examples:

```text
critical
high
historical
needs-verification
deterministic-likely-but-unverified
requires-archival-rpc
L4
L5
```

Current truth: the repository has 18 structured PoCs and 0 L4+ archival
confirmed entries.

## Search By Readiness Gap

Examples:

```text
pre-audit readiness
audit blocker
missing invariant
oracle-risk
vault-accounting
ERC4626 readiness
share accounting
totalAssets external dependency
fee accounting
strategy accounting
withdrawal queue
oracle-dependent vault
vault invariant tests
reentrancy-review
access-control-review
upgradeability review
reward accounting
AMM invariant
lending liquidation
cross-chain validation
Foundry invariant testing
```

## Search By Report Type

Examples:

```text
pre-audit report
readiness score
research dashboard
poc maturity index
verification report
search index
launch report
pre-audit sprint
ecosystem pack
Vault Rule Pack
Vault Launch Report
Vault Pre-Audit Sprint
PR readiness comment
generated issue checklist
generated issue plan
GitHub issue workflow
issue creation dry-run
issue marker
duplicate prevention
finding IDs
.arkheionx.json
SARIF
GitHub Code Scanning
baseline diff
readiness baseline
finding fingerprint
CI gating
fail threshold
new readiness gaps
resolved readiness gaps
pre-audit diff
oracle rule pack
access control rule pack
reentrancy value flow rule pack
reward accounting rule pack
semantic-lite analysis
Solidity structure extraction
evidence-based findings
confidence scoring
detection sources
Slither integration
Slither JSON
false positive reduction
keyword-only downgrade
low-confidence findings
Launch Report OS
Launch Readiness Report
Pre-Audit Sprint
Contest Readiness Mode
Contest Readiness Report
executive summary
remediation roadmap
delivery artifacts
scope checklist
researcher onboarding checklist
audit handoff package
try Arkheionx in 5 minutes
public demo workflow
demo protocol
oracle staking demo
before after case study
external validation
rule calibration
false positive calibration
external validation feedback
case study template
demo GitHub Action workflow
```

## Search By Monetization Or Services

Examples:

```text
Indie Builder Sponsor
Protocol Pro Sponsor
Launch Report
Pre-Audit Sprint
Ecosystem Pack
Research Sponsorship
Contest Readiness Pack
Launch Readiness Report
GitHub Action
PR comment mode
issue checklist
issue plan JSON
readiness remediation
config suppression
SARIF output
baseline diff
CI gating
GitHub Code Scanning
delivery artifacts
executive summary
remediation roadmap
public demo workflow
rule calibration
external validation feedback
services
sponsorship
monetization
```

## Local Search Commands

```sh
rg -n "vault accounting|share price manipulation|totalAssets" .
rg -n "ERC4626|convertToShares|convertToAssets|previewDeposit|previewWithdraw" .
rg -n "strategy accounting|withdrawalQueue|requestWithdraw|claimWithdraw|cooldown" .
rg -n "oracle manipulation|stale|TWAP|latestRoundData" .
rg -n "missing invariant|pre-audit readiness|audit blocker" .
rg -n "ARK-VLT-001|ARK-ORC-001|finding IDs|suppressed_findings" .
rg -n "SARIF|Code Scanning|baseline diff|finding fingerprint|fail-score-below" .
rg -n "PR readiness comment|generated issue checklist|generated issue plan|.arkheionx.json" .
rg -n "oracle rule pack|access control rule pack|reentrancy value flow|reward accounting rule pack" .
rg -n "issue marker|duplicate prevention|issue creation dry-run|GitHub issue workflow" .
rg -n "semantic-lite|Solidity structure extraction|finding evidence|confidence_reason" .
rg -n "Slither integration|slither-json|slither-output|slither-strict" .
rg -n "false positive reduction|keyword-only downgrade|low-confidence findings" .
rg -n "Launch Report OS|Pre-Audit Sprint|Contest Readiness Mode|delivery artifacts" .
rg -n "executive summary|remediation roadmap|scope checklist|researcher onboarding checklist" .
rg -n "try Arkheionx in 5 minutes|public demo workflow|oracle staking demo" .
rg -n "before after case study|rule calibration|external validation feedback" .
rg -n "root-cause analysis|failed assumption|broken invariant" .
```

## Search Tags

Recommended repository topics:

```text
defi-security
smart-contract-security
solidity-security
foundry
pre-audit
audit-readiness
invariant-testing
exploit-research
root-cause-analysis
web3-security
indie-defi
security-tools
github-action
```
