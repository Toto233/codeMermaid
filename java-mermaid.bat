@echo off
REM Java Mermaid Flowchart Generator for Windows
REM Usage: java-mermaid.bat CLASS_NAME METHOD_NAME JAVA_FILE [OPTIONS]

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto run_generator
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto run_generator
)

echo Error: Python not found. Please install Python 3.6+ and add it to PATH.
pause
exit /b 1

:run_generator
REM Change to the directory where this script is located
cd /d "%~dp0"

REM Check if java_mermaid module exists
if not exist "java_mermaid\__main__.py" (
    echo Error: java_mermaid module not found.
    echo Make sure this script is in the same directory as the java_mermaid folder.
    pause
    exit /b 1
)

REM Run the generator with all provided arguments
%PYTHON_CMD% -m java_mermaid %*

if %errorlevel% neq 0 (
    echo.
    echo Error running Java Mermaid Flowchart Generator
    pause
    exit /b %errorlevel%
)

echo.
echo Generation completed successfully!
echo Check for .mmd files for clean Mermaid code that can be copied to other tools.
pause