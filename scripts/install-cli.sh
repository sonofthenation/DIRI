#!/usr/bin/env sh
set -eu

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL_BIN="$HOME/.local/bin"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
UV_LINK_MODE=copy uv tool install --editable . --force

case ":$PATH:" in
  *":$TOOL_BIN:"*) ;;
  *)
    echo "DIRI was installed, but $TOOL_BIN is not in PATH."
    echo "Add this line to your shell profile, then restart your terminal:"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    ;;
esac

echo "DIRI CLI installed. Try: diri --help"
