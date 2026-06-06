# Protocol Graph Smoke Test (v3.8, in progress)

> Status: active v3.8.0 branch work, not a finalized or published release. This
> smoke workflow is local and offline: no Foundry install, no `forge`, no RPC,
> and no network. It verifies the Protocol Intelligence Core and the
> review-package protocol-graph integration, and confirms the safety boundary.

This is a repeatable, network-free smoke run. Steps 1–6 run the existing test
suites; steps 7–13 use a small temporary fixture to confirm the review-package
protocol-graph behavior and the no-overclaim boundary. Nothing is uploaded,
submitted, or published.

## Prerequisites

- A local Arkheionx checkout (`arkheionx version` works).
- `python3` available.

This smoke test uses a `$TMP` shell variable instead of any hard-coded home path.

## 1. Run the intelligence engine tests

```sh
python3 -m unittest tests.test_intelligence_roles tests.test_intelligence_value_paths \
  tests.test_intelligence_assumptions tests.test_intelligence_test_gaps
```

## 2. Run the protocol graph tests

```sh
python3 -m unittest tests.test_intelligence_graph
```

## 3. Run the coverage correlation tests

```sh
python3 -m unittest tests.test_intelligence_coverage
```

## 4. Run the evidence/report graph context tests

```sh
python3 -m unittest tests.test_evidence_graph_context tests.test_report_graph_context
```

## 5. Run the review-package protocol graph tests

```sh
python3 -m unittest tests.test_review_package_protocol_graph
```

## 6. Run the full suite and make validate

```sh
python3 -m unittest discover -s tests -p "test_*.py"
make validate
```

Both should complete cleanly; `make validate` exits `0`.

## 7. Create a temporary project with optional graph fixtures

The Protocol Intelligence Core ships no public graph writer, so this step writes
a tiny, hand-made optional fixture under `.arkheionx/out/protocol-graph/` to
exercise the review-package inclusion path. It is illustrative only.

```sh
TMP="$(mktemp -d)"
mkdir -p "$TMP/.arkheionx/out/review-map" "$TMP/.arkheionx/out/protocol-graph"
printf '{"schema_version":"1.0.0"}' > "$TMP/.arkheionx/out/review-map/review-map.json"
printf '{}' > "$TMP/.arkheionx/out/review-map/evidence-links.json"
printf '{"targets":[]}' > "$TMP/.arkheionx/out/artifacts-index.json"
printf '%s' '{"graph_id":"protocol-intelligence-graph:demo:g1","protocol_name":"demo","nodes":[],"edges":[],"checks":[],"manual_review_required":true,"ready_for_submission":false}' \
  > "$TMP/.arkheionx/out/protocol-graph/graph.json"
```

## 8. Baseline the review-package artifact count

```sh
arkheionx review-package "$TMP" --no-write --json | python3 -c 'import sys,json;print("with graph", json.load(sys.stdin)["artifact_count"])'
```

Remove the graph file and re-run to confirm the graph artifacts are **optional**
(the package still builds, with a lower count):

```sh
mv "$TMP/.arkheionx/out/protocol-graph/graph.json" "$TMP/graph.json.bak"
arkheionx review-package "$TMP" --no-write --json | python3 -c 'import sys,json;print("without graph", json.load(sys.stdin)["artifact_count"])'
mv "$TMP/graph.json.bak" "$TMP/.arkheionx/out/protocol-graph/graph.json"
```

The "with graph" count is higher; a missing `protocol-graph/` folder is never an
error.

## 9. Verify the manifest includes the graph kind

```sh
arkheionx review-package "$TMP" --json >/dev/null
python3 -c "import json; m=json.load(open('$TMP/.arkheionx/out/review-package/manifest.json')); print('graph kinds', sorted({a['kind'] for a in m['included_artifacts'] if a['kind'].startswith('protocol_graph')}))"
```

Expect at least `protocol_graph` in the listed kinds.

## 10. Verify `manual_review_required` true and `ready_for_submission` false

```sh
arkheionx review-package "$TMP" --json | python3 -c 'import sys,json;d=json.load(sys.stdin);print("manual_review_required",d["manual_review_required"]);print("ready_for_submission",d["ready_for_submission"]);assert d["manual_review_required"] is True and d["ready_for_submission"] is False'
```

## 11. Verify no HUMAN_REVIEWED and no finality wording in the package

```sh
python3 - "$TMP" <<'PY'
import sys, pathlib
root = pathlib.Path(sys.argv[1]) / ".arkheionx" / "out" / "review-package"
blob = (root / "manifest.json").read_text() + (root / "validation.json").read_text()
low = blob.lower()
assert "HUMAN_REVIEWED" not in blob, "human-reviewed status must not appear"
for term in ("confirmed vulnerability", "final severity", "audit passed", "bounty eligible"):
    assert term not in low, f"forbidden finality wording present: {term}"
print("no HUMAN_REVIEWED and no finality wording: ok")
PY
```

## 12. Verify the export is deterministic

```sh
arkheionx review-package "$TMP" --export zip --json | python3 -c 'import sys,json;print("first", json.load(sys.stdin)["export_checksum_sha256"])'
arkheionx review-package "$TMP" --export zip --json | python3 -c 'import sys,json;print("second", json.load(sys.stdin)["export_checksum_sha256"])'
```

The two export checksums match: repeating the export over unchanged inputs is
byte-identical. The archive contains the `protocol-graph/` files under
`artifacts/`, with relative paths only.

## 13. Verify validation catches an overclaim (negative check)

```sh
printf '%s' '{"graph_id":"g","protocol_name":"demo","nodes":[],"edges":[],"note":"confirmed vulnerability","manual_review_required":true,"ready_for_submission":false}' \
  > "$TMP/.arkheionx/out/protocol-graph/graph.json"
arkheionx review-package "$TMP" --json | python3 -c 'import sys,json;d=json.load(sys.stdin);print("validation_status", d["validation_status"]);print("ready_for_submission", d["ready_for_submission"])'
```

The tampered artifact makes the package invalid while `ready_for_submission`
stays `false`; the no-overclaim boundary holds.

## 14. Clean up

```sh
rm -rf "$TMP"
```

## Notes

This smoke test is local and static only: no RPC, no private keys, no seed
phrases, no live-chain calls, no transaction broadcasting, no exploit automation,
and no auto-submit. Protocol-graph artifacts are optional review context; they
are never required, never finalize a conclusion, and the package is never pushed,
published, or ready for submission.

## Related docs

- [`PROTOCOL_INTELLIGENCE_CORE.md`](PROTOCOL_INTELLIGENCE_CORE.md)
- [`PROTOCOL_GRAPH_WORKFLOW.md`](PROTOCOL_GRAPH_WORKFLOW.md)
- [`REVIEW_PACKAGE.md`](REVIEW_PACKAGE.md)
- [`REVIEW_PACKAGE_SMOKE_TEST.md`](REVIEW_PACKAGE_SMOKE_TEST.md)
