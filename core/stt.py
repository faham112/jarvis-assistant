import speech_recognition as sr
from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT, ENERGY_THRESHOLD, DYNAMIC_ENERGY


class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY
        self.microphone = None
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
        except Exception as e:
            print(f"[STT] Microphone not ready: {e}")

    def listen(self, prompt: str | None = None) -> str:
        if not self.microphone:
            return ""
        if prompt:
            print(prompt)
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )
            text = self.recognizer.recognize_google(audio)
            print(f"You: {text}")
            return text.lower().strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[STT] Recognition service error: {e}")
            return ""
        except Exception as e:
            print(f"[STT] Error: {e}")
            return ""
