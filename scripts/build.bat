@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%\.."

set "PYTHON_CMD=python"
where py >nul 2>nul
if %errorlevel%==0 set "PYTHON_CMD=py -3"

%PYTHON_CMD% tools\build.py src bin %*
set "BUILD_EXIT=%errorlevel%"

popd
exit /b %BUILD_EXIT%