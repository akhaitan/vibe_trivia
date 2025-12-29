#!/bin/bash
# Build script for Render deployment
# Handles Rust/Cargo setup for pydantic-core compilation

set -e

echo "Setting up build environment..."

# CRITICAL: Set Cargo environment variables FIRST, before any commands
# These must be exported before pip tries to install pydantic-core
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup
export CARGO_TARGET_DIR=/tmp/cargo-target
export CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse

# Create writable directories
mkdir -p /tmp/cargo /tmp/rustup /tmp/cargo-target
mkdir -p /tmp/cargo/registry/index
mkdir -p /tmp/cargo/registry/cache

# Install Rust toolchain if not present (needed for pydantic-core compilation)
if ! command -v rustc &> /dev/null; then
    echo "Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --no-modify-path
    export PATH="$HOME/.cargo/bin:$PATH"
    # After installation, use user's cargo directory
    export CARGO_HOME="$HOME/.cargo"
    export RUSTUP_HOME="$HOME/.rustup"
    mkdir -p "$HOME/.cargo" "$HOME/.rustup"
else
    # Ensure default toolchain is set
    if command -v rustup &> /dev/null; then
        rustup default stable 2>/dev/null || {
            rustup toolchain install stable
            rustup default stable
        }
    fi
fi

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
# pydantic-core will compile, but now Cargo can write to /tmp or $HOME
echo "Installing dependencies (this may take a few minutes for pydantic-core)..."
pip install -r requirements.txt

echo "Build completed successfully!"

