@echo off
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  python -m venv .venv
  .venv\Scripts\python.exe -m pip install -U pip
  .venv\Scripts\pip.exe install -r requirements.txt
  .venv\Scripts\pip.exe install edge-tts
)
.venv\Scripts\python.exe discord_bot.py
pause
