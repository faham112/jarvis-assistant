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

Teams & Task Management (multi-user, persisted in data/tasks.json + data/teams.json):
  create team NAME
  add MEMBER to team NAME [as ROLE]
  remove MEMBER from team NAME
  list teams
  team NAME workload | workload

  add task TITLE [for ASSIGNEE] [priority low|medium|high|urgent] [due YYYY-MM-DD] [project NAME] [team NAME]
  my tasks | all tasks | tasks for ASSIGNEE | team NAME tasks
  overdue tasks | urgent tasks
  start task TITLE | complete task TITLE | block task TITLE | delete task TITLE
  reassign task TITLE to ASSIGNEE

REST API (see api_server.py): /teams, /teams/{name}/members, /teams/{name}/workload,
  /tasks (GET/POST), /tasks/{id} (GET/PATCH/DELETE), /tasks/overdue, /tasks/{id}/subtasks, /workload
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
