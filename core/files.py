import shutil
from pathlib import Path

from core import logger

GROUPS = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a", ".aac"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Installers": {".exe", ".msi", ".dmg", ".apk"},
}


def downloads_dir():
    return Path.home() / "Downloads"


def desktop_dir():
    return Path.home() / "Desktop"


def organize_downloads():
    root = downloads_dir()
    if not root.exists():
        return "Downloads folder nahi mili."
    moved = 0
    skipped = 0
    for item in root.iterdir():
        if not item.is_file() or item.name.startswith("."):
            continue
        group = "Other"
        ext = item.suffix.lower()
        for name, exts in GROUPS.items():
            if ext in exts:
                group = name
                break
        dest_dir = root / group
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / item.name
        if dest.exists():
            skipped += 1
            continue
        shutil.move(str(item), str(dest))
        moved += 1
    msg = "Downloads organize ho gaye. Moved %s files. Skipped %s (already there)." % (moved, skipped)
    logger.log("organize_downloads", msg)
    return msg


def make_folder(place, name):
    name = (name or "New Folder").strip().replace("..", "")
    for bad in ("/", "\\"):
        name = name.replace(bad, "-")
    base = desktop_dir() if place == "desktop" else downloads_dir()
    path = base / name
    path.mkdir(parents=True, exist_ok=True)
    logger.log("make_folder", str(path))
    return "Folder ban gaya: " + str(path)
