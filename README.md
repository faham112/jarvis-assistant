# MJ — Hey MJ Voice Assistant

Windows 10/11 aur Linux. Wake phrase: **Hey MJ**.

Brain: **Ollama** (local LLM). Voice: Google STT + pyttsx3 TTS.
Agar Ollama band ho, built-in commands phir bhi chalte hain.

Repo: https://github.com/faham112/jarvis-assistant

---

## A to Z setup

### 0) Jo chahiye

- Python 3.10+
- Mic + speaker
- Internet (pehli dafa packages + Google voice ke liye)
- RAM: 8GB better. Ollama model ~2GB disk

### 1) Code lao

```bash
git clone https://github.com/faham112/jarvis-assistant.git
cd jarvis-assistant
```

Agar pehle clone ho chuka hai:

```bash
git pull
```

### 2) Ollama install (brain)

**Windows:** https://ollama.com/download se installer, phir PowerShell:

```powershell
ollama --version
ollama pull llama3.2
ollama serve
```

Kam RAM ho to:

```powershell
ollama pull llama3.2:1b
```

Us ke baad `.env` mein `OLLAMA_MODEL=llama3.2:1b`

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

Check:

```bash
curl http://127.0.0.1:11434/api/tags
```

### 3) Python env

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`pyaudio` error:

```powershell
pip install pipwin
pipwin install pyaudio
```

**Linux**

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip portaudio19-dev espeak ffmpeg
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Config

```bash
copy .env.example .env     # Windows
cp .env.example .env       # Linux
```

`.env` edit:

```
ASSISTANT_NAME=MJ
OWNER_NAME=Faheem
OLLAMA_MODEL=llama3.2
```

### 5) Run

Ollama chal raha ho, phir:

```bash
python jarvis.py
```

Bolo: **Hey MJ**
MJ: **Yes?**
Phir command.

Text mode: seedha type + Enter. Voice: khali Enter.

---

## Voice wake

Google STT jo sunta hai usme ye phrases match hote hain:

- hey mj
- hey m j
- hey emjay
- ok mj
- hey jarvis
- mj

STT kabhi `hey emjay` likh deta hai — wo bhi accept hai.

**Sach baat:** yeh speaker ID nahi hai (sirf tumhari awaz unlock).
Yeh wake phrase hai. Jo bhi mic ke paas Hey MJ bole, activate ho sakta hai.
True voice-lock alag biometric model maangta hai.

Session ~25 seconds khula rehta hai, us dauran dobara hey MJ zaroori nahi.

---

## Commands

- time / kitna baja
- date / tareekh
- open notepad / chrome / vscode
- kholo firefox
- open youtube
- search python
- who is / wikipedia / kaun hai
- volume up / down / mute
- screenshot
- lock screen
- note buy milk / yaad rakh
- read notes
- shutdown / restart (confirm: yes)
- koi bhi sawal -> Ollama
- goodbye / sleep

Dangerous actions confirm ke baghair nahi chalte.

---

## Troubleshooting

Mic: Windows Privacy -> Microphone on. Linux: arecord -l

Hey MJ nahi sunta: saaf bolo, internet on, text se `hey mj time` try karo.

Ollama: alag terminal mein `ollama serve`. `ollama list` mein model dikhna chahiye.

Linux silent TTS: `sudo apt install espeak`
