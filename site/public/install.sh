#!/usr/bin/env bash
# ArkheionX official source installer
# Website: https://arkheionx.dev
# Source:  https://github.com/Yudis-bit/arkheionx
#
# Recommended first-use path:
#   curl -fsSL https://arkheionx.dev/install.sh -o arkheionx-install.sh
#   less arkheionx-install.sh
#   bash arkheionx-install.sh
#
# Direct install:
#   curl -fsSL https://arkheionx.dev/install.sh | bash
#
# This installer:
# - clones or updates the public GitHub source checkout
# - creates a local Python virtual environment
# - installs ArkheionX in editable source mode
# - creates local command wrappers
#
# This installer does not:
# - ask for private keys, seed phrases, or secrets
# - call RPC endpoints by default
# - run live-chain transactions
# - run exploit tests during installation
# - confirm vulnerabilities or produce audit conclusions

set -euo pipefail

REPO_URL="https://github.com/Yudis-bit/arkheionx.git"
BRANCH="main"
ARKHEIONX_HOME="${ARKHEIONX_HOME:-$HOME/.arkheionx}"
SRC_DIR="$ARKHEIONX_HOME/src"
VENV_DIR="$ARKHEIONX_HOME/venv"
BIN_DIR="${ARKHEIONX_BIN_DIR:-$HOME/.local/bin}"
ARKHEIONX_WRAPPER="$BIN_DIR/arkheionx"
ARKUP_WRAPPER="$BIN_DIR/arkup"

log() {
  printf 'arkheionx: %s\n' "$*"
}

fail() {
  printf 'arkheionx: error: %s\n' "$*" >&2
  exit 1
}

case "$(uname -s 2>/dev/null || true)" in
  Linux|Darwin) ;;
  *) fail "supported operating systems are Linux and macOS" ;;
esac

command -v git >/dev/null 2>&1 || fail "git is required"
command -v python3 >/dev/null 2>&1 || fail "python3 is required"

python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
  || fail "Python 3.11 or newer is required"

mkdir -p "$ARKHEIONX_HOME" "$BIN_DIR"

if [ -d "$SRC_DIR/.git" ]; then
  origin_url="$(git -C "$SRC_DIR" remote get-url origin)"
  [ "$origin_url" = "$REPO_URL" ] || fail "$SRC_DIR has an unexpected origin: $origin_url"
  log "updating public source checkout"
  git -C "$SRC_DIR" fetch origin "$BRANCH"
  git -C "$SRC_DIR" checkout "$BRANCH"
  git -C "$SRC_DIR" merge --ff-only "origin/$BRANCH"
elif [ -e "$SRC_DIR" ]; then
  fail "$SRC_DIR exists but is not an ArkheionX Git checkout"
else
  log "cloning public source"
  git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$SRC_DIR"
fi

log "creating isolated Python environment"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check --no-build-isolation -e "$SRC_DIR"

cat > "$ARKHEIONX_WRAPPER" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/arkheionx" "\$@"
EOF
chmod 0755 "$ARKHEIONX_WRAPPER"

if [ -f "$SRC_DIR/arkup" ]; then
  cat > "$ARKUP_WRAPPER" <<EOF
#!/usr/bin/env bash
exec bash "$SRC_DIR/arkup" "\$@"
EOF
  chmod 0755 "$ARKUP_WRAPPER"
fi

log "verifying installation"
"$ARKHEIONX_WRAPPER" version

printf '\nInstalled wrappers:\n'
printf '  %s\n' "$ARKHEIONX_WRAPPER"
[ -x "$ARKUP_WRAPPER" ] && printf '  %s\n' "$ARKUP_WRAPPER"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    printf '\nAdd this directory to PATH in your shell configuration:\n'
    printf '  export PATH="%s:$PATH"\n' "$BIN_DIR"
    ;;
esac

printf '\nNext commands:\n'
printf '  arkheionx doctor --install\n'
printf '  arkheionx demo --list\n'
printf '  arkheionx review-map /path/to/authorized/repository\n'
