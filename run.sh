#!/usr/bin/env bash
# One-command launch. Runs fully on mock data — no API keys required.
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
[ -f .env ] && set -a && . ./.env && set +a
echo "▸ Verdict on http://localhost:8000"
exec .venv/bin/uvicorn verdict.server:app --host 127.0.0.1 --port 8000 --log-level warning
