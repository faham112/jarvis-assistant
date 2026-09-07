from collections import Counter
from pathlib import Path
import re
from core.workspace import ROOTS, ensure_workspace

LINE = re.compile(
    r"^\[?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APMapm]{2})?\]?\s*-?\s*([^:]+):\s*(.*)$"
)

def find_export():
    search = [ensure_workspace(), Path.home() / "Downloads", Path.home() / "storage" / "downloads"]
    search.extend(ROOTS)
    for folder in search:
        if not folder.exists():
            continue
        for p in folder.rglob("*"):
            if not p.is_file():
                continue
            n = p.name.lower()
            if n.endswith(".txt") and ("whatsapp" in n or "chat" in n):
                return p
    return None

def summarize(path=None):
    p = path or find_export()
    if not p:
        return (
            "Live WhatsApp inbox MJ nahi padh sakti. "
            "Chat -> menu -> Export chat (without media). "
            "File MJ-Workspace ya Downloads mein rakho. Phir: whatsapp summary"
        )
    who = Counter()
    texts = []
    raw = p.read_text(encoding="utf-8", errors="replace")
    for line in raw.splitlines():
        m = LINE.match(line.strip())
        if not m:
            continue
        sender, body = m.group(2).strip(), m.group(3).strip()
        if "omitted" in body.lower() or body.startswith("<Media"):
            continue
        who[sender] += 1
        texts.append("%s: %s" % (sender, body[:120]))
    if not who:
        return "Export mili (%s) lekin parse nahi hui." % p
    lines = ["File: " + str(p), "Kis kis ne msg kiya:"]
    for name, n in who.most_common(20):
        lines.append("  %s — %s msgs" % (name, n))
    lines.append("Last 8:")
    lines.extend("  " + t for t in texts[-8:])
    return "\n".join(lines)
