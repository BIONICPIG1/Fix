@echo off
setlocal
set "FIX_ROOT=%~dp0"
if not defined MSYS2_ROOT set "MSYS2_ROOT=C:\msys64"
set "FIX_UCRT_BIN=%MSYS2_ROOT%\ucrt64\bin"
set "FIX_PYTHON=%FIX_UCRT_BIN%\python.exe"

if not exist "%FIX_PYTHON%" (
    echo [ERROR] MSYS2 UCRT64 Python not found: "%FIX_PYTHON%"
    echo Install MSYS2 UCRT64 and the dependencies in docs\WINDOWS_SETUP.md.
    echo If MSYS2 was installed elsewhere, set MSYS2_ROOT to that directory.
    exit /b 1
)

rem Include the DLLs/FFmpeg from the same MSYS2 installation as Python.
set "PATH=%FIX_UCRT_BIN%;%MSYS2_ROOT%\usr\bin;%PATH%"
"%FIX_PYTHON%" "%FIX_ROOT%scripts\check_dependencies.py"
if errorlevel 1 exit /b 1

if /I "%~1"=="--check" exit /b 0
if /I "%~1"=="--test" (
    "%FIX_PYTHON%" -m pytest -q "%FIX_ROOT%tests"
    if errorlevel 1 exit /b 1
    exit /b 0
)

"%FIX_PYTHON%" "%FIX_ROOT%app.py" %*
exit /b %ERRORLEVEL%
