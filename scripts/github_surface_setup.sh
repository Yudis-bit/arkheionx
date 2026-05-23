#!/usr/bin/env bash
# github_surface_setup.sh
#
# Apply repository description and topics for the Arkheionx Vault
# repository (Yudis-bit/DeFi-Exploit-PoCs).
#
# Safe by default:
#   - Dry-run unless --apply is passed.
#   - Never changes visibility, never deletes anything, never pushes,
#     never modifies code, never uploads secrets.
#   - Only edits the repository description and topic list via gh CLI.
#
# Usage:
#   ./scripts/github_surface_setup.sh              # dry-run
#   ./scripts/github_surface_setup.sh --dry-run    # dry-run (explicit)
#   ./scripts/github_surface_setup.sh --apply      # actually apply
#
set -euo pipefail

REPO="Yudis-bit/DeFi-Exploit-PoCs"

DESCRIPTION="Arkheionx Vault — independent DeFi exploit PoC archive focused on assertions, root-cause analysis, and fork verification readiness."

TOPICS=(
  "web3-security"
  "defi-security"
  "smart-contract-security"
  "smart-contract-auditing"
  "solidity"
  "foundry"
  "exploit-poc"
  "incident-analysis"
  "security-research"
  "reproducible-research"
  "root-cause-analysis"
  "arkheionx"
)

mode="dry-run"
case "${1:-}" in
  ""|--dry-run) mode="dry-run" ;;
  --apply)      mode="apply" ;;
  -h|--help)
    sed -n '2,18p' "$0"
    exit 0
    ;;
  *)
    echo "error: unknown argument: $1" >&2
    echo "usage: $0 [--dry-run|--apply]" >&2
    exit 2
    ;;
esac

if ! command -v gh >/dev/null 2>&1; then
  echo "error: gh CLI not found in PATH." >&2
  echo "       install from https://cli.github.com/ and run 'gh auth login'." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "error: gh CLI is not authenticated." >&2
  echo "       run: gh auth login" >&2
  exit 1
fi

echo "repo:        $REPO"
echo "mode:        $mode"
echo
echo "description: $DESCRIPTION"
echo "topics:"
for t in "${TOPICS[@]}"; do
  echo "  - $t"
done
echo

if [ "$mode" = "dry-run" ]; then
  echo "[dry-run] would run:"
  echo "  gh repo edit $REPO --description \"\$DESCRIPTION\""
  for t in "${TOPICS[@]}"; do
    echo "  gh repo edit $REPO --add-topic $t"
  done
  echo
  echo "to apply for real, re-run with: $0 --apply"
  exit 0
fi

echo "[apply] setting description..."
gh repo edit "$REPO" --description "$DESCRIPTION"

echo "[apply] adding topics..."
for t in "${TOPICS[@]}"; do
  echo "  + $t"
  gh repo edit "$REPO" --add-topic "$t"
done

echo
echo "done. verify in GitHub repo About panel."
