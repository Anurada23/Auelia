@echo off
echo ====================================
echo Starting Finder AI v2...
echo ====================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import langchain" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements-minimal.txt
)

REM Start the application
echo.
echo Starting server...
python run.py

pause