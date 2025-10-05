#!/bin/bash
set -euo pipefail

echo " Setting up uv for Help Center Backend..."

if ! command -v uv &> /dev/null; then
    echo " Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo " uv version: $(uv --version)"

echo " Creating lock file..."
uv lock

echo " Installing dependencies..."
uv sync

echo " Setup complete! Available commands:"
echo "  uv run python -m graphql-api.main"
echo "  uv run python -m editor-api.main"
echo "  uv add <package>"
echo "  uv remove <package>"
echo "  uv lock"
