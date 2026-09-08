import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, ASSISTANT_NAME, OWNER_NAME

SYSTEM_PROMPT = f"""Tum {ASSISTANT_NAME} ho, {OWNER_NAME} ki female assistant.
Hamesha Roman Urdu mein jawab do (Urdu words English letters: theek, batao, ho gaya).
Mood: narm, seedhi, thori si tameez. Larki wali awaz/andaaz.
Meetings, teams, WhatsApp inbox invent mat karo.
Data na ho to bolo data nahi, command do: help, time, system health.
40 words se kam.
"""

class Brain:
    def __init__(self):
        self.online = False
        self.history = []
        self._check()
    def _check(self):
        try:
            r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
            self.online = r.status_code == 200
        except Exception:
            self.online = False
        print("[LLM]", "ready" if self.online else "off", OLLAMA_MODEL)
    def ask(self, user_text):
        if not self.online:
            return "Ollama band hai. !mj help likho."
        self.history.append({"role": "user", "content": user_text})
        self.history = self.history[-8:]
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
        try:
            r = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
                timeout=120,
            )
            r.raise_for_status()
            content = (r.json().get("message") or {}).get("content", "").strip()
            if content:
                self.history.append({"role": "assistant", "content": content})
                return content
            return "Khali jawab. !mj help"
        except Exception as e:
            self.online = False
            return "Ollama error: %s" % e
