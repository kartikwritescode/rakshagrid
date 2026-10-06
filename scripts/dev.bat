@echo off
rem scripts/dev.bat - Launch local development servers on Windows
echo ==================================================
echo Starting Raksha Grid Production Monorepo Dev Servers...
echo ==================================================

rem Store root path
set ROOT_DIR=%CD%

rem Kill any orphan processes on port 3000 and 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

start "RakshaGrid FastAPI Backend" cmd /k "cd /d %ROOT_DIR% && python -m uvicorn rakshagrid.api.main:app --host 0.0.0.0 --port 8000 --reload"
start "RakshaGrid Next.js Frontend" cmd /k "cd /d %ROOT_DIR%\apps\web && npm run dev"

echo Backend and Frontend dev servers launched successfully.
