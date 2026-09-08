@echo off
set SRC=%~dp0
set DEST=%LOCALAPPDATA%\MJ-Client
mkdir "%DEST%" 2>nul
copy /Y "%SRC%config.txt" "%DEST%\" >nul
copy /Y "%SRC%MJ-Chat.ps1" "%DEST%\" >nul
copy /Y "%SRC%Start-MJ.bat" "%DEST%\" >nul
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\MJ.lnk'); $s.TargetPath='%DEST%\Start-MJ.bat'; $s.Save()"
echo Desktop pe MJ shortcut.
pause
start "" "%DEST%\Start-MJ.bat"
