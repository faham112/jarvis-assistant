import pyttsx3

from config import TTS_RATE, TTS_VOLUME, PREFERRED_VOICE_KEYWORDS


class Speaker:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
        except Exception as exc:
            self.engine = None
            print(f"TTS unavailable; continuing in text mode: {exc}")
            return
        self.engine.setProperty("rate", TTS_RATE)
        self.engine.setProperty("volume", TTS_VOLUME)
        self._pick_voice()

    def _pick_voice(self):
        voices = self.engine.getProperty("voices") or []
        for voice in voices:
            name = (getattr(voice, "name", "") or "").lower()
            vid = (getattr(voice, "id", "") or "").lower()
            if any(k in name or k in vid for k in PREFERRED_VOICE_KEYWORDS):
                self.engine.setProperty("voice", voice.id)
                break

    def say(self, text):
        if not text:
            return
        print("MJ:", text)
        if self.engine is None:
            return
        self.engine.say(text)
        self.engine.runAndWait()
