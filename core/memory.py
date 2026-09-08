import json
from datetime import datetime
from pathlib import Path
from config import DATA_DIR

MEM_FILE = DATA_DIR / "memory.json"

def _load():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MEM_FILE.exists():
        return {"facts": {}}
    try:
        return json.loads(MEM_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"facts": {}}

def _save(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEM_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def set_fact(key, value):
    key = (key or "").strip().lower()[:80]
    value = (value or "").strip()[:400]
    if not key or not value:
        return "Example: yaad rakh city Karachi"
    data = _load()
    data.setdefault("facts", {})[key] = {"value": value, "when": datetime.now().isoformat(timespec="seconds")}
    _save(data)
    return "Yaad rakh li: %s = %s" % (key, value)

def get_fact(key):
    key = (key or "").strip().lower()
    fact = _load().get("facts", {}).get(key)
    if not fact:
        return "Memory nahi: " + key
    return "%s = %s" % (key, fact["value"])

def forget(key):
    key = (key or "").strip().lower()
    data = _load()
    if key not in data.get("facts", {}):
        return "Woh fact nahi."
    del data["facts"][key]
    _save(data)
    return "Bhool gayi: " + key

def list_facts():
    facts = _load().get("facts", {})
    if not facts:
        return "Memory khali. Bolo: yaad rakh naam Faham"
    lines = ["Memory:"]
    for k, v in list(facts.items())[:40]:
        lines.append("  %s = %s" % (k, v.get("value", "")))
    return "\n".join(lines)

def snapshot():
    facts = _load().get("facts", {})
    if not facts:
        return ""
    parts = ["%s=%s" % (k, v.get("value", "")) for k, v in list(facts.items())[:25]]
    return "Known facts: " + "; ".join(parts)
