#!/bin/sh
# Arkheionx local installer (v2.5.0 — Installer & Onboarding).
#
# Safe, local-first, no-root install of the Arkheionx CLI. It prefers pipx and
# falls back to an isolated virtual environment under your home directory.
#
# This script never asks for root, never edits your shell profile, never asks
# for secrets, never makes RPC or live-chain calls, and only ever runs `pip`
# against the Arkheionx repository (or a local checkout) that you point it at.
#
# Usage:
#   sh install.sh [--help] [--dry-run] [--method auto|pipx|venv] [--local <path>]
#
# Environment (all optional):
#   ARKHEIONX_REPO_URL       Git URL to install from
#                            (default: https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git)
#   ARKHEIONX_REF            Git ref to install (default: v2.4.0 stable)
#   ARKHEIONX_INSTALL_DIR    Base install dir (default: $HOME/.arkheionx)
#   ARKHEIONX_BIN_DIR        Wrapper dir (default: $HOME/.arkheionx/bin)
#   ARKHEIONX_INSTALL_METHOD auto | pipx | venv (default: auto)
#   ARKHEIONX_LOCAL_PATH     Install from this local checkout instead of git
#   ARKHEIONX_NO_MODIFY_PATH Always 1; this script never edits shell profiles
#   ARKHEIONX_YES            1 to skip interactive confirmation
#   ARKHEIONX_DRY_RUN        1 to print actions without executing them
set -eu

ARKHEIONX_REPO_URL="${ARKHEIONX_REPO_URL:-https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git}"
ARKHEIONX_REF="${ARKHEIONX_REF:-v2.4.0}"
ARKHEIONX_INSTALL_DIR="${ARKHEIONX_INSTALL_DIR:-$HOME/.arkheionx}"
ARKHEIONX_BIN_DIR="${ARKHEIONX_BIN_DIR:-$ARKHEIONX_INSTALL_DIR/bin}"
ARKHEIONX_INSTALL_METHOD="${ARKHEIONX_INSTALL_METHOD:-auto}"
ARKHEIONX_LOCAL_PATH="${ARKHEIONX_LOCAL_PATH:-}"
ARKHEIONX_NO_MODIFY_PATH=1
ARKHEIONX_YES="${ARKHEIONX_YES:-0}"
ARKHEIONX_DRY_RUN="${ARKHEIONX_DRY_RUN:-0}"
MIN_PY_MINOR=11

log() { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
err() { printf 'error: %s\n' "$*" >&2; }

run() {
    if [ "$ARKHEIONX_DRY_RUN" = "1" ]; then
        log "DRY-RUN: $*"
        return 0
    fi
    "$@"
}

usage() {
    cat <<'EOF'
Arkheionx installer

Usage:
  sh install.sh [options]

Options:
  --help            Show this help and exit.
  --dry-run         Print what would happen without changing anything.
  --method VALUE    Install method: auto (default), pipx, or venv.
  --local PATH      Install from a local repository checkout.

The installer is local-first: no root, no shell-profile edits, no secrets,
no RPC, and no live-chain calls. Arkheionx is not published to PyPI; it is
installed from the GitHub repository or a local checkout.

After install, add the bin dir to your PATH and run `arkheionx doctor`.
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --dry-run) ARKHEIONX_DRY_RUN=1 ;;
        --method) shift; ARKHEIONX_INSTALL_METHOD="${1:-auto}" ;;
        --local) shift; ARKHEIONX_LOCAL_PATH="${1:-}" ;;
        *) err "unknown option: $1"; usage; exit 2 ;;
    esac
    shift
done

detect_os() {
    os="$(uname -s 2>/dev/null || echo unknown)"
    case "$os" in
        Linux|Darwin) log "Detected OS: $os" ;;
        MINGW*|MSYS*|CYGWIN*)
            err "Native Windows shells are not tested. Use WSL2 or a POSIX shell."
            exit 2 ;;
        *) warn "Untested OS '$os'. Continuing, but this is unsupported." ;;
    esac
}

