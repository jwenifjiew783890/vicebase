#!/usr/bin/env bash
# Vision installer for Linux and macOS.
#
#   bash install/install.sh                # install to ~/.local/share/vision
#   bash install/install.sh --skip-models  # set up the app, fetch models later
#   VISION_INSTALL_DIR=/opt/vision bash install/install.sh
#
# Creates a private virtualenv, installs dependencies, downloads models and
# writes a `vision` launcher. Nothing is installed system-wide except the
# launcher symlink, and that only if ~/.local/bin exists.
set -euo pipefail

DIR="${VISION_INSTALL_DIR:-$HOME/.local/share/vision}"
SKIP_MODELS=0
for a in "$@"; do [ "$a" = "--skip-models" ] && SKIP_MODELS=1; done

cyan(){ printf '\033[36m%s\033[0m\n' "$1"; }
say(){  printf '  %s\n' "$1"; }
die(){  printf '\033[31m  %s\033[0m\n' "$1"; exit 1; }

cat <<'BANNER'
====================================================
  VISION - personal AI assistant
====================================================
BANNER

cyan "Checking Python"
PY=""
for c in python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null 2>&1; then
    v=$("$c" -c 'import sys;print(sys.version_info[:2]>=(3,10))' 2>/dev/null || echo False)
    [ "$v" = "True" ] && { PY="$c"; break; }
  fi
done
[ -n "$PY" ] || die "Python 3.10+ is required. Install it and run this again."
say "using $PY ($($PY --version 2>&1))"

cyan "Installing to $DIR"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$DIR"
for item in vision requirements.txt VISION.md LICENSE; do
  [ -e "$SRC/$item" ] && cp -r "$SRC/$item" "$DIR/" && say "copied $item"
done

cyan "Creating a private Python environment"
"$PY" -m venv "$DIR/.venv" || die "could not create a virtualenv (need python3-venv)"
VPY="$DIR/.venv/bin/python"
say "venv at $DIR/.venv"

cyan "Installing dependencies (a few minutes)"
"$VPY" -m pip install --upgrade pip --quiet
"$VPY" -m pip install -r "$DIR/requirements.txt" --quiet \
  || die "dependency install failed -- scroll up for the reason"
say "dependencies installed"

cyan "Installing the browser for the browser agent (~150 MB)"
if "$VPY" -m playwright install chromium >/dev/null 2>&1; then
  say "chromium installed"
else
  say "chromium install failed -- the browser agent will report itself"
  say "unavailable until you run '$VPY -m playwright install chromium'"
fi

if [ "$SKIP_MODELS" -eq 0 ]; then
  cyan "Downloading models (~2.9 GB, resumable)"
  (cd "$DIR" && "$VPY" -m vision.setup_models) || \
    say "some downloads failed -- re-run '$VPY -m vision.setup_models'"
else
  say "skipped models -- run '$VPY -m vision.setup_models' later"
fi

cyan "Creating the launcher"
# In bin/, not at the top: $DIR/vision is the package directory we just
# copied, and writing the launcher there fails with "Is a directory".
mkdir -p "$DIR/bin"
cat > "$DIR/bin/vision" <<LAUNCH
#!/usr/bin/env bash
cd "$DIR"
exec "$DIR/.venv/bin/python" -m vision "\$@"
LAUNCH
chmod +x "$DIR/bin/vision"
if [ -d "$HOME/.local/bin" ]; then
  ln -sf "$DIR/bin/vision" "$HOME/.local/bin/vision"
  say "launcher: vision (on your PATH)"
else
  say "launcher: $DIR/bin/vision"
fi

cyan "Checking the installation"
(cd "$DIR" && "$VPY" -m vision --check) || true

cat <<DONE

====================================================
  Installed.

  Launch it:   $DIR/bin/vision
  Then open:   http://127.0.0.1:8765

  Connect your Obsidian vault in Settings, or set
      VISION_VAULT=/path/to/your/vault
====================================================
DONE
