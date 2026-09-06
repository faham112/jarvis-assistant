import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "notes.txt"

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "MJ")
OWNER_NAME = os.getenv("OWNER_NAME", "Boss")

WAKE_PHRASES = (
    "hey mj",
    "hey m j",
    "hey emjay",
    "hey em jay",
    "ok mj",
    "okay mj",
    "hi mj",
    "yo mj",
    "hey jarvis",
    "ok jarvis",
    "jarvis",
)
WAKE_ALIASES = {"mj", "emjay", "jarvis"}

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

TTS_RATE = int(os.getenv("TTS_RATE", "175"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))
PREFERRED_VOICE_KEYWORDS = ("david", "mark", "male", "english", "en_")

LISTEN_TIMEOUT = 7
PHRASE_TIME_LIMIT = 12
ENERGY_THRESHOLD = 300
DYNAMIC_ENERGY = True
SESSION_SECONDS = 25

DANGEROUS_KEYWORDS = ("shutdown", "restart", "reboot", "format", "delete all", "rm -rf")
