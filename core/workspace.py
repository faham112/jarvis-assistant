from pathlib import Path
from core import logger

ROOTS = [
    Path.home() / "MJ-Workspace",
    Path.home() / "Downloads",
    Path.home() / "Documents",
    Path.home() / "Desktop",
    Path.home() / "storage" / "downloads",
    Path.home() / "storage" / "shared" / "Download",
]

def ensure_workspace():
    ws = Path.home() / "MJ-Workspace"
    ws.mkdir(parents=True, exist_ok=True)
    return ws

def _safe(path):
    path = path.expanduser().resolve()
    home = Path.home().resolve()
    if home not in path.parents and path != home:
        raise ValueError("Sirf home folder ke andar.")
    s = str(path)
    if "/etc" in s or "/sys" in s or "/proc" in s:
        raise ValueError("Blocked path")
    return path

def resolve(name):
    name = (name or "").strip().strip("\"'")
    name = name.replace("\\", "/")
    if not name or name in (".", "workspace", "mj workspace"):
        return ensure_workspace()
    p = Path(name)
    if p.is_absolute():
        return _safe(p)
    for root in ROOTS:
        cand = root / name
        if cand.exists():
            return _safe(cand)
    return _safe(ensure_workspace() / name)

def list_dir(name=""):
    p = resolve(name)
    if not p.exists():
        return "Folder nahi: " + str(p)
    if p.is_file():
        return "Yeh file hai: " + str(p)
    items = sorted(p.iterdir(), key=lambda x: x.name.lower())[:80]
    if not items:
        return str(p) + " khali hai."
    lines = [str(p) + ":"]
    for i in items:
        lines.append("  " + i.name + ("/" if i.is_dir() else ""))
    logger.log("ls", str(p))
    return "\n".join(lines)

def read_file(name):
    p = resolve(name)
    if not p.is_file():
        return "File nahi mili: " + str(p)
    data = p.read_text(encoding="utf-8", errors="replace")[:4000]
    logger.log("read", str(p))
    return str(p) + "\n\n" + data

def write_file(name, content, append=False):
    p = resolve(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with p.open(mode, encoding="utf-8") as f:
        f.write(content if content.endswith("\n") else content + "\n")
    logger.log("write", str(p))
    return "Update ho gaya: " + str(p)
