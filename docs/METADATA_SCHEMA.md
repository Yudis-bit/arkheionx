# Metadata Schema

Every PoC in Arkheionx Vault is described by an entry in
`metadata/registry.json`. The schema is also expressed machine-readable in
`metadata/schema.json`.

## Why a registry

Public surfaces (README registry, web app, GitHub topics) are generated from
this single source of truth. Hand-edited tables drift from code; generated
ones do not.

## Required fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable kebab-case identifier, e.g. `2023-03-euler-finance`. |
| `title` | string | Human-readable title, e.g. `Euler Finance`. |
| `protocol` | string | Protocol name as it appears in post-mortems. |
| `date` | string | `YYYY-MM` of the incident or disclosure. |
| `vm` | enum | `EVM`, `SVM`, `MoveVM`, or `Other`. |
| `chain` | string | `ethereum`, `base`, `arbitrum`, `optimism`, `polygon`, `bsc`, `avalanche`, `solana`, `aptos`, `sui`, etc. Use `n/a` for synthetic/educational. |
| `severity` | enum | `critical`, `high`, `medium`, `low`, `informational`. |
| `category` | enum | See [category values](#category-values). |
| `status` | enum | See [status values](#status-values). |
| `poc_path` | string | Path from repo root, e.g. `EVM/test/2017-07/Exploit_2017-07.t.sol`. |
| `reproducibility` | enum | See [reproducibility values](#reproducibility-values). |
| `summary` | string | One paragraph, plain prose. No marketing language. |
| `root_cause` | string | One paragraph, technical. |
| `impact` | string | One paragraph, concrete (USD lost, contracts drained, DoS surface). |
| `references` | array of `{title, url}` | At least one external reference unless `status` is `embargoed` or `educational`. |

## Conditional required fields

| Field | Required when |
|---|---|
| `block_number` | `vm == "EVM"` and `status != "embargoed"`. |
| `rpc_alias` | `vm == "EVM"` and the test calls `vm.createSelectFork`. |

## Optional fields

| Field | Type | Description |
|---|---|---|
| `loss_usd` | number | Approximate loss in USD at the time of incident. |
| `attack_tx` | string | Primary attack transaction hash. |
| `patched_status` | string | `patched`, `partially-patched`, `unpatched`, `n/a`. |
| `disclosure_link` | string | Link to bounty/disclosure record if public. |
| `contest_link` | string | Link to contest report if applicable. |
| `writeup_link` | string | Link to a long-form analysis. |
| `notes` | string | Free-form maintainer notes. |
| `tags` | array of string | Free-form tags. |

## Enum values

### Category values

`logic`, `oracle`, `access-control`, `reentrancy`, `dos`, `math`, `signature`,
`upgradeability`, `flash-loan`, `governance`, `mev`, `bridge`, `cryptography`,
`other`.

### Status values

| Value | Meaning |
|---|---|
| `historical` | Real incident, post-mortem available, no longer exploitable as written. |
| `patched` | Fixed in production; PoC reproduces pre-patch state via fork. |
| `educational` | Synthetic example illustrating a vulnerability class. |
| `template` | Skeleton, not yet a working PoC. |
| `embargoed` | Under disclosure embargo; metadata only. |
| `incomplete` | Code present, missing assertions or references. |
| `needs-verification` | Listed but the maintainer has not re-run it locally on this branch. |

### Severity values

`critical`, `high`, `medium`, `low`, `informational`.

### VM values

`EVM`, `SVM`, `MoveVM`, `Other`.

### Reproducibility values

| Value | Meaning |
|---|---|
| `deterministic` | Pinned fork, hard assertions, runs on configured archival RPC. |
| `partially-deterministic` | Pinned fork; some state recreated rather than forked. |
| `requires-archival-rpc` | Needs archive history beyond standard RPC retention. |
| `local-only` | Local validator with deployed bytecode, no fork. |
| `template-only` | Stub for future work. |
| `unverified` | Code present, reproducibility not yet confirmed. |

## Validation rules

`scripts/validate_metadata.py` enforces:

1. Every entry has all required fields.
2. Every `poc_path` exists on disk.
3. Every `id` is unique.
4. Every `vm == "EVM"` non-embargoed entry declares `block_number`.
5. Every `severity`, `status`, `vm`, `category`, `reproducibility` value is
   in the allowed enum.
6. `embargoed` entries do not include `poc_path`, `attack_tx`, or any
   field that would expose live exploit details.
7. Non-`embargoed`, non-`educational` entries declare at least one reference.

## Example entry

```json
{
  "id": "2017-07-parity-multisig",
  "title": "Parity Wallet — initWallet hijack",
  "protocol": "Parity Multisig Wallet",
  "date": "2017-07",
  "vm": "EVM",
  "chain": "ethereum",
  "severity": "critical",
  "category": "access-control",
  "status": "historical",
  "poc_path": "EVM/test/2017-07/Exploit_2017-07.t.sol",
  "block_number": 4043799,
  "rpc_alias": "mainnet",
  "reproducibility": "needs-verification",
  "summary": "Public initWallet on a deployed multisig allowed any caller to overwrite ownership and drain the wallet.",
  "root_cause": "Initializer was not access-controlled and could be re-invoked after deployment.",
  "impact": "Approximately 153,037 ETH (~$30M at the time) drained from a single wallet.",
  "loss_usd": 30000000,
  "attack_tx": "0x9dbf0326a03a2a3719c27be4fa69aacc9857fd231a8d9dcaede4bb083def75ec",
  "references": [
    {"title": "OpenZeppelin post-mortem", "url": "https://www.openzeppelin.com/news/on-the-parity-wallet-multisig-hack-405a8c12e8f7"}
  ]
}
```
