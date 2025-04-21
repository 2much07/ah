@echo off
echo Running ARK Character Implant Manager...

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Requesting Admin privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~fnx0' -Verb RunAs"
    exit /b
)

:: Get the directory where the batch file is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..

:: Set Python path to include project modules
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

:: Run the character implant module
cd /d %PROJECT_ROOT%
python -m modules.character_implant.character_implant_ui

echo.
echo Press any key to exit...
pause > nul