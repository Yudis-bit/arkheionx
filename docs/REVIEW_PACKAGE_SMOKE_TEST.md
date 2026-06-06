# Review Package Smoke Test

A local, repeatable smoke workflow for the v3.6 review package. It runs entirely
on your machine in a temporary directory, copies a bundled demo, builds the
package in dry-run, write, and export modes, and checks the safety-relevant
output. Nothing is uploaded, submitted, or published.

## Prerequisites

- A local Arkheionx install (`arkheionx version` works).
- A shell with `python3` available for JSON inspection.

This smoke test uses a `$TMP` shell variable instead of any hard-coded home
path.

## 1. Create a temporary directory

```sh
TMP="$(mktemp -d)"
echo "smoke dir: $TMP"
```

## 2. Copy a bundled demo project

```sh
arkheionx demo --copy lending-vault "$TMP/demo"
```

## 3. Generate the review-map artifacts

```sh
arkheionx review-map "$TMP/demo"
arkheionx value-paths "$TMP/demo"
arkheionx assumptions "$TMP/demo"
arkheionx test-gap-map "$TMP/demo"
arkheionx proof-plan "$TMP/demo"
arkheionx evidence-links "$TMP/demo"
```

## 4. Build the package as a dry run (no files written)

```sh
arkheionx review-package "$TMP/demo" --no-write --json
```

## 5. Build the package folder

```sh
arkheionx review-package "$TMP/demo" --json
```

## 6. Export a deterministic ZIP

```sh
arkheionx review-package "$TMP/demo" --export zip --json
```

## 7. Inspect the package layout

```sh
find "$TMP/demo/.arkheionx/out/review-package" -maxdepth 2 -type f
```

Expect `manifest.json`, `validation.json`, `README.md`, `limitations.md`,
`checksums/SHA256SUMS`, copied files under `artifacts/`, and (when buildable)
`artifacts/intelligence/protocol-model.json`.

## 8. Inspect the archive entries

```sh
python3 -c "import zipfile, glob; z=glob.glob('$TMP/demo/.arkheionx/out/review-package/exports/*.zip')[0]; print('\n'.join(zipfile.ZipFile(z).namelist()))"
```

Entries are under `arkheionx-review-package/` and use relative paths only; the
`exports/` directory is not inside the archive.

## 9. Verify `manual_review_required` is true

```sh
arkheionx review-package "$TMP/demo" --json | python3 -c "import sys, json; d=json.load(sys.stdin); print('manual_review_required', d['manual_review_required'])"
```

## 10. Verify `ready_for_submission` is false

```sh
arkheionx review-package "$TMP/demo" --json | python3 -c "import sys, json; d=json.load(sys.stdin); print('ready_for_submission', d['ready_for_submission'])"
```

## 11. Verify no absolute paths in the result

```sh
arkheionx review-package "$TMP/demo" --json | python3 -c "import sys, json; d=json.load(sys.stdin); print('package_root', d['package_root']); assert not d['package_root'].startswith('/')"
```

## 12. Verify the protocol-model sidecar when buildable

```sh
arkheionx review-package "$TMP/demo" --json | python3 -c "import sys, json; d=json.load(sys.stdin); print('protocol_model_included', d['protocol_model_included'], d['protocol_model_path'])"
```

## 13. Verify cross-reference warning counts

```sh
arkheionx review-package "$TMP/demo" --json | python3 -c "import sys, json; d=json.load(sys.stdin); print('crossref', d['crossref_check_count'], 'warnings', d['crossref_warning_count'], 'errors', d['crossref_error_count'])"
```

Cross-reference warnings are guidance, not failures; cross-reference errors stay
at zero in this local smoke.

## 14. Clean up the temporary directory

```sh
rm -rf "$TMP"
```

## Notes

This smoke test is local and static only: no RPC, no private keys, no seed
phrases, no live-chain calls, no transaction broadcasting, no exploit
automation, and no auto-submit. The package is review guidance: manual review is
required, and it is not pushed, published, or ready for submission.

## Related docs

- [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md)
- [`REVIEW_PACKAGE_WORKFLOW.md`](REVIEW_PACKAGE_WORKFLOW.md)

## Optional: local validation inclusion (v3.7, in progress)

This optional step checks that the review package picks up local-validation
artifacts. It is local and offline: no Foundry install, no `forge`, no RPC, and
no network.

```sh
# Copy a small saved Foundry output into the temp project.
cp tests/fixtures/local_validation/foundry/forge-test-json-basic.json "$TMP/foundry-output.json"

# Baseline package artifact count (no local validation yet).
arkheionx review-package "$TMP" --no-write --json | python3 -c 'import sys,json;print("before",json.load(sys.stdin)["artifact_count"])'

# Ingest the saved output (dry run, then write).
arkheionx local-validate "$TMP" --input "$TMP/foundry-output.json" --json --no-write
arkheionx local-validate "$TMP" --input "$TMP/foundry-output.json" --json

# Package artifact count now includes the local-validation artifacts.
arkheionx review-package "$TMP" --no-write --json | python3 -c 'import sys,json;d=json.load(sys.stdin);print("after",d["artifact_count"],"ready",d["ready_for_submission"])'
```

Expect the `after` artifact count to be higher than `before`, and
`ready_for_submission` to remain `false`. Manual review remains required. See
[`LOCAL_VALIDATION_SMOKE_TEST.md`](LOCAL_VALIDATION_SMOKE_TEST.md).

## Optional: protocol graph inclusion (v3.8, in progress)

This optional step checks that the review package picks up optional
protocol-graph artifacts. It is local and offline. The Protocol Intelligence Core
ships no public graph writer, so this writes a tiny illustrative fixture under
`protocol-graph/` to exercise the inclusion path.

```sh
# Baseline package artifact count (no protocol graph yet).
arkheionx review-package "$TMP/demo" --no-write --json | python3 -c 'import sys,json;print("before",json.load(sys.stdin)["artifact_count"])'

# Write a minimal optional graph fixture.
mkdir -p "$TMP/demo/.arkheionx/out/protocol-graph"
printf '%s' '{"graph_id":"protocol-intelligence-graph:demo:g1","protocol_name":"demo","nodes":[],"edges":[],"checks":[],"manual_review_required":true,"ready_for_submission":false}' \
  > "$TMP/demo/.arkheionx/out/protocol-graph/graph.json"

# Package artifact count now includes the protocol-graph artifact.
arkheionx review-package "$TMP/demo" --no-write --json | python3 -c 'import sys,json;d=json.load(sys.stdin);print("after",d["artifact_count"],"ready",d["ready_for_submission"])'
```

Expect the `after` count to be higher than `before`, and `ready_for_submission`
to remain `false`.

Verify the manifest includes the graph kind and that the export includes and
deterministically packages the graph file:

```sh
arkheionx review-package "$TMP/demo" --export zip --json >/dev/null
python3 -c "import json; m=json.load(open('$TMP/demo/.arkheionx/out/review-package/manifest.json')); print('graph kinds', sorted({a['kind'] for a in m['included_artifacts'] if a['kind'].startswith('protocol_graph')}))"
python3 -c "import zipfile, glob; z=glob.glob('$TMP/demo/.arkheionx/out/review-package/exports/*.zip')[0]; print('graph in archive', any(n.endswith('protocol-graph/graph.json') for n in zipfile.ZipFile(z).namelist()))"
```

Confirm validation catches an overclaim (negative check):

```sh
printf '%s' '{"graph_id":"g","protocol_name":"demo","nodes":[],"edges":[],"note":"confirmed vulnerability","manual_review_required":true,"ready_for_submission":false}' \
  > "$TMP/demo/.arkheionx/out/protocol-graph/graph.json"
arkheionx review-package "$TMP/demo" --json | python3 -c 'import sys,json;d=json.load(sys.stdin);print("validation_status",d["validation_status"],"ready",d["ready_for_submission"])'
```

The tampered artifact makes the package invalid while `ready_for_submission`
stays `false`. Graph artifacts are optional, never required, and never finalize a
conclusion; manual review remains required. See
[`PROTOCOL_GRAPH_SMOKE_TEST.md`](PROTOCOL_GRAPH_SMOKE_TEST.md) and
[`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md).
