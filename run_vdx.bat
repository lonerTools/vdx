@echo off
setlocal enabledelayedexpansion

:: paths
set "SCRIPT_DIR=%~dp0"
set "USER_SSDX=%USERPROFILE%\.ssdx\vdx_reports"
set "LOCAL_VDX_P_DIR=%SCRIPT_DIR%vdx_reports"

:: colors
set "YLW=[93m"
set "BYL=[1;93m"
set "RED=[91m"
set "BRD=[1;91m"
set "GRN=[32m"
set "BGN=[1;32m"
set "BLD=[1m"
set "RST=[0m"

:MENU
cls
echo %BLD%==================================================%RST%
echo               %YLW%VDX%RST% REPORT RUNNER
echo %BLD%==================================================%RST%
echo   %BLD%[1] Run vdx.py      (Saves to:%YLW% %USER_SSDX%)%RST%
echo   %BLD%[2] Run vdx-p.py    (Saves to:%YLW% %LOCAL_VDX_P_DIR%)%RST%
echo   [%BRD%3%RST%] %BLD%Exit%RST%
echo %BLD%==================================================%RST%
echo.
echo.
set /p "choice=  %BLD%Select an option (1-3): %RST%"

if "%choice%"=="1" goto RUN_VDX
if "%choice%"=="2" goto RUN_VDX_P
if "%choice%"=="3" exit /b 0

echo %BRD%Invalid%RST% choice. Please try again.
timeout /t 2 >nul
goto MENU

:RUN_VDX
echo.
echo Running %BYL%vdx.py%RST% ...
cd /d "%SCRIPT_DIR%"
python "%SCRIPT_DIR%vdx.py"
echo.
echo Done. Press %BGN%Enter%RST% to return to the menu.
pause >nul
goto MENU

:RUN_VDX_P
echo.
echo Running %BYL%vdx-p.py%RST% ...
cd /d "%SCRIPT_DIR%"
python "%SCRIPT_DIR%vdx-p.py"
echo.
echo Done. Press %BGN%Enter%RST% to return to the menu.
pause >nul
goto MENU