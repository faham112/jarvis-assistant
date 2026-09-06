from config import WAKE_PHRASES, WAKE_ALIASES


def _normalize(text):
    t = (text or "").lower()
    for ch in ",.!?:":
        t = t.replace(ch, " ")
    return " ".join(t.split())


def contains_wake(text):
    t = _normalize(text)
    if not t:
        return False
    if t in WAKE_ALIASES:
        return True
    if any(phrase in t for phrase in WAKE_PHRASES):
        return True
    words = t.split()
    return "mj" in words or "jarvis" in words


def strip_wake(text):
    t = _normalize(text)
    for phrase in sorted(WAKE_PHRASES, key=len, reverse=True):
        if t.startswith(phrase):
            return t[len(phrase):].strip()
    parts = t.split()
    if parts and parts[0] in WAKE_ALIASES:
        return " ".join(parts[1:]).strip()
    return t
