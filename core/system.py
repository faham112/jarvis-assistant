import platform
import subprocess
from datetime import datetime
import webbrowser

from config import NOTES_FILE, DATA_DIR

IS_WINDOWS = platform.system() == "Windows"


def now_text():
    return datetime.now().strftime("%I:%M %p")


def date_text():
    return datetime.now().strftime("%A, %d %B %Y")


def open_url(url):
    webbrowser.open(url)


def search_web(query):
    open_url("https://www.google.com/search?q=" + query.replace(" ", "+"))


def youtube(query):
    open_url("https://www.youtube.com/results?search_query=" + query.replace(" ", "+"))


def _run(cmd, shell=False):
    subprocess.Popen(cmd, shell=shell)


def open_app(name):
    name = name.lower().strip()
    win_map = {
        "notepad": "notepad",
        "calculator": "calc",
        "cmd": "cmd",
        "powershell": "powershell",
        "explorer": "explorer",
        "chrome": "chrome",
        "edge": "msedge",
        "vscode": "code",
        "spotify": "spotify",
    }
    linux_map = {
        "notepad": "gedit",
        "calculator": "gnome-calculator",
        "terminal": "x-terminal-emulator",
        "files": "xdg-open .",
        "chrome": "google-chrome",
        "firefox": "firefox",
        "vscode": "code",
        "spotify": "spotify",
    }
    try:
        if IS_WINDOWS:
            _run(win_map.get(name, name), shell=True)
        else:
            _run(linux_map.get(name, name), shell=True)
        return "Opening " + name + "."
    except Exception as e:
        return "Open nahi ho saka: " + name + ". " + str(e)


def volume(action):
    action = action.lower()
    try:
        if IS_WINDOWS:
            keys = {"up": "175", "down": "174", "mute": "173"}
            code = keys.get(action, "175")
            _run(
                'powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]' + code + ')"',
                shell=True,
            )
        else:
            if action == "up":
                _run("pactl set-sink-volume @DEFAULT_SINK@ +10%", shell=True)
            elif action == "down":
                _run("pactl set-sink-volume @DEFAULT_SINK@ -10%", shell=True)
            else:
                _run("pactl set-sink-mute @DEFAULT_SINK@ toggle", shell=True)
        return "Volume " + action + "."
    except Exception as e:
        return "Volume change fail: " + str(e)


def screenshot():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / ("shot_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png")
    try:
        if IS_WINDOWS:
            script = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "Add-Type -AssemblyName System.Drawing; "
                "$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
                "$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height; "
                "$g = [System.Drawing.Graphics]::FromImage($bmp); "
                "$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size); "
                "$bmp.Save('" + str(path).replace("\\", "\\\\") + "');"
            )
            subprocess.run(["powershell", "-c", script], check=False)
        else:
            subprocess.run(["gnome-screenshot", "-f", str(path)], check=False)
        return "Screenshot saved: " + str(path)
    except Exception as e:
        return "Screenshot fail: " + str(e)


def lock_screen():
    try:
        if IS_WINDOWS:
            _run(["rundll32.exe", "user32.dll,LockWorkStation"])
        else:
            _run("loginctl lock-session", shell=True)
        return "Locking the screen."
    except Exception as e:
        return "Lock fail: " + str(e)


def save_note(text):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(datetime.now().isoformat() + "  " + text + "\n")
    return "Note saved."


def read_notes():
    if not NOTES_FILE.exists():
        return "No notes yet."
    lines = NOTES_FILE.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return "No notes yet."
    return "Latest notes: " + " | ".join(lines[-5:])


def power_action(kind):
    kind = kind.lower()
    if IS_WINDOWS:
        if kind == "shutdown":
            _run("shutdown /s /t 30", shell=True)
            return "Windows 30 seconds mein shutdown. Cancel: shutdown /a"
        if kind == "restart":
            _run("shutdown /r /t 30", shell=True)
            return "Windows 30 seconds mein restart. Cancel: shutdown /a"
    else:
        if kind == "shutdown":
            _run("shutdown -h +1", shell=True)
            return "Linux 1 minute mein shutdown. Cancel: shutdown -c"
        if kind == "restart":
            _run("shutdown -r +1", shell=True)
            return "Linux 1 minute mein restart. Cancel: shutdown -c"
    return "Unknown power action."
