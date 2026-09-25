#!/bin/sh
# Install Token Visualizer from the latest GitHub release.
#
#   curl -fsSL https://raw.githubusercontent.com/Mattbusel/Token-Visualizer/main/install.sh | sh
#
# Options (environment variables):
#   INSTALL_DIR=/some/dir   where to put the binary (default: ~/.local/bin)
#   INSTALL_VERSION=v1.2.3  install a specific release instead of the latest
#
# It downloads the archive for your OS and CPU, checks it against the release's
# SHA256SUMS.txt, and copies one file (token-visualizer) into INSTALL_DIR. Nothing else.
set -eu

REPO="Mattbusel/Token-Visualizer"
PREFIX="token-visualizer"      # archive name prefix
BIN="token-visualizer"            # file name inside the archive
CMD="token-visualizer"            # command name you will type
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "this installer needs '$1'; install it and try again"; }

need curl
need tar
need uname

os="$(uname -s)"
arch="$(uname -m)"
ext="tar.gz"
exe=""
case "$os" in
  Linux)
    case "$arch" in
      x86_64|amd64) target="linux-x86_64" ;;
      *) die "no prebuilt Linux binary for $arch yet; use: pipx install git+https://github.com/$REPO" ;;
    esac ;;
  Darwin)
    case "$arch" in
      arm64|aarch64) target="macos-arm64" ;;
      x86_64) target="macos-x86_64" ;;
      *) die "unsupported macOS CPU: $arch" ;;
    esac ;;
  MINGW*|MSYS*|CYGWIN*)
    target="windows-x86_64"; ext="zip"; exe=".exe"; need unzip ;;
  *) die "unsupported OS: $os (on Windows PowerShell use install.ps1 instead)" ;;
esac

if [ -n "${INSTALL_VERSION:-}" ]; then
  tag="$INSTALL_VERSION"
else
  # The /releases/latest page redirects to /releases/tag/<tag>; no API token needed.
  url="$(curl -fsSLI -o /dev/null -w '%{url_effective}' "https://github.com/$REPO/releases/latest")" \
    || die "could not reach github.com; check your connection"
  tag="${url##*/}"
  case "$tag" in v*) ;; *) die "could not find the latest release of $REPO" ;; esac
fi

name="$PREFIX-$tag-$target"
base="https://github.com/$REPO/releases/download/$tag"
tmp="$(mktemp -d 2>/dev/null || mktemp -d -t "$CMD")"
trap 'rm -rf "$tmp"' EXIT INT TERM

say "Downloading $name.$ext ..."
curl -fsSL -o "$tmp/$name.$ext" "$base/$name.$ext" || die "download failed: $base/$name.$ext"
curl -fsSL -o "$tmp/SHA256SUMS.txt" "$base/SHA256SUMS.txt" || die "could not download SHA256SUMS.txt"

expected="$(grep " \*\{0,1\}$name.$ext\$" "$tmp/SHA256SUMS.txt" | cut -d' ' -f1)"
[ -n "$expected" ] || die "$name.$ext is not listed in SHA256SUMS.txt"
if command -v sha256sum >/dev/null 2>&1; then
  actual="$(sha256sum "$tmp/$name.$ext" | cut -d' ' -f1)"
elif command -v shasum >/dev/null 2>&1; then
  actual="$(shasum -a 256 "$tmp/$name.$ext" | cut -d' ' -f1)"
else
  die "need sha256sum or shasum to verify the download"
fi
[ "$expected" = "$actual" ] || die "checksum mismatch for $name.$ext (expected $expected, got $actual); not installing"
say "Checksum OK."

if [ "$ext" = "zip" ]; then
  unzip -q "$tmp/$name.$ext" -d "$tmp"
else
  tar xzf "$tmp/$name.$ext" -C "$tmp"
fi
[ -f "$tmp/$name/$BIN$exe" ] || die "archive did not contain $BIN$exe"

mkdir -p "$INSTALL_DIR"
cp "$tmp/$name/$BIN$exe" "$INSTALL_DIR/$CMD$exe"
chmod +x "$INSTALL_DIR/$CMD$exe"
if [ "$os" = "Darwin" ] && command -v xattr >/dev/null 2>&1; then
  xattr -d com.apple.quarantine "$INSTALL_DIR/$CMD$exe" 2>/dev/null || true
fi

say "Installed $CMD $tag to $INSTALL_DIR/$CMD$exe"
case ":$PATH:" in
  *":$INSTALL_DIR:"*) say "Try it: token-visualizer --help" ;;
  *) say ""
     say "$INSTALL_DIR is not on your PATH yet. Add this line to ~/.bashrc or ~/.zshrc:"
     say "  export PATH=\"$INSTALL_DIR:\$PATH\""
     say "Then open a new terminal and run: token-visualizer --help" ;;
esac
