@echo off
REM Java Mermaid Flowchart Generator Setup for Windows

echo Java Mermaid Flowchart Generator Setup
echo ======================================

REM Check if we're running from the correct directory
if not exist "java_mermaid\__main__.py" (
    echo Error: This script must be run from the root directory of the Java Mermaid project
    echo Please navigate to the directory containing this setup script and java_mermaid folder
    pause
    exit /b 1
)

echo Checking for Python...
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo Python found
    set PYTHON_CMD=python
    goto check_pip
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    echo Python3 found
    set PYTHON_CMD=python3
    goto check_pip
)

echo Error: Python not found in PATH
echo Please install Python 3.6 or higher from https://www.python.org/downloads/
pause
exit /b 1

:check_pip
echo Checking for pip...
%PYTHON_CMD% -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: pip not found. Please ensure pip is installed with Python.
    pause
    exit /b 1
)

echo Installing required Python packages...
%PYTHON_CMD% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Warning: Failed to install packages from requirements.txt
    echo You may need to install packages manually:
    echo   pip install javalang==0.13.1 requests==2.27.1 click==8.0.4
    echo.
)

echo.
echo Setup completed!
echo.
echo To use the Java Mermaid Flowchart Generator:
echo 1. Set your API key as environment variable:
echo    set OPENAI_API_KEY=your-api-key-here
echo.
echo 2. Run the generator using the batch file:
echo    java-mermaid.bat ClassName methodName File.java
echo.
echo 3. Or run directly with Python:
echo    python -m java_mermaid ClassName methodName File.java
echo.
echo For more information, see the README.md file.
echo.
pause