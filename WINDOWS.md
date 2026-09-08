# MJ on Windows 10 / 11

1. Python 3.11+ from python.org — tick Add to PATH
2. `winget install Gyan.FFmpeg` then open a new terminal
3. Ollama from ollama.com then `ollama pull llama3.2`

```powershell
cd $env:USERPROFILE
git clone https://github.com/faham112/jarvis-assistant.git
cd jarvis-assistant
python -m venv .venv
.\ .venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
pip install edge-tts
```

If script blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Local mic:
```powershell
python jarvis.py
```

Discord:
```powershell
python discord_bot.py
```

Or double-click `scripts\start-mj-windows.bat`

Bot jis PC pe chale, folders usi PC ke control hote hain.
