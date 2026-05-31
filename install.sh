#!/bin/sh
# Arkheionx local installer (v2.7.0 — arkup & install lifecycle).
#
# Safe, local-first, no-root install of the Arkheionx CLI. It prefers pipx and
# falls back to an isolated virtual environment under your home directory, and
# records a local install receipt so `arkup` can inspect and update it.
#
# This script never asks for root, never edits your shell profile, never asks
# for secrets, never makes RPC or live-chain calls, and only ever runs `pip`
# against the Arkheionx repository (or a local checkout) that you point it at.
#
# Usage:
#   sh install.sh [--help] [--dry-run] [--method auto|pipx|venv]
#                 [--channel stable|main] [--ref <git-ref>] [--local <path>]
#
# Source model (precedence: local > ref > channel):
#   stable  default; installs the documented stable tag.
#   main    --channel main; latest development main (opt-in).
#   ref     --ref <tag|branch|sha>; pinned explicit ref.
#   local   --local <path>; install from a local checkout.
#
# Environment (all optional):
#   ARKHEIONX_REPO_URL       Git URL (default: https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git)
#   ARKHEIONX_STABLE_TAG     Stable tag for the stable channel (default: v2.6.0)
#   ARKHEIONX_CHANNEL        stable | main (default: stable)
#   ARKHEIONX_REF            Explicit git ref (sets source kind = ref)
#   ARKHEIONX_LOCAL_PATH     Local checkout path (sets source kind = local)
#   ARKHEIONX_INSTALL_DIR    Base install dir (default: $HOME/.arkheionx)
#   ARKHEIONX_BIN_DIR        Wrapper dir (default: $HOME/.arkheionx/bin)
#   ARKHEIONX_INSTALL_METHOD auto | pipx | venv (default: auto)
#   ARKHEIONX_NO_MODIFY_PATH Always 1; this script never edits shell profiles
#   ARKHEIONX_YES            1 to skip interactive confirmation
#   ARKHEIONX_DRY_RUN        1 to print actions without executing them
set -eu

INSTALLER_VERSION="2.7.0"
ARKHEIONX_REPO_URL="${ARKHEIONX_REPO_URL:-https://github.com/Yudis-bit/DeFi-Exploit-PoCs.git}"
ARKHEIONX_STABLE_TAG="${ARKHEIONX_STABLE_TAG:-v2.7.0}"
ARKHEIONX_CHANNEL="${ARKHEIONX_CHANNEL:-stable}"
ARKHEIONX_REF="${ARKHEIONX_REF:-}"
ARKHEIONX_LOCAL_PATH="${ARKHEIONX_LOCAL_PATH:-}"
ARKHEIONX_INSTALL_DIR="${ARKHEIONX_INSTALL_DIR:-$HOME/.arkheionx}"
ARKHEIONX_BIN_DIR="${ARKHEIONX_BIN_DIR:-$ARKHEIONX_INSTALL_DIR/bin}"
ARKHEIONX_INSTALL_METHOD="${ARKHEIONX_INSTALL_METHOD:-auto}"
ARKHEIONX_NO_MODIFY_PATH=1
ARKHEIONX_YES="${ARKHEIONX_YES:-0}"
ARKHEIONX_DRY_RUN="${ARKHEIONX_DRY_RUN:-0}"
MIN_PY_MINOR=11
SOURCE_KIND=stable
INSTALL_METHOD=""
CMD_PATH=""

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
  --help              Show this help and exit.
  --dry-run           Print what would happen without changing anything.
  --method VALUE      Install method: auto (default), pipx, or venv.
  --channel VALUE     Source channel: stable (default) or main.
  --ref VALUE         Install a pinned git ref (tag, branch, or sha).
  --local PATH        Install from a local repository checkout.

Source model (precedence: local > ref > channel):
  stable  installs the documented stable tag (default).
  main    latest development main (opt-in, --channel main).
  ref     pinned explicit ref (--ref vX.Y.Z).
  local   install from a local checkout (--local PATH).

The installer is local-first: no root, no shell-profile edits, no secrets,
no RPC, and no live-chain calls. Arkheionx is not published to PyPI; it is
installed from the GitHub repository or a local checkout. On success it writes
a local install receipt to $ARKHEIONX_INSTALL_DIR/install.json.

After install, add the bin dir to your PATH and run `arkheionx doctor`.
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --dry-run) ARKHEIONX_DRY_RUN=1 ;;
        --method) shift; ARKHEIONX_INSTALL_METHOD="${1:-auto}" ;;
        --channel) shift; ARKHEIONX_CHANNEL="${1:-stable}" ;;
        --ref) shift; ARKHEIONX_REF="${1:-}" ;;
        --local) shift; ARKHEIONX_LOCAL_PATH="${1:-}" ;;
        *) err "unknown option: $1"; usage; exit 2 ;;
    esac
    shift
