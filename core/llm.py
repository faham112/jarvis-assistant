import re, requests
from config import OLLAMA_HOST, OLLAMA_MODEL, ASSISTANT_NAME

SYSTEM_PROMPT = f"""Tum {ASSISTANT_NAME} ho.
Roman Urdu, short.
MANA: Sahib, Janab, comet, GitHub lecture, Pandas, NumPy, fake Discord errors,
numbered option menus, "Play mj-reply", project names jo user ne na likhe.
Agar tool result nahi diya gaya to mat bolo ke system toot gaya.
Agar pata nahi: "Ye data mere paas nahi. !mj help"
Max 30 words.
"""

BANNED = re.compile(
    r"\b(sahib|saheb|janab|huzoor|comet|pandas|numpy)\b",
    re.I,
)

def clean_reply(text):
    t = BANNED.sub("", text or "")
    t = re.sub(r"Play mj-reply.*", "", t, flags=re.I)
    return re.sub(r" +", " ", t).strip() or "Theek hai. !mj help"

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
            return "Ollama band hai. !mj help"
        try:
            from core.memory import snapshot
            facts = snapshot()
        except Exception:
            facts = ""
        sys = SYSTEM_PROMPT + ("\n" + facts if facts else "")
        self.history = self.history[-6:]
        self.history.append({"role": "user", "content": user_text})
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
