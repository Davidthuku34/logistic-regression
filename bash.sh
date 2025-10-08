#!/usr/bin/env bash
# build.sh - Render build script

set -o errexit  # exit on error

echo "🚀 Starting build process for GenePredict..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"

# Optional: Run any additional setup commands here
# python -c "from db import test_connection; test_connection()"

echo "🧬 GenePredict ready for deployment!"