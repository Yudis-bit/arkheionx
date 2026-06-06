# Local Validation Smoke Test (v3.7, in progress)

> Status: active v3.7.0 branch work, not a finalized release. This smoke test is
> local and offline: it requires no Foundry install, no `forge`, no RPC, and no
> network. See [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md).

This walkthrough exercises the saved-output local-validation flow end to end using
only a temporary directory and a small saved Foundry output. It writes nothing
outside the temporary repository and cleans up afterward.

## 1. Create a temporary repo and a saved output

```sh
TMP="$(mktemp -d)"
cp tests/fixtures/local_validation/foundry/forge-test-json-basic.json "$TMP/foundry-output.json"
```

The fixture is a small, deterministic saved `forge test --json`-shaped document.
Producing such a file is external to Arkheionx; here we just copy a committed one.

## 2. Dry run (`--no-write`)

```sh
arkheionx local-validate "$TMP" --input "$TMP/foundry-output.json" --json --no-write
```

Expect exit `0`, `no_write` true, `written` false, `manual_review_required` true,
`ready_for_submission` false, and no `.arkheionx/` directory created under `$TMP`.

## 3. Write the artifacts

```sh
arkheionx local-validate "$TMP" --input "$TMP/foundry-output.json" --json
ls "$TMP/.arkheionx/out/local-validation"
ls "$TMP/.arkheionx/out/local-validation/checksums"
```

Expect `summary.json`, `run.json`, `results/`, `artifacts-index.json`, and
`checksums/SHA256SUMS`. `traces/` appears only when trace metadata is present.

## 4. Confirm safety properties

```sh
grep -R "ready_for_submission" "$TMP/.arkheionx/out/local-validation/summary.json"
```

Expect `"ready_for_submission": false` and `"manual_review_required": true`. The
generated files contain no absolute paths and no human-reviewed status, and make
no confirmed-vulnerability, final-severity, audit-passed, or bounty-eligibility
claim.

## 5. Include in a review package

```sh
# A minimal required artifact so the package has review-map context.
mkdir -p "$TMP/.arkheionx/out/review-map"
printf '{"schema_version":"1.0.0"}' > "$TMP/.arkheionx/out/review-map/review-map.json"

arkheionx review-package "$TMP" --json
```

Expect the package `artifact_count` to include the local-validation artifacts,
`manual_review_required` true, and `ready_for_submission` false. Local-validation
artifacts are optional and never required.

## 6. Optional deterministic export

```sh
arkheionx review-package "$TMP" --export zip --json
```

A repeated export over the same inputs produces an identical archive checksum, and
the archive entries are relative-only (no absolute paths, no backslashes).

## 7. Clean up

```sh
rm -rf "$TMP"
```

## Notes

- Foundry is not required: this flow ingests a saved file and never runs `forge`.
- No RPC, no fork-url behavior, no private keys, no seed phrases, no broadcasting,
  and no live-chain calls are involved.
- Manual review is always required; the output is review guidance only.
