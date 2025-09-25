#!/bin/bash
set -euo pipefail

echo "=== ULTRA SIMPLE STARTUP ==="
echo "Environment: ${ENVIRONMENT:-not_set}"
echo "Port: ${PORT:-8080}"
echo "============================="

echo "Starting simple HTTP server on port ${PORT:-8080}..."
python3 -m http.server ${PORT:-8080}
