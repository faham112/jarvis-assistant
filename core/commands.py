import re
import wikipedia

from core import system
from core import files
from core import health
from core import logger
from core.llm import Brain


class Router:
    def __init__(self, brain):
        self.brain = brain
        self.pending_danger = None

    def handle(self, command):
        q = (command or "").lower().strip()
        if not q:
            return "I did not catch that."

        if self.pending_danger:
            if q in ("yes", "haan", "han", "confirm", "do it", "ok"):
                action = self.pending_danger
                self.pending_danger = None
                return system.power_action(action)
            self.pending_danger = None
            return "Cancelled."

        if q in ("exit", "quit", "goodbye", "sleep", "band karo", "go offline", "goodbye mj"):
            return "__EXIT__"

        if "your name" in q or "tumhara naam" in q:
            return "MJ. Just a rather useful machine."

        if "time" in q or "kitna baja" in q or "what time" in q:
            return "The time is " + system.now_text() + "."

        if "date" in q or "tareekh" in q or "aaj ka din" in q:
            return "Today is " + system.date_text() + "."

        if "volume up" in q or "awaz barhao" in q or "sound up" in q:
            return system.volume("up")
        if "volume down" in q or "awaz kam" in q or "sound down" in q:
            return system.volume("down")
        if "mute" in q or "unmute" in q:
            return system.volume("mute")

        if any(k in q for k in (
            "organize downloads",
            "downloads folder saaf",
            "downloads organize",
            "saaf karo downloads",
            "organize my downloads",
        )):
            return files.organize_downloads()

        if any(k in q for k in ("system health", "pc slow", "system check", "mera pc slow")):
            return health.system_health()

        if "folder banao" in q or "create folder" in q or "folder bana" in q:
            name = q
            for cut in ("desktop pe", "desktop par", "on desktop", "create folder", "folder banao", "folder bana", "naam ka", "named"):
                name = name.replace(cut, " ")
            name = " ".join(name.split()) or "Projects"
            place = "desktop" if "desktop" in q else "downloads"
            return files.make_folder(place, name)

        if q.startswith("close ") or q.startswith("band karo "):
            app = q.split(" ", 1)[1].replace("karo", "").strip()
            return system.close_app(app)

        if "whatsapp" in q:
            system.open_url("https://web.whatsapp.com")
            logger.log("whatsapp", q)
            return "WhatsApp Web khol diya. Contact khud select karo."

        m = re.search(r"(?:open|kholo)\s+(chrome|google)\s+(?:and\s+)?(?:search(?:\s+for)?|pe search)\s+(.+)", q)
        if m:
            query = m.group(2).strip()
            system.search_web(query)
            return "Chrome/search: " + query

        if "screenshot" in q or "screen shot" in q or "what's on my screen" in q or "kya screen" in q:
            return system.screenshot()

        if ("lock" in q and "screen" in q) or q in ("lock", "lock pc"):
            return system.lock_screen()

        if q.startswith("note ") or q.startswith("yaad rakh ") or q.startswith("remember "):
            text = q.split(" ", 1)[1]
            return system.save_note(text)

        if "read notes" in q or "notes padho" in q or "my notes" in q:
            return system.read_notes()

        if q.startswith("open ") or q.startswith("kholo "):
            target = q.split(" ", 1)[1]
            if target.startswith("http") or ("." in target and " " not in target):
                url = target if target.startswith("http") else "https://" + target
                system.open_url(url)
                return "Opening " + target + "."
            return system.open_app(target)

        if "youtube" in q:
            query = q.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
            system.youtube(query or "music")
            return "Opening YouTube."

        if q.startswith("search ") or q.startswith("google ") or "search karo" in q:
            query = q.replace("search karo", "").replace("search", "").replace("google", "").strip()
            system.search_web(query)
            return "Searching for " + query + "."

        if "wikipedia" in q or q.startswith("who is") or q.startswith("what is") or "kaun hai" in q:
            topic = q.replace("wikipedia", "").replace("who is", "").replace("what is", "").replace("kaun hai", "").strip()
            try:
                wikipedia.set_lang("en")
                return wikipedia.summary(topic or q, sentences=2)
            except Exception:
                system.search_web(topic or q)
                return "Wikipedia short answer nahi mila, search khol diya."

        if "shutdown" in q or "band kar do computer" in q:
            self.pending_danger = "shutdown"
            return "Confirm shutdown? Say yes."
        if "restart" in q or "reboot" in q:
            self.pending_danger = "restart"
            return "Confirm restart? Say yes."

        if "joke" in q:
            return "I would tell a UDP joke, but I am not sure you would get it."

        if any(w in q for w in ("hello", "salam", "assalam", "hi mj")):
            return "Online. What do you need?"

        return self.brain.ask(command)
