@echo off
REM ################################################################################
REM YouTube Twin - Windows Startup Script
REM This script sets up and runs both frontend and backend on Windows
REM ################################################################################

color 0A
echo.
echo ========================================================
echo.
echo              YouTube Twin - Windows Setup
echo           AI-Powered Video Chat Assistant
echo.
echo ========================================================
echo.

REM Check Python installation
echo [1/6] Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Setup Backend
echo [2/6] Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
echo (This may take a few minutes...)
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Please check the error messages above
    echo Common fixes:
    echo 1. Run as Administrator
    echo 2. Check internet connection
    echo 3. Run: python -m pip install --upgrade pip
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Check for .env file
if not exist ".env" (
    echo [WARNING] .env file not found
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
        echo.
        echo ========================================================
        echo IMPORTANT: Please edit backend\.env and add your OpenAI API key
        echo Get your API key from: https://platform.openai.com/api-keys
        echo.
        echo After adding your API key, press any key to continue...
        echo ========================================================
        pause >nul
    ) else (
        echo [ERROR] .env.example not found
        echo Please create backend\.env manually with your OPENAI_API_KEY
        pause
        exit /b 1
    )
)

REM Verify API key
findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
if errorlevel 1 (
    echo [ERROR] OPENAI_API_KEY not configured in .env file
    echo Please add your OpenAI API key to backend\.env
    echo Format: OPENAI_API_KEY=sk-your-key-here
    pause
    exit /b 1
)

echo [OK] Backend setup complete
cd ..
echo.

REM Setup Frontend
echo [3/6] Setting up frontend...
cd frontend

if not exist "index.html" (
    echo [ERROR] Frontend files missing
    echo Please ensure index.html, style.css, and script.js are present
    pause
    exit /b 1
)

echo [OK] Frontend setup complete
cd ..
echo.

REM Kill existing processes on ports
echo [4/6] Checking for existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Stopping process on port 5000...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Stopping process on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] Ports cleared
echo.

REM Start Backend Server
echo [5/6] Starting backend server...
cd backend
start "YouTube Twin Backend" cmd /k "venv\Scripts\activate.bat && python app.py"
echo [OK] Backend server started
echo     API running at: http://localhost:5000
cd ..
echo.

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo [6/6] Starting frontend server...
cd frontend
start "YouTube Twin Frontend" cmd /k "python -m http.server 8000"
echo [OK] Frontend server started
echo     Frontend running at: http://localhost:8000
cd ..
echo.

REM Wait for frontend to start
timeout /t 2 /nobreak >nul

echo.
echo ========================================================
echo           YouTube Twin is now running!
echo ========================================================
echo.
echo  Frontend:    http://localhost:8000
echo  Backend API: http://localhost:5000
echo.
echo  Two command windows have opened:
echo    1. Backend Server (Python Flask)
echo    2. Frontend Server (HTTP Server)
echo.
echo  To stop the servers:
echo    - Close both command windows, or
echo    - Press Ctrl+C in each window
echo.
echo  Opening browser...
echo ========================================================
echo.

REM Open browser
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo Application is ready! You can close this window.
echo The servers will continue running in the other windows.
echo.
pause