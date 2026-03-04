#!/bin/bash
set -e

# Extractversion from pyproject.toml
TOOLBOX_VERSION=$(grep -o '^toolbox_version = "[^"]*"' pyproject.toml | cut -d '"' -f 2)

if [ -z "$TOOLBOX_VERSION" ]; then
    echo "Error: Could not find toolbox_version in pyproject.toml"
    exit 1
fi

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH="arm64"
fi

if [ "$OS" = "mingw64_nt"* ] || [ "$OS" = "msys_nt"* ] || [ "$OS" = "cygwin_nt"* ]; then
    OS="windows"
    EXT=".exe"
else
    EXT=""
fi

DOWNLOAD_URL="https://storage.googleapis.com/genai-toolbox/v${TOOLBOX_VERSION}/${OS}/${ARCH}/toolbox${EXT}"

echo "Downloading genai-toolbox v${TOOLBOX_VERSION} for ${OS}/${ARCH}..."
curl -L --fail -o "toolbox${EXT}" "${DOWNLOAD_URL}"

if [ -n "$EXT" ]; then
    chmod +x "toolbox${EXT}"
else
    chmod +x "toolbox"
fi

echo "Successfully installed toolbox binary."
