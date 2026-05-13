#!/usr/bin/env bash
# Syntra API — yerel geliştirme (Linux / macOS)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8000}"
exec python -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port "$PORT" \
  --reload \
  --reload-dir app
