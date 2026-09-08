@echo off
title MJ Setup - Windows 11
echo MJ Setup (VPS API)
set /p MJURL=VPS URL [http://136.244.78.245:8080]: 
if "%MJURL%"=="" set MJURL=http://136.244.78.245:8080
set /p MJKEY=API key paste karo: 
if "%MJKEY%"=="" (echo Key khali nahi. & pause & exit /b 1)
echo Checking /activate ...
powershell -NoProfile -Command "try { $r = Invoke-RestMethod -Uri '%MJURL%/activate' -Headers @{ 'X-API-Key' = '%MJKEY%' } -TimeoutSec 12; if ($r.activated) { Write-Host 'MJ ACTIVATE' $r.message; exit 0 } ; exit 1 } catch { Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 (echo Activate fail. VPS API + firewall 8080 + key check karo. & pause & exit /b 1)
set DEST=%LOCALAPPDATA%\MJ-Client
mkdir "%DEST%" >nul 2>&1
> "%DEST%\config.txt" echo %MJURL%
>> "%DEST%\config.txt" echo %MJKEY%
copy /Y "%~dp0MJ-Chat.ps1" "%DEST%\" >nul
copy /Y "%~dp0Start-MJ.bat" "%DEST%\" >nul
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\MJ.lnk'); $s.TargetPath='%DEST%\Start-MJ.bat'; $s.Save()"
echo Desktop shortcut MJ
pause
start "" "%DEST%\Start-MJ.bat"
