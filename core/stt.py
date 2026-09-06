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
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[STT] Microphone ready.")
        except Exception as e:
            print("[STT] Microphone not ready:", e)
            print("[STT] Voice nahi chalega. Text mode use karo.")

    def listen(self, prompt=None, timeout=None):
        if not self.microphone:
            return ""
        if prompt:
            print(prompt)
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout if timeout is not None else LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )
            text = self.recognizer.recognize_google(audio)
            print("You:", text)
            return text.lower().strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print("[STT] Google speech error (internet check karo):", e)
            return ""
        except Exception as e:
            print("[STT] Error:", e)
            return ""
