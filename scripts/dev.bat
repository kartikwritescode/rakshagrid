@echo off
rem scripts/dev.bat - Launch local development servers on Windows
echo ======================================================================
echo   Starting Raksha Grid Production Monorepo Dev Servers...
echo ======================================================================

rem Determine repository root directory reliably from script location
for %%i in ("%~dp0..") do set "ROOT_DIR=%%~fi"
cd /d "%ROOT_DIR%"

rem Kill any orphan processes on port 3000 and 8000
echo [*] Checking and releasing ports 3000 and 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1

rem Resolve Python environment and verify uvicorn
set "PYTHON_EXE="

if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (
    "%ROOT_DIR%\.venv\Scripts\python.exe" -c "import uvicorn" >nul 2>&1
    if errorlevel 1 (
        echo [!] .venv detected but uvicorn is missing. Installing backend dependencies...
        "%ROOT_DIR%\.venv\Scripts\python.exe" -m pip install -r "%ROOT_DIR%\requirements.txt"
        "%ROOT_DIR%\.venv\Scripts\python.exe" -m pip install -e "%ROOT_DIR%\packages\common" -e "%ROOT_DIR%\packages\ai-scam" -e "%ROOT_DIR%\packages\ai-currency" -e "%ROOT_DIR%\packages\ai-crime" -e "%ROOT_DIR%\packages\ai-graph" -e "%ROOT_DIR%\apps\api"
    )
    echo [OK] Using virtual environment: .venv
    set "PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe"
)

if not defined PYTHON_EXE (
    py -3.12 -c "import uvicorn" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Using Python 3.12
        set "PYTHON_EXE=py -3.12"
    )
)

if not defined PYTHON_EXE (
    python -c "import uvicorn" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Using system Python
        set "PYTHON_EXE=python"
    ) else (
        echo [!] uvicorn is not found. Installing requirements...
        python -m pip install -r "%ROOT_DIR%\requirements.txt"
        set "PYTHON_EXE=python"
    )
)

rem Check frontend node_modules
if not exist "%ROOT_DIR%\apps\web\node_modules" (
    echo [*] Frontend dependencies missing. Running npm install in apps\web...
    cd /d "%ROOT_DIR%\apps\web" && call npm install && cd /d "%ROOT_DIR%"
)

echo.
echo [*] Launching FastAPI Backend on http://localhost:8000 ...
if exist "%ROOT_DIR%\.venv\Scripts\activate.bat" (
    start "RakshaGrid FastAPI Backend" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn apps.api.src.main:app --host 0.0.0.0 --port 8000 --reload"
) else (
    start "RakshaGrid FastAPI Backend" cmd /k "%PYTHON_EXE% -m uvicorn apps.api.src.main:app --host 0.0.0.0 --port 8000 --reload"
)

echo [*] Launching Next.js Frontend on http://localhost:3000 ...
start "RakshaGrid Next.js Frontend" cmd /k "cd apps\web && npm run dev"

echo.
echo ======================================================================
echo   Raksha Grid is running:
echo     - Backend API:    http://localhost:8000
echo     - API Swagger UI: http://localhost:8000/docs
echo     - Frontend App:   http://localhost:3000
echo ======================================================================
