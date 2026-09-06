import requests

from config import OLLAMA_HOST, OLLAMA_MODEL, ASSISTANT_NAME, OWNER_NAME

SYSTEM_PROMPT = (
    f"You are {ASSISTANT_NAME}, a sharp personal desktop assistant for {OWNER_NAME}. "
    "Speak briefly, like JARVIS: useful, calm, a little dry humor. "
    "User may speak Urdu/Roman Urdu mixed with English. Reply in the same mix if they do. "
    "If they ask you to do a computer action, say what you would do in one short sentence. "
    "Do not invent that you already clicked buttons unless a tool result is given. "
    "Keep answers under 60 words unless they ask for detail."
)


class Brain:
    def __init__(self):
        self.online = False
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self._check()

    def _check(self):
        try:
            r = requests.get(OLLAMA_HOST + "/api/tags", timeout=2)
            self.online = r.status_code == 200
        except Exception:
            self.online = False
        if self.online:
            print("[LLM] Ollama ready @", OLLAMA_HOST, "model=", OLLAMA_MODEL)
        else:
            print("[LLM] Ollama nahi milaa. Commands still work.")

    def ask(self, user_text):
        if not self.online:
            return (
                "Ollama band hai. Pehle Ollama start karo aur model pull karo. "
                "Us ke baghair main sirf built-in commands chala sakta hoon."
            )
        self.history.append({"role": "user", "content": user_text})
        try:
            r = requests.post(
                OLLAMA_HOST + "/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": self.history[-12:],
                    "stream": False,
                },
                timeout=120,
            )
            r.raise_for_status()
            content = r.json().get("message", {}).get("content", "").strip()
            if content:
                self.history.append({"role": "assistant", "content": content})
                return content
            return "Model ne khali jawab diya."
        except Exception as e:
            self.online = False
            return "Ollama error: " + str(e)