done

resolve_source() {
    if [ -n "$ARKHEIONX_LOCAL_PATH" ]; then
        SOURCE_KIND=local
    elif [ -n "$ARKHEIONX_REF" ]; then
        SOURCE_KIND=ref
    elif [ "$ARKHEIONX_CHANNEL" = "main" ]; then
        SOURCE_KIND=main
        ARKHEIONX_REF=main
    else
        SOURCE_KIND=stable
        ARKHEIONX_REF="$ARKHEIONX_STABLE_TAG"
    fi
}

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
    if [ "$SOURCE_KIND" = "local" ]; then
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
    CMD_PATH="$(command -v arkheionx 2>/dev/null || true)"
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
    CMD_PATH="$wrapper"
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
    INSTALL_METHOD="$method"
    log "Install method: $method"
}

installed_version() {
    v=""
    if [ -n "$CMD_PATH" ] && [ -x "$CMD_PATH" ]; then
        v="$("$CMD_PATH" version 2>/dev/null | sed -n 's/^Arkheionx package version: //p' | head -1)"
    fi
    [ -n "$v" ] && printf '%s' "$v" || printf 'unknown'
}

write_receipt() {
    receipt="$ARKHEIONX_INSTALL_DIR/install.json"
    if [ "$ARKHEIONX_DRY_RUN" = "1" ]; then
        log "DRY-RUN: write install receipt $receipt"
        return 0
    fi
    A_RECEIPT_PATH="$receipt" \
    A_TOOL="arkheionx" \
    A_METHOD="$INSTALL_METHOD" \
    A_SOURCE_KIND="$SOURCE_KIND" \
    A_REPO_URL="$ARKHEIONX_REPO_URL" \
    A_REF="$ARKHEIONX_REF" \
    A_LOCAL_PATH="$ARKHEIONX_LOCAL_PATH" \
    A_INSTALL_DIR="$ARKHEIONX_INSTALL_DIR" \
    A_BIN_DIR="$ARKHEIONX_BIN_DIR" \
    A_CMD_PATH="$CMD_PATH" \
    A_PY="$(command -v "$PYTHON" 2>/dev/null || printf '%s' "$PYTHON")" \
    A_VERSION="$(installed_version)" \
    A_INSTALLER_VERSION="$INSTALLER_VERSION" \
    "$PYTHON" - <<'PY'
import datetime, json, os
path = os.environ["A_RECEIPT_PATH"]
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
installed_at = now
try:
    with open(path, encoding="utf-8") as handle:
        installed_at = json.load(handle).get("installed_at", now)
except Exception:
    pass
data = {
    "schema_version": 1,
    "tool": os.environ["A_TOOL"],
    "installed_at": installed_at,
    "updated_at": now,
    "install_method": os.environ["A_METHOD"],
    "source_kind": os.environ["A_SOURCE_KIND"],
    "repo_url": os.environ.get("A_REPO_URL", ""),
    "ref": os.environ.get("A_REF", ""),
    "local_path": os.environ.get("A_LOCAL_PATH", ""),
    "install_dir": os.environ["A_INSTALL_DIR"],
    "bin_dir": os.environ["A_BIN_DIR"],
    "command_path": os.environ.get("A_CMD_PATH", ""),
    "detected_python": os.environ.get("A_PY", ""),
    "installed_version": os.environ.get("A_VERSION", ""),
    "installer_version": os.environ.get("A_INSTALLER_VERSION", ""),
    "notes": "",
}
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY
    log "Install receipt: $receipt"
}

main() {
    log "Arkheionx installer"
    log "Note: local-first install. No root, no profile edits, no secrets, no RPC."
    log "Arkheionx is not published to PyPI; installing from repo/local checkout."
    resolve_source
    detect_os
    find_python
    if [ "$SOURCE_KIND" = "local" ]; then
        log "Source: local checkout $ARKHEIONX_LOCAL_PATH (kind: local)"
    else
        log "Source: $ARKHEIONX_REPO_URL @ $ARKHEIONX_REF (kind: $SOURCE_KIND)"
    fi
    confirm
    choose_and_install
    write_receipt
    log ""
    log "Next steps:"
    log "  ${PATH_HINT:-export PATH=\"$ARKHEIONX_BIN_DIR:\$PATH\"}"
    log "  arkheionx version"
    log "  arkheionx doctor --install"
    log "  arkheionx open ."
    log ""
    log "Done. This installer made no system-wide or root changes."
}

main
