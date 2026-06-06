# Metadata Schema

Every PoC in Arkheionx Vault is described by an entry in
`metadata/registry.json`. The machine-readable source of truth is
`metadata/schema.json`; this document explains the same contract in prose.

## Why a registry

Public surfaces (README registry, reports, verification skeletons, dashboards)
are generated from this single source of truth. Hand-edited tables drift from
code; generated ones do not.

## Top-level shape

`metadata/registry.json` contains:

| Field | Type | Description |
|---|---|---|
| `version` | string | Registry format/version label. |
| `maintainer` | string | Maintainer identity. |
| `generated_at` | string | Optional timestamp if a generator writes one. |
| `entries` | array | One registry entry per PoC. |

## Required entry fields

Every entry currently requires the following fields. For EVM entries,
`block_number` is the exact fork block used by the Solidity PoC; it may be the
attack block or `attack block - 1`, but it must match the source file.

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable kebab-case identifier, e.g. `2021-10-indexed-finance`. |
| `title` | string | Human-readable incident title. |
| `protocol` | string | Protocol/project name as it should appear publicly. |
| `date` | string | `YYYY-MM` incident/disclosure month. |
| `vm` | enum | `EVM`, `SVM`, `MoveVM`, or `Other`. |
| `chain` | string | Chain slug, e.g. `ethereum`, `base`, `arbitrum`, `bsc`. |
| `rpc_alias` | string | Fork alias declared in `EVM/foundry.toml` for EVM PoCs. |
| `block_number` | integer/null | Pinned fork block. Required for active EVM entries. |
| `severity` | enum | See [severity values](#severity-values). |
| `category` | enum | See [category values](#category-values). |
| `exploit_primitive` | string | Concise primitive abused by the attacker. |
| `status` | enum | See [status values](#status-values). |
| `reproducibility` | enum | See [reproducibility values](#reproducibility-values). |
| `poc_path` | string | Repo-root-relative path, e.g. `EVM/test/2021-10/Exploit_2021-10.t.sol`. |
| `summary` | string | One-paragraph summary without hype. |
| `root_cause` | string | Technical root cause. |
| `impact` | string | Concrete impact: drained funds, control transition, DoS, etc. |
| `attacker_path` | string | Step-by-step attacker path at a high level. |
| `invariant_broken` | string | Protocol invariant that failed. |
| `protocol_assumption_failure` | string | Assumption the protocol made that turned out false. |
| `attacker_profit_check` | string | Intended assertion/proof for attacker profit or control. |
| `victim_loss_check` | string | Intended assertion/proof for victim loss or state damage. |
| `assertion_quality` | enum | Static assertion strength: `strong`, `medium`, `weak`, `none`, `unknown`. |
| `verification_status` | enum | Runtime verification status. |
| `references` | array | One or more `{title, url}` references unless the entry is embargoed/educational. |

## Optional entry fields

| Field | Type | Description |
|---|---|---|
| `loss_usd` | number | Approximate USD loss at incident time. |
| `attack_tx` | string | Primary attack transaction hash. |
| `patched_status` | enum | `patched`, `partially-patched`, `unpatched`, or `n/a`. |
| `patch_reference` | string | Patch reference if public. |
| `disclosure_reference` | URI | Disclosure/advisory reference. |
| `disclosure_link` | URI | Disclosure/advisory link. |
| `contest_link` | URI | Contest report link if applicable. |
| `writeup_reference` | URI | Long-form write-up reference. |
| `writeup_link` | URI | Long-form write-up link. |
| `audit_lesson` | string | Auditor-facing lesson. |
| `similar_incidents` | array | Related entry IDs/slugs. |
| `latest_public_rpc_status` | enum | Latest public-RPC smoke-test result; not final verification. |
| `latest_public_rpc_notes` | string | Notes about the public-RPC smoke test; never include RPC URLs/API keys. |
| `notes` | string | Maintainer notes. |
| `tags` | array | Free-form tags. |

## Enum values

### Category values

These values mirror `metadata/schema.json` and `docs/EXPLOIT_TAXONOMY.md`:

- `oracle-manipulation`
- `flash-loan-price-manipulation`
- `reentrancy`
- `read-only-reentrancy`
- `access-control-failure`
- `arithmetic-precision-rounding`
- `accounting-mismatch`
- `share-price-manipulation`
- `donation-inflation`
- `governance-attack`
- `signature-permit-misuse`
- `bridge-validation-failure`
- `liquidation-logic-flaw`
- `vault-strategy-accounting-flaw`
- `amm-invariant-manipulation`
- `fee-on-transfer-rebasing-assumption`
- `callback-misuse`
- `initialization-bug`
- `proxy-upgradeability-issue`
- `unsafe-external-call`
- `bad-debt-creation`
- `invariant-bypass`
- `economic-design-flaw`
- `other`

### Status values

| Value | Meaning |
|---|---|
| `historical` | Real historical incident, already resolved or no longer exploitable as written. |
| `patched` | Fixed in production; PoC reproduces pre-patch/fork state. |
| `educational` | Synthetic or explanatory entry. |
| `template` | Skeleton, not yet a working PoC. |
| `incomplete` | Code/metadata exists but is below the standard. |
| `needs-verification` | Listed but not runtime-verified on this branch/environment. |
| `embargoed` | Under disclosure embargo; do not include active-target exploit details. |

### Severity values

- `critical`
- `high`
- `medium`
- `low`
- `informational`
- `unknown`

### VM values

- `EVM`
- `SVM`
- `MoveVM`
- `Other`

### Reproducibility values

| Value | Meaning |
|---|---|
| `deterministic-confirmed` | Pinned archival fork run has passed and a real verification report is committed. |
| `deterministic-likely-but-unverified` | Source/metadata are pinned and plausible, but archival fork execution is not recorded. |
| `requires-archival-rpc` | PoC needs historical state unavailable from common public RPCs. |
| `partially-reproducible` | Some parts reproduce, but not the complete historical path. |
| `compile-only` | Compiles but is not expected to execute as a full fork reproduction yet. |
| `incomplete` | Missing required behavior, metadata, or assertions. |
| `unknown` | Status not yet classified. |

### Assertion quality values

- `strong`
- `medium`
- `weak`
- `none`
- `unknown`

### Verification status values

- `verified`
- `not-run-no-rpc`
- `failed`
- `compile-only`
- `pending`
- `unknown`

### Public RPC smoke-test values

- `not-tested`
- `public-rpc-pass`
- `public-rpc-not-archival`
- `public-rpc-rate-limited`
- `public-rpc-unstable`
- `public-rpc-failed-unknown`

## Validation rules

Run validation from the repository root:

```sh
python3 scripts/validate_metadata.py
```

The validator enforces:

1. Schema-required fields, enum values, simple URI formats, and no unexpected
   fields when `additionalProperties: false` applies.
2. Unique entry IDs.
3. Existing `poc_path` files for non-embargoed entries.
4. At least one reference for non-`embargoed`, non-`educational`, non-`template`
   entries.
5. EVM `rpc_alias` values are declared in `EVM/foundry.toml`.
6. EVM `block_number` matches the block passed to `createSelectFork` in the PoC
   source file.
7. EVM `rpc_alias` matches the alias passed to `createSelectFork`; direct
   `vm.envString("ETH_RPC_URL")` usage is mapped back to the matching
   `foundry.toml` alias.
8. Embargoed entries do not include `poc_path` or `attack_tx`.

## Example entry

```json
{
  "id": "2021-10-indexed-finance",
  "title": "Indexed Finance — DEFI5/CC10 reweight manipulation",
  "protocol": "Indexed Finance",
  "date": "2021-10",
  "vm": "EVM",
  "chain": "ethereum",
  "rpc_alias": "mainnet",
  "block_number": 13417948,
  "severity": "critical",
  "category": "amm-invariant-manipulation",
  "exploit_primitive": "weight-shift abuse during index reweighting",
  "status": "historical",
  "reproducibility": "deterministic-likely-but-unverified",
  "poc_path": "EVM/test/2021-10/Exploit_2021-10.t.sol",
  "summary": "During an index reweighting, the attacker used flash-loaned assets to mint outsized index tokens and redeem the underlying basket.",
  "root_cause": "Reweighting math allowed attacker-supplied imbalance to dominate new weights.",
  "impact": "Approximately $16M drained from DEFI5 and CC10 indices.",
  "attacker_path": "Flash-loan supply, dominate reweight inputs, mint outsized index tokens, redeem underlying basket.",
  "invariant_broken": "Index token mint price equals fair basket value during reweighting.",
  "protocol_assumption_failure": "Assumed reweight inputs were bounded by realistic counterparty capital.",
  "attacker_profit_check": "Attacker basket-asset balance after redeem > pre-attack basket-asset balance.",
  "victim_loss_check": "DEFI5 / CC10 underlying balances < pre-attack balances.",
  "assertion_quality": "weak",
  "verification_status": "not-run-no-rpc",
  "attack_tx": "0x44aad3b853866468161735496a5d9cc961ce5aa872924c5d78673076b1cd95aa",
  "references": [
    {
      "title": "BlockSec analysis",
      "url": "https://blocksecteam.medium.com/the-analysis-of-indexed-finance-security-incident-8a62b9799836"
    }
  ]
}
```
