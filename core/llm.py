import re, requests
from config import OLLAMA_HOST, OLLAMA_MODEL, ASSISTANT_NAME

SYSTEM_PROMPT = f"""Tum {ASSISTANT_NAME} ho, female assistant.
Roman Urdu. Sahib mat bolo.
Facts sirf Known facts se. Invent mat karo. 40 words.
"""
BANNED = re.compile(r"\\b(sahib|saheb|janab|huzoor)\\b", re.I)

def clean_reply(text):
    t = BANNED.sub("", text or "")
    return re.sub(r" +", " ", t).strip() or "Theek hai."

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
            return "Ollama band hai."
        try:
            from core.memory import snapshot
            facts = snapshot()
        except Exception:
            facts = ""
        sys = SYSTEM_PROMPT + ("\n" + facts if facts else "")
        self.history.append({"role": "user", "content": user_text})
        self.history = self.history[-8:]
        try:
            r = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": [{"role": "system", "content": sys}] + self.history, "stream": False},
                timeout=120,
            )
            r.raise_for_status()
            content = clean_reply((r.json().get("message") or {}).get("content", ""))
            self.history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            self.online = False
            return "Ollama error: %s" % e
