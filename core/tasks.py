import os, platform, socket, urllib.parse, urllib.request

HELP = """MJ tasks (usi machine pe jahan bot chal raha ho):

Time/date: time | date
System: system health | organize downloads | folder banao NAME
Files: list folder [Downloads] | file padho NAME | update NAME pe TEXT
Notes: note TEXT | read notes
Web: search QUERY | youtube QUERY | weather CITY
WhatsApp: whatsapp summary (export txt)
Discord: !join !leave !mj COMMAND
Danger: shutdown | restart (confirm)
"""

def weather(city=""):
    city = (city or "").strip() or "Karachi"
    url = "https://wttr.in/%s?format=3" % urllib.parse.quote(city)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mj"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.read().decode("utf-8", "replace").strip()
    except Exception as e:
        return "Weather nahi mili: " + str(e)

def host_info():
    return "Host %s | %s | user %s" % (
        socket.gethostname(), platform.system(),
        os.getenv("USER") or os.getenv("USERNAME") or "?",
    )
