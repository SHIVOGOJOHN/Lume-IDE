@echo off
setlocal
cd /d "%~dp0"

set "SCRIPT=luau_ide.py"
set "ICON=logo.ico"
set "PNG=logo.png"
set "OUTPUT=Lume.exe"
set "PRODUCT=Lume"
set "VERSION=0.9.0"
set "DESCRIPTION=Luau desktop IDE with integrated terminal and project tools"
set "LUAU_SOURCE="

if not exist "%SCRIPT%" (
  echo Missing %SCRIPT%
  exit /b 1
)

if exist "luau.exe" (
  set "LUAU_SOURCE=luau.exe"
) else if exist "C:\luau\luau.exe" (
  set "LUAU_SOURCE=C:\luau\luau.exe"
)

set "LUAU_FLAG="
if defined LUAU_SOURCE (
  set "LUAU_FLAG=--include-data-files=%LUAU_SOURCE%=luau.exe"
)

python -m nuitka ^
  --standalone ^
  --onefile ^
  --enable-plugin=tk-inter ^
  --assume-yes-for-downloads ^
  --windows-console-mode=disable ^
  --windows-icon-from-ico=%ICON% ^
  --output-filename=%OUTPUT% ^
  --product-name=%PRODUCT% ^
  --file-description="%DESCRIPTION%" ^
  --company-name=%PRODUCT% ^
  --product-version=%VERSION% ^
  --file-version=%VERSION% ^
  --copyright="Copyright (c) 2026 %PRODUCT%" ^
  --include-data-files=%PNG%=%PNG% ^
  --include-data-dir=assets=assets ^
  %LUAU_FLAG% ^
  %SCRIPT%

endlocal
