#!/bin/sh
# Arkheionx uninstaller (v2.5.0 — Installer & Onboarding).
#
# Removes only Arkheionx-managed paths created by install.sh. It never uses
# root, never edits your shell profile, never deletes a repository checkout,
# your reports, or per-project `.arkheionx/` artifacts in other repositories.
#
# Usage:
#   sh uninstall.sh [--help] [--dry-run]
#
# Environment (all optional):
#   ARKHEIONX_INSTALL_DIR    Base install dir (default: $HOME/.arkheionx)
#   ARKHEIONX_BIN_DIR        Wrapper dir (default: $HOME/.arkheionx/bin)
#   ARKHEIONX_YES            1 to skip interactive confirmation
#   ARKHEIONX_DRY_RUN        1 to print actions without executing them
#   ARKHEIONX_PIPX_UNINSTALL 1 to also run `pipx uninstall arkheionx`
set -eu

ARKHEIONX_INSTALL_DIR="${ARKHEIONX_INSTALL_DIR:-$HOME/.arkheionx}"
ARKHEIONX_BIN_DIR="${ARKHEIONX_BIN_DIR:-$ARKHEIONX_INSTALL_DIR/bin}"
ARKHEIONX_YES="${ARKHEIONX_YES:-0}"
ARKHEIONX_DRY_RUN="${ARKHEIONX_DRY_RUN:-0}"
ARKHEIONX_PIPX_UNINSTALL="${ARKHEIONX_PIPX_UNINSTALL:-0}"

log() { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
err() { printf 'error: %s\n' "$*" >&2; }

usage() {
    cat <<'EOF'
Arkheionx uninstaller

Usage:
  sh uninstall.sh [--help] [--dry-run]

Removes only Arkheionx-managed paths:
  $ARKHEIONX_BIN_DIR/arkheionx
  $ARKHEIONX_INSTALL_DIR/venv
  $ARKHEIONX_INSTALL_DIR/install.json (install receipt)
  $ARKHEIONX_INSTALL_DIR (only if empty after the above)

It does not use root, does not edit shell profiles, and never deletes a repo
checkout, your reports, or per-project .arkheionx/ artifacts. If you installed
with pipx, run `pipx uninstall arkheionx` (or set ARKHEIONX_PIPX_UNINSTALL=1).
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --dry-run) ARKHEIONX_DRY_RUN=1 ;;
        *) err "unknown option: $1"; usage; exit 2 ;;
    esac
    shift
done

# Refuse to operate on a non-managed install dir to avoid deleting user data.
case "$ARKHEIONX_INSTALL_DIR" in
    "$HOME"/.arkheionx|"$HOME"/.arkheionx/*) : ;;
    */.arkheionx|*/.arkheionx/*) : ;;
    *)
        err "Refusing to operate on non-Arkheionx path: $ARKHEIONX_INSTALL_DIR"
        err "Set ARKHEIONX_INSTALL_DIR to a path ending in .arkheionx."
        exit 2 ;;
esac

remove() {
    target="$1"
    [ -e "$target" ] || { log "skip (absent): $target"; return 0; }
    if [ "$ARKHEIONX_DRY_RUN" = "1" ]; then
        log "DRY-RUN: remove $target"
    else
        rm -rf "$target"
        log "removed: $target"
    fi
}

confirm() {
    [ "$ARKHEIONX_YES" = "1" ] && return 0
    [ "$ARKHEIONX_DRY_RUN" = "1" ] && return 0
    printf 'Remove the paths listed above? [y/N] '
    read -r reply 2>/dev/null || reply=""
    case "$reply" in y|Y|yes|YES) return 0 ;; *) err "Aborted by user."; exit 1 ;; esac
}

show_receipt() {
    rcp="$1"
    [ -f "$rcp" ] || return 0
    log "Found install receipt: $rcp"
    if command -v python3 >/dev/null 2>&1; then
        python3 - "$rcp" <<'PY' 2>/dev/null || log "  (receipt unreadable)"
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    print("  (receipt malformed; will still be removed)"); sys.exit(0)
for key in ("source_kind", "ref", "local_path", "installed_version", "install_method"):
    value = data.get(key)
    if value:
        print(f"  {key}: {value}")
PY
    fi
    log ""
}

main() {
    wrapper="$ARKHEIONX_BIN_DIR/arkheionx"
    venv="$ARKHEIONX_INSTALL_DIR/venv"
    receipt="$ARKHEIONX_INSTALL_DIR/install.json"

    log "Arkheionx uninstaller"
    show_receipt "$receipt"
    log "Will remove only these Arkheionx-managed paths:"
    log "  $wrapper"
    log "  $venv"
    log "  $receipt"
    log "  $ARKHEIONX_INSTALL_DIR (only if empty afterwards)"
    log ""

    confirm
    remove "$wrapper"
    remove "$venv"
    remove "$receipt"

    # Remove the managed bin dir only if it is now empty.
    if [ -d "$ARKHEIONX_BIN_DIR" ] && [ -z "$(ls -A "$ARKHEIONX_BIN_DIR" 2>/dev/null)" ]; then
        remove "$ARKHEIONX_BIN_DIR"
    fi

    if [ -d "$ARKHEIONX_INSTALL_DIR" ]; then
        if [ -z "$(ls -A "$ARKHEIONX_INSTALL_DIR" 2>/dev/null)" ]; then
            remove "$ARKHEIONX_INSTALL_DIR"
        else
            log "kept (not empty): $ARKHEIONX_INSTALL_DIR"
        fi
    fi

    log ""
    if [ "$ARKHEIONX_PIPX_UNINSTALL" = "1" ] && command -v pipx >/dev/null 2>&1; then
        if [ "$ARKHEIONX_DRY_RUN" = "1" ]; then
            log "DRY-RUN: pipx uninstall arkheionx"
        else
            pipx uninstall arkheionx || warn "pipx uninstall arkheionx did not complete."
        fi
    else
        log "If you installed with pipx, also run: pipx uninstall arkheionx"
    fi
    log "Done. No root changes were made and no shell profiles were modified."
}

main
