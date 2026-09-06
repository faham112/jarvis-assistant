# Jarvis — Cross-platform AI Assistant

Windows 10 / 11 **aur** Linux ke liye simple Jarvis-style assistant.

Yeh version beginner-friendly hai:

- Voice + text dono
- Time, date, Wikipedia, web search
- Apps / websites kholna
- YouTube search
- Offline TTS (`pyttsx3`)
- Speech-to-text Google recognizer se (internet chahiye)

## Clone

```bash
git clone https://github.com/faham112/jarvis-assistant.git
cd jarvis-assistant
```

## Requirements

- Python 3.10+
- Microphone + speakers
- Internet (voice recognition + search ke liye)

## Windows install

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python jarvis.py
```

Agar `pyaudio` fail ho:

```powershell
pip install pipwin
pipwin install pyaudio
```

## Linux install

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip portaudio19-dev espeak ffmpeg
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python jarvis.py
```

## Commands examples

- `Jarvis, time kya hua hai`
- `date`
- `open youtube`
- `open notepad`  (Windows) / `open firefox` (Linux)
- `who is Elon Musk`
- `search python tutorial`
- `joke`
- `goodbye`

Text mode bhi chalega: seedha type karke Enter dabao.

## Next upgrades

1. Wake word engine: Porcupine / openWakeWord
2. Local LLM: Ollama (`llama3.2` / `qwen2.5`)
3. Better voice: Piper TTS or edge-tts
4. System control: volume, brightness, screenshots
5. Memory: notes + reminders SQLite mein
