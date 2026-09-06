import pyttsx3
from config import TTS_RATE, TTS_VOLUME, PREFERRED_VOICE_KEYWORDS


class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", TTS_RATE)
        self.engine.setProperty("volume", TTS_VOLUME)
        self._pick_voice()

    def _pick_voice(self):
        voices = self.engine.getProperty("voices") or []
        chosen = None
        for voice in voices:
            name = (voice.name or "").lower()
            vid = (voice.id or "").lower()
            if any(k in name or k in vid for k in PREFERRED_VOICE_KEYWORDS):
                chosen = voice.id
                break
        if chosen:
            self.engine.setProperty("voice", chosen)

    def say(self, text: str):
        if not text:
            return
        print(f"Jarvis: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
