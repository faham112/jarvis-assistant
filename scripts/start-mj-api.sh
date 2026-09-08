#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
export MJ_API_KEY="${MJ_API_KEY:-change-me}"
exec uvicorn api_server:app --host 0.0.0.0 --port 8080
