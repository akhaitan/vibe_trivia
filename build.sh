#!/bin/bash
# Build script for Render deployment
# Sets up environment to prevent Rust/Cargo compilation issues

set -e

echo "Setting up build environment..."

# Set environment variables to allow Cargo to write to /tmp
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup

# Upgrade pip first
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"