find_python() {
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            minor="$("$candidate" -c 'import sys; print(sys.version_info[1])' 2>/dev/null || echo 0)"
            major="$("$candidate" -c 'import sys; print(sys.version_info[0])' 2>/dev/null || echo 0)"
            if [ "$major" = "3" ] && [ "$minor" -ge "$MIN_PY_MINOR" ] 2>/dev/null; then
                PYTHON="$candidate"
                log "Detected Python: $candidate (3.$minor)"
                return 0
            fi
        fi
    done
    err "Python 3.$MIN_PY_MINOR+ is required but was not found. Install it and retry."
    exit 2
}

pip_source() {
    if [ -n "$ARKHEIONX_LOCAL_PATH" ]; then
        printf '%s' "$ARKHEIONX_LOCAL_PATH"
    else
        printf 'git+%s@%s' "$ARKHEIONX_REPO_URL" "$ARKHEIONX_REF"
    fi
}

confirm() {
    [ "$ARKHEIONX_YES" = "1" ] && return 0
    [ "$ARKHEIONX_DRY_RUN" = "1" ] && return 0
    printf 'Proceed with install? [y/N] '
    read -r reply 2>/dev/null || reply=""
    case "$reply" in y|Y|yes|YES) return 0 ;; *) err "Aborted by user."; exit 1 ;; esac
}

install_pipx() {
    log "Installing Arkheionx with pipx from: $(pip_source)"
    run pipx install --force "$(pip_source)"
    PATH_HINT="pipx ensurepath (then restart your shell)"
}

install_venv() {
    venv="$ARKHEIONX_INSTALL_DIR/venv"
    log "Installing Arkheionx into an isolated venv: $venv"
    run mkdir -p "$ARKHEIONX_INSTALL_DIR" "$ARKHEIONX_BIN_DIR"
    run "$PYTHON" -m venv "$venv"
    run "$venv/bin/python" -m pip install --upgrade pip
    run "$venv/bin/python" -m pip install "$(pip_source)"
    wrapper="$ARKHEIONX_BIN_DIR/arkheionx"
    if [ "$ARKHEIONX_DRY_RUN" = "1" ]; then
        log "DRY-RUN: write wrapper $wrapper -> $venv/bin/arkheionx"
    else
        printf '#!/bin/sh\nexec "%s/bin/arkheionx" "$@"\n' "$venv" >"$wrapper"
        chmod +x "$wrapper"
    fi
    PATH_HINT="export PATH=\"$ARKHEIONX_BIN_DIR:\$PATH\""
}

choose_and_install() {
    method="$ARKHEIONX_INSTALL_METHOD"
    if [ "$method" = "auto" ]; then
        if command -v pipx >/dev/null 2>&1; then method=pipx; else method=venv; fi
    fi
    case "$method" in
        pipx)
            command -v pipx >/dev/null 2>&1 || { err "pipx requested but not installed."; exit 2; }
            install_pipx ;;
        venv) install_venv ;;
        *) err "unknown install method: $method"; exit 2 ;;
    esac
    log "Install method: $method"
}

main() {
    log "Arkheionx installer"
    log "Note: local-first install. No root, no profile edits, no secrets, no RPC."
    log "Arkheionx is not published to PyPI; installing from repo/local checkout."
    detect_os
    find_python
    if [ -n "$ARKHEIONX_LOCAL_PATH" ]; then
        log "Source: local checkout $ARKHEIONX_LOCAL_PATH"
    else
        log "Source: $ARKHEIONX_REPO_URL @ $ARKHEIONX_REF"
    fi
    confirm
    choose_and_install
    log ""
    log "Next steps:"
    log "  ${PATH_HINT:-export PATH=\"$ARKHEIONX_BIN_DIR:\$PATH\"}"
    log "  arkheionx version"
    log "  arkheionx doctor"
    log "  arkheionx open ."
    log ""
    log "Done. This installer made no system-wide or root changes."
}

main
