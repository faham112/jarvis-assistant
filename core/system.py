import os
import platform
import subprocess
import webbrowser
from datetime import datetime


IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"


def now_text() -> str:
    return datetime.now().strftime("%I:%M %p")


def date_text() -> str:
    return datetime.now().strftime("%A, %d %B %Y")


def open_url(url: str):
    webbrowser.open(url)


def open_app(name: str) -> str:
    name = name.lower().strip()
    mapping_win = {
        "notepad": "notepad",
        "calculator": "calc",
        "cmd": "cmd",
        "explorer": "explorer",
        "chrome": "chrome",
        "edge": "msedge",
        "vscode": "code",
    }
    mapping_linux = {
        "notepad": "gedit",
        "calculator": "gnome-calculator",
        "terminal": "xdg-terminal",
        "files": "xdg-open .",
        "chrome": "google-chrome",
        "firefox": "firefox",
        "vscode": "code",
    }

    try:
        if IS_WINDOWS:
            exe = mapping_win.get(name, name)
            os.startfile(exe) if "." in exe or os.path.exists(exe) else subprocess.Popen(exe, shell=True)
        else:
            cmd = mapping_linux.get(name, name)
            subprocess.Popen(cmd, shell=True)
        return f"Opening {name}."
    except Exception as e:
        return f"I could not open {name}. {e}"


def search_web(query: str):
    open_url(f"https://www.google.com/search?q={query.replace(' ', '+')}")


def youtube(query: str):
    open_url(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
