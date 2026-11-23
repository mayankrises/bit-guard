#!/usr/bin/env bash
# Starts mock backend (8444) + frontend (8000). Open http://localhost:8000
set -e
cd "$(dirname "$0")"
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q fastapi "uvicorn[standard]" jinja2 requests redis pandas pydantic
(cd mock_backend && uvicorn mock_api:app --port 8444) &
BACK=$!
trap "kill $BACK" EXIT
cd frontend
BACKEND_URL=http://localhost:8444 uvicorn app.main:app --port 8000
