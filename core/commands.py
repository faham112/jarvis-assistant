import re
import wikipedia
from core import system, files, health, logger
from core.llm import Brain

class Router:
    def __init__(self, brain: Brain):
        self.brain = brain
        self.pending_danger = None

    def handle(self, command: str) -> str:
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
        task_reply = self._handle_tasks(q, command)
        if task_reply is not None:
            return task_reply
        if "time" in q or "kitna baja" in q or "what time" in q:
            return "The time is " + system.now_text() + "."
        if re.search(r"\bdate\b", q) or "tareekh" in q or "aaj ka din" in q:
            return "Today is " + system.date_text() + "."
        if "volume up" in q or "awaz barhao" in q or "sound up" in q:
            return system.volume("up")
        if "volume down" in q or "awaz kam" in q or "sound down" in q:
            return system.volume("down")
        if "mute" in q or "unmute" in q:
            return system.volume("mute")
        if any(k in q for k in ("organize downloads", "downloads folder saaf", "downloads organize", "saaf karo downloads", "organize my downloads")):
            return files.organize_downloads()
        if any(k in q for k in ("system health", "pc slow", "system check", "ram", "mera pc slow")):
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
        if any(k in q for k in ("list folder", "folder dikhao", "ls ", "kya files", "directory dikhao")):
            name = q
            for cut in ("list folder", "folder dikhao", "directory dikhao", "kya files hain", "kya files", "ls"):
                name = name.replace(cut, " ")
            from core import workspace
            return workspace.list_dir(name.strip())
        m = re.search(r"(?:read|padho|kholo file|file padho)\s+(.+)", q)
        if m:
            from core import workspace
            return workspace.read_file(m.group(1).strip())
        m = re.search(r"(?:update|likho|write|file update|edit file)\s+(\S+)\s+(?:pe|par|with|ko|:)?\s*(.+)", q)
        if m:
            from core import workspace
            return workspace.write_file(m.group(1).strip(), m.group(2).strip())
        if any(k in q for k in ("whatsapp summary", "wa summary", "kitne msg", "kis kis ne msg", "a to z msg")):
            from core import wa_summary
            return wa_summary.summarize()
        if "whatsapp" in q or "wa pe" in q or "msg karo" in q or ("message" in q and "faham" in q):
            from core import contacts
            name, msg = contacts.parse_whatsapp_command(q)
            number = contacts.lookup(name or q)
            if not number:
                logger.log("whatsapp", "no contact")
                return "Number set nahi. WhatsApp live inbox bhi nahi. Summary ke liye export chat + whatsapp summary."
            url = contacts.wa_link(number, msg)
            system.open_url(url)
            return "WhatsApp chat link khol di. Send khud dabao."
        m = re.search(r"(?:open|kholo)\s+(chrome|google)\s+(?:and\s+)?(?:search(?:\s+for)?|pe search)\s+(.+)", q)
        if m:
            system.search_web(m.group(2).strip())
            return "Chrome/search: " + m.group(2).strip()
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
                system.open_url(target if target.startswith("http") else "https://" + target)
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

    # -----------------------------------------------------------------
    # Team & task management commands
    # -----------------------------------------------------------------
    def _handle_tasks(self, q, original):
        from core import task_manager as tm

        # --- Teams ---
        m = re.search(r"(?:create|banao|naya)\s+team\s+(.+)", q)
        if m:
            team = tm.create_team(m.group(1).strip())
            return "Team '%s' ban gayi." % team["name"]

        m = re.search(r"add\s+(.+?)\s+to\s+team\s+(.+?)(?:\s+as\s+(.+))?$", q)
        if m:
            member, team_name, role = m.group(1).strip(), m.group(2).strip(), (m.group(3) or "member").strip()
            team = tm.add_member(team_name, member, role)
            return "%s ko team '%s' mein add kar diya (%s)." % (member, team["name"], role)

        m = re.search(r"remove\s+(.+?)\s+from\s+team\s+(.+)", q)
        if m:
            team = tm.remove_member(m.group(2).strip(), m.group(1).strip())
            if team:
                return "%s ko team '%s' se remove kar diya." % (m.group(1).strip(), team["name"])
            return "Team nahi mili."

        if q in ("list teams", "teams dikhao", "show teams"):
            teams = tm.list_teams()
            if not teams:
                return "Koi team nahi banayi abhi."
            lines = ["Teams (%d):" % len(teams)]
            for t in teams:
                names = ", ".join(m["name"] for m in t["members"]) or "no members"
                lines.append("- %s: %s" % (t["name"], names))
            return "\n".join(lines)

        m = re.search(r"team\s+(.+?)\s+workload", q) or re.search(r"workload\s+(?:for\s+)?(?:team\s+)?(.+)", q)
        if m and "team" in q:
            summary = tm.workload_summary(team=m.group(1).strip())
            return tm.format_workload(summary)
        if q in ("workload", "team workload"):
            return tm.format_workload(tm.workload_summary())

        # --- Task creation ---
        # e.g. "add task fix login bug for ali priority high due 2026-09-20 project app team backend"
        m = re.search(r"(?:add|create|naya)\s+task\s+(.+)", q)
        if m:
            rest = m.group(1).strip()
            assignee = team = project = due = None
            priority = "medium"

            mm = re.search(r"\bfor\s+([a-z0-9_\- ]+?)(?=\s+priority\b|\s+due\b|\s+project\b|\s+team\b|$)", rest)
            if mm:
                assignee = mm.group(1).strip()
            mm = re.search(r"\bpriority\s+(low|medium|high|urgent)\b", rest)
            if mm:
                priority = mm.group(1)
            mm = re.search(r"\bdue\s+(\d{4}-\d{2}-\d{2})\b", rest)
            if mm:
                due = mm.group(1)
            mm = re.search(r"\bproject\s+([a-z0-9_\- ]+?)(?=\s+priority\b|\s+due\b|\s+team\b|\s+for\b|$)", rest)
            if mm:
                project = mm.group(1).strip()
            mm = re.search(r"\bteam\s+([a-z0-9_\- ]+?)(?=\s+priority\b|\s+due\b|\s+project\b|\s+for\b|$)", rest)
            if mm:
                team = mm.group(1).strip()

            title = rest
            for cut_pattern in (r"\bfor\s+.+", r"\bpriority\s+\w+", r"\bdue\s+\S+", r"\bproject\s+.+?(?=\s+(?:priority|due|team|for)\b|$)", r"\bteam\s+.+?(?=\s+(?:priority|due|project|for)\b|$)"):
                title = re.sub(cut_pattern, "", title).strip()
            title = title or rest

            task = tm.create_task(title=title, assignee=assignee, priority=priority,
                                   due_date=due, project=project, team=team)
            return "Task banaya: " + tm.format_task_line(task)

        # --- Task listing ---
        if q in ("my tasks", "mere task", "meri tasks"):
            return tm.format_task_list(tm.list_tasks(assignee=None, status=None), header="All open tasks")
        m = re.search(r"tasks\s+for\s+(.+)", q)
        if m:
            return tm.format_task_list(tm.list_tasks(assignee=m.group(1).strip()), header="Tasks for " + m.group(1).strip())
        m = re.search(r"team\s+(.+?)\s+tasks", q)
        if m:
            return tm.format_task_list(tm.list_tasks(team=m.group(1).strip()), header="Team " + m.group(1).strip() + " tasks")
        if q in ("overdue tasks", "overdue"):
            return tm.format_task_list(tm.overdue_tasks(), header="Overdue tasks")
        if q in ("urgent tasks", "urgent"):
            return tm.format_task_list(tm.list_tasks(priority="urgent"), header="Urgent tasks")
        if q in ("all tasks", "list tasks", "tasks dikhao", "show tasks"):
            return tm.format_task_list(tm.list_tasks(), header="All tasks")

        # --- Task status updates ---
        m = re.search(r"(?:complete|done|finish)\s+task\s+(.+)", q)
        if m:
            task = tm.find_task_by_title(m.group(1).strip())
            if not task:
                return "Task nahi mila: " + m.group(1).strip()
            tm.set_status(task["id"], "done")
            return "Task complete: " + task["title"]

        m = re.search(r"start\s+task\s+(.+)", q)
        if m:
            task = tm.find_task_by_title(m.group(1).strip())
            if not task:
                return "Task nahi mila: " + m.group(1).strip()
            tm.set_status(task["id"], "in_progress")
            return "Task shuru: " + task["title"]

        m = re.search(r"block(?:ed)?\s+task\s+(.+)", q)
        if m:
            task = tm.find_task_by_title(m.group(1).strip())
            if not task:
                return "Task nahi mila: " + m.group(1).strip()
            tm.set_status(task["id"], "blocked")
            return "Task blocked: " + task["title"]

        m = re.search(r"(?:delete|remove|cancel)\s+task\s+(.+)", q)
        if m:
            task = tm.find_task_by_title(m.group(1).strip())
            if not task:
                return "Task nahi mila: " + m.group(1).strip()
            tm.delete_task(task["id"])
            return "Task delete kar diya: " + task["title"]

        m = re.search(r"reassign\s+task\s+(.+?)\s+to\s+(.+)", q)
        if m:
            task = tm.find_task_by_title(m.group(1).strip())
            if not task:
                return "Task nahi mila: " + m.group(1).strip()
            tm.update_task(task["id"], assignee=m.group(2).strip())
            return "Task '%s' ab %s ko assign hai." % (task["title"], m.group(2).strip())

        return None
