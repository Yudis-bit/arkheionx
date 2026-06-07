#!/usr/bin/env bash
# Arkheionx v4.0.0 local release smoke.
#
# Runs the stable review-map workflow against the bundled demo and the public
# documentation gates. Local and static only: no RPC, no live-chain calls, no
# exploit automation, no secrets, and no network access (the optional site build
# uses already-installed node modules).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="python3 -m arkheionx.cli.main"
DEMO="examples/vault-strategy-oracle-fixture"

note() { printf '\n=== %s ===\n' "$*"; }

note "version"
$PY version | head -4

note "doctor (status line)"
$PY doctor | grep -E "^Status" || true

note "review-map demo (exit 1 is intentional heuristic guidance)"
$PY review-map "$DEMO" >/dev/null 2>&1 && rc=0 || rc=$?
echo "review-map exit=$rc"
[ "$rc" = "0" ] || [ "$rc" = "1" ] || { echo "unexpected review-map exit"; exit 1; }

note "test-gap-map demo carries Source evidence"
$PY test-gap-map "$DEMO" --no-write --out /tmp/arkheionx-v4-smoke-nope >/tmp/arkheionx-v4-tgm.txt 2>/dev/null || true
if grep -q "Source:" /tmp/arkheionx-v4-tgm.txt; then
  echo "Source: present"
else
  echo "missing Source evidence"; exit 1
fi
rm -f /tmp/arkheionx-v4-tgm.txt

note "proof-plan demo"
$PY proof-plan "$DEMO" >/dev/null 2>&1 && rc=0 || rc=$?
echo "proof-plan exit=$rc"

note "documentation + safety gates"
python3 scripts/check_docs_links.py --check
python3 scripts/check_safety_wording.py --strict
python3 scripts/check_version_consistency.py --check
python3 scripts/check_release_readiness.py --check

note "optional site build (skipped if node_modules is absent)"
if [ -d site/node_modules ]; then
  ( cd site && npm run build >/dev/null 2>&1 && echo "site build OK" )
else
  echo "site build skipped (run 'cd site && npm ci' first)"
fi

note "smoke complete"
echo "Arkheionx v4 release smoke passed (local/static, no network, no secrets)."
