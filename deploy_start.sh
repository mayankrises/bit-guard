#!/bin/sh
# Starts the mock backend (internal, 8444) and the frontend (public, $PORT)
cd /app/mock_backend && uvicorn mock_api:app --host 127.0.0.1 --port 8444 &

cd /app/frontend
export BACKEND_URL="http://127.0.0.1:8444"
export REDIS_HOST="${REDIS_HOST:-localhost}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
