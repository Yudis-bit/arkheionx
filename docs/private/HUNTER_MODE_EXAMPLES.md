# Hunter Mode — Examples

Private, local-only. All examples are generic: replace the placeholders with your own
authorized local inputs. Nothing here targets a specific company, protocol, or chain.

## Minimal run (scope only)

```bash
arkheionx hunter . \
  --scope-file scope.md \
  --out .arkheionx/hunter \
  --json
```

## Full local context (no RPC)

```bash
arkheionx hunter . \
  --scope-file scope.md \
  --known ./known \
  --audits ./audits \
  --addresses addresses.json \
  --out .arkheionx/hunter \
  --strict-context \
  --top 5 \
  --max-leads 25 \
  --json
```

## Optional read-only deployment verification

The endpoint is masked in all output and only read-only methods are ever issued.

```bash
arkheionx hunter . \
  --scope-file scope.md \
  --known ./known \
  --audits ./audits \
  --addresses addresses.json \
  --rpc-url "$RPC_ENDPOINT" \
  --out .arkheionx/hunter-rpc \
  --json
```

## Optional deployment calls (read-only)

`deployment-calls.json`:

```json
{
  "calls": [
    { "name": "owner", "to": "0x1111111111111111111111111111111111111111", "selector": "0x8da5cb5b", "decode": "address" }
  ]
}
```

```bash
arkheionx hunter . \
  --scope-file scope.md \
  --addresses addresses.json \
  --rpc-url "$RPC_ENDPOINT" \
  --deployment-calls deployment-calls.json \
  --out .arkheionx/hunter-rpc-calls \
  --json
```

## Optional live registry diff (read-only)

`registry-calls.json` (never guess selectors — provide them):

```json
{
  "registry_calls": [
    { "name": "getPools", "target": "Registry", "selector": "0x...", "decode": "address[]" },
    { "name": "poolCount", "target": "Registry", "selector": "0x...", "decode": "uint256" }
  ]
}
```

```bash
arkheionx hunter . \
  --scope-file scope.md \
  --addresses addresses.json \
  --rpc-url "$RPC_ENDPOINT" \
  --registry-calls registry-calls.json \
  --out .arkheionx/hunter-registry \
  --json
```

## Optional freshness baseline

```bash
arkheionx hunter . \
  --scope-file scope.md \
  --audits ./audits \
  --baseline-ref audited-commit \
  --out .arkheionx/hunter-baseline \
  --json
```

## Source recovery

```bash
# Provide a local source directory for deployed contracts with no repo source:
arkheionx hunter . --scope-file scope.md --addresses addresses.json \
  --source-dir ./recovered-src --out .arkheionx/hunter

# Disable network source recovery entirely (stay fully local):
arkheionx hunter . --scope-file scope.md --addresses addresses.json \
  --no-source-recovery --out .arkheionx/hunter
```

## Compatibility alias

```bash
arkheionx triage . --hunter --scope-file scope.md --out .arkheionx/hunter
```

## Reading the output

```bash
cat .arkheionx/hunter/00-run-context.md
cat .arkheionx/hunter/08-top-leads.md
cat .arkheionx/hunter/09-poc-plans.md
cat .arkheionx/hunter/10-submission-risk.md
cat .arkheionx/hunter/11-report-filter.md
cat .arkheionx/hunter/90-engine-evaluation.md
```

Read `08-top-leads.md` first. Pursue only PURSUE_NOW / NEEDS_POC leads, apply each kill
condition aggressively, and do not write a report until the PoC assertion passes.

## Generic options reference

```text
--scope-file       --known            --audits           --addresses
--source-dir       --source-recovery  --no-source-recovery
--baseline-ref     --since-date       --audit-date       --fresh-allowlist
--rpc-url          --deployment-calls --registry-calls
--strict-context   --top              --max-leads        --out   --json   --no-write
```
