import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ASSISTANT_NAME = "Jarvis"
WAKE_WORDS = ("jarvis", "hey jarvis", "ok jarvis")

TTS_RATE = 175
TTS_VOLUME = 1.0

# Prefer a male English voice if available
PREFERRED_VOICE_KEYWORDS = ("david", "mark", "male", "english", "en_")

LISTEN_TIMEOUT = 6
PHRASE_TIME_LIMIT = 10
ENERGY_THRESHOLD = 300
DYNAMIC_ENERGY = True
