@echo off
cd /d %~dp0
python -m venv .venv
call .venv\Scripts\activate
pip install -q fastapi "uvicorn[standard]" jinja2 requests redis pandas pydantic
start "mock-backend" cmd /k "cd mock_backend && uvicorn mock_api:app --port 8444"
cd frontend
set BACKEND_URL=http://localhost:8444
uvicorn app.main:app --port 8000
