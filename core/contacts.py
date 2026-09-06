import os
import re
import urllib.parse


def _load_book():
    book = {}
    raw = os.getenv("WA_CONTACTS", "")
    for part in raw.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        name, num = part.split("=", 1)
        digits = re.sub(r"\D", "", num)
        if digits.startswith("0") and len(digits) == 11:
            digits = "92" + digits[1:]
        if digits:
            book[name.strip().lower()] = digits
    extras = {
        "faham": os.getenv("CONTACT_FAHAM", ""),
        "faheem": os.getenv("CONTACT_FAHEEM", ""),
        "abdul faheem": os.getenv("CONTACT_FAHEEM", ""),
        "abdul faham": os.getenv("CONTACT_FAHAM", ""),
    }
    for k, v in extras.items():
        digits = re.sub(r"\D", "", v)
        if digits.startswith("0") and len(digits) == 11:
            digits = "92" + digits[1:]
        if digits:
            book[k] = digits
    return book


def lookup(name):
    book = _load_book()
    key = (name or "").lower().strip()
    if key in book:
        return book[key]
    for n, num in book.items():
        if n in key or key in n:
            return num
    return ""


def parse_whatsapp_command(q):
    q = (q or "").lower()
    msg = "hi"
    m = re.search(r"(?:bolo|kaho|kehdo|keho|message|msg)\s+(.+)$", q)
    if m:
        msg = m.group(1).strip() or "hi"
    name = ""
    for token in ("abdul faheem", "abdul faham", "abdul fsheem", "faheem", "faham"):
        if token in q:
            name = token
            break
    return name, msg


def wa_link(number, text):
    return "https://wa.me/%s?text=%s" % (number, urllib.parse.quote(text))
