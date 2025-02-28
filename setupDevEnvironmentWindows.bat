echo off

cd /D "%~dp0"

python -m pip install --upgrade pip setuptools virtualenv

REM Create a virtual environment and activate it
python -m venv venv
call venv\Scripts\activate.bat

REM verify that the venv is activated
if "%VIRTUAL_ENV%" == "" (
    echo "ERROR: virtual environment is not activated"
    pause
    exit 1
 )

REM Install the required packages
%~dp0venv\Scripts\python.exe -m pip install --upgrade pip
%~dp0venv\Scripts\python.exe -m pip install -r requirements-desktop-development.txt

echo:
echo "If you wish to run the GUI from Visual studio code, select the interpreter from the venv folder"
echo "To run the GUI, run the command: runGuiWindows.bat"

pause