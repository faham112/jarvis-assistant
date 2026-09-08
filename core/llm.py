import re
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, ASSISTANT_NAME, OWNER_NAME

SYSTEM_PROMPT = f"""Tum {ASSISTANT_NAME} ho, female assistant.
Roman Urdu mein baat karo jaise normal log: theek, ho gaya, batao.
Kabhi NA bolo: Sahib, Saheb, Janab, Sir, Madam, Team briefing, Project names ghad ke.
Na film JARVIS, na naukar. Seedhi dost-assistant.
Jhoot meetings/log invent mat karo.
40 words se kam.
"""

BANNED = re.compile(
    r"\b(sahib|saheb|saahib|janab|janaab|huzoor|madam)\b",
    re.I,
)

def clean_reply(text):
    t = text or ""
    t = BANNED.sub("", t)
    t = t.replace("صاحب", "").replace("جناب", "")
    t = re.sub(r"\s+,", ",", t)
    t = re.sub(r" +", " ", t).strip(" ,.")
    return t or "Theek hai."

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
                content = clean_reply(content)
                self.history.append({"role": "assistant", "content": content})
                return content
            return "Theek hai. !mj help"
        except Exception as e:
            self.online = False
            return "Ollama error: %s" % e
