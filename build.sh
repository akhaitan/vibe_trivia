#!/bin/bash
# Build script for Render deployment
# Handles Rust/Cargo setup if needed, otherwise uses pure Python packages

set -e

echo "Setting up build environment..."

# Set Cargo to use /tmp if Rust compilation is needed
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup
mkdir -p /tmp/cargo /tmp/rustup

# If rustup exists but has no default, install a default toolchain
if command -v rustup &> /dev/null; then
    echo "Configuring rustup..."
    rustup default stable 2>/dev/null || {
        echo "Installing Rust stable toolchain..."
        rustup toolchain install stable
        rustup default stable
    }
fi

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"

