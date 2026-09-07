import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, ASSISTANT_NAME, OWNER_NAME

SYSTEM_PROMPT = f"""You are {ASSISTANT_NAME}, a short assistant for {OWNER_NAME}.
Reply in the user's language mix (Urdu/Roman Urdu/English).
You do NOT have meetings, teams, WhatsApp inbox, email, or secret files.
NEVER invent names, projects, briefings, or "I already sent you".
If you do not have a tool result, say you don't have that data and suggest a real command: help, time, system health, list folder, weather CITY.
Do not roleplay a movie JARVIS staff meeting.
Max 40 words.
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
        if self.online:
            print(f"[LLM] Ollama ready @ {OLLAMA_HOST} model={OLLAMA_MODEL}")
        else:
            print("[LLM] Ollama nahi milaa.")

    def ask(self, user_text: str) -> str:
        if not self.online:
            return "Ollama band hai. !mj help se real commands chalao."
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
            return "Model ne khali jawab diya. !mj help"
        except Exception as e:
            self.online = False
            return f"Ollama error: {e}"
