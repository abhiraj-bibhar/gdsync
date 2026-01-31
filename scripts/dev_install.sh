#!/usr/bin/env bash
set -e

echo "🔧 Setting up gdsync development environment"

# -----------------------------
# Python check
# -----------------------------
if ! command -v python >/dev/null 2>&1; then
  echo "❌ Python not found"
  exit 1
fi

PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✔ Using Python $PYTHON_VERSION"

# -----------------------------
# Upgrade core tooling
# -----------------------------
echo "⬆ Upgrading pip, setuptools, wheel"
python -m pip install --upgrade pip setuptools wheel

# -----------------------------
# Install runtime dependencies
# -----------------------------
echo "📦 Installing gdsync dependencies"
python -m pip install \
  google-api-python-client \
  google-auth \
  google-auth-oauthlib \
  google-auth-httplib2 \
  requests

# -----------------------------
# Install gdsync (editable)
# -----------------------------
echo "🔗 Installing gdsync in editable mode"
python -m pip install -e .

# -----------------------------
# Done
# -----------------------------
echo
echo "✅ gdsync development setup complete"
echo
echo "Try:"
echo "  gdsync --help"
echo "  gdsync auth help"