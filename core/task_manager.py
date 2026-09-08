"""
MJ Task & Team Manager
-----------------------
Advanced task management for MJ: multi-user teams, task assignment,
priorities, due dates, statuses, projects, and simple workload analytics.

Storage: two flat JSON files under DATA_DIR (data/tasks.json, data/teams.json).
No external DB dependency, keeps the "works offline" spirit of the rest of MJ.
"""
import json
import uuid
from datetime import datetime, date
from pathlib import Path

from config import DATA_DIR

TASKS_FILE = DATA_DIR / "tasks.json"
TEAMS_FILE = DATA_DIR / "teams.json"

PRIORITIES = ("low", "medium", "high", "urgent")
STATUSES = ("todo", "in_progress", "blocked", "done", "cancelled")


# ---------------------------------------------------------------------------
# Low-level storage helpers
# ---------------------------------------------------------------------------

def _load(path: Path, default):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save(path: Path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    tmp.replace(path)


def _new_id():
    return uuid.uuid4().hex[:8]


def _now():
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def _load_teams():
    return _load(TEAMS_FILE, {"teams": {}})


def _save_teams(data):
    _save(TEAMS_FILE, data)


def create_team(name, description=""):
    data = _load_teams()
    for t in data["teams"].values():
        if t["name"].lower() == name.lower():
            return t
    team_id = _new_id()
    team = {
        "id": team_id,
        "name": name,
        "description": description,
        "created_at": _now(),
        "members": [],
    }
    data["teams"][team_id] = team
    _save_teams(data)
    return team


def add_member(team_name, member_name, role="member"):
    data = _load_teams()
    team = _find_team(data, team_name)
    if not team:
        team = create_team(team_name)
        data = _load_teams()
        team = data["teams"][team["id"]]
    for m in team["members"]:
        if m["name"].lower() == member_name.lower():
            m["role"] = role
            _save_teams(data)
            return team
    team["members"].append({"name": member_name, "role": role, "added_at": _now()})
    _save_teams(data)
    return team


def remove_member(team_name, member_name):
    data = _load_teams()
    team = _find_team(data, team_name)
    if not team:
        return None
    team["members"] = [m for m in team["members"] if m["name"].lower() != member_name.lower()]
    _save_teams(data)
    return team


def list_teams():
    data = _load_teams()
    return list(data["teams"].values())


def get_team(team_name):
    data = _load_teams()
    return _find_team(data, team_name)


def _find_team(data, team_name):
    for t in data["teams"].values():
        if t["name"].lower() == team_name.lower() or t["id"] == team_name:
            return t
    return None


def delete_team(team_name):
    data = _load_teams()
    team = _find_team(data, team_name)
    if not team:
        return False
    del data["teams"][team["id"]]
    _save_teams(data)
    return True


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def _load_tasks():
    return _load(TASKS_FILE, {"tasks": {}})


def _save_tasks(data):
    _save(TASKS_FILE, data)


def create_task(title, assignee=None, priority="medium", due_date=None,
                 project=None, team=None, notes=""):
    priority = priority.lower() if priority else "medium"
    if priority not in PRIORITIES:
        priority = "medium"
    task_id = _new_id()
    task = {
        "id": task_id,
        "title": title.strip(),
        "assignee": assignee,
        "team": team,
        "project": project,
        "priority": priority,
        "status": "todo",
        "due_date": due_date,  # expected "YYYY-MM-DD" or None
        "notes": notes,
        "created_at": _now(),
        "updated_at": _now(),
        "completed_at": None,
        "subtasks": [],
    }
    data = _load_tasks()
    data["tasks"][task_id] = task
    _save_tasks(data)
    return task


def add_subtask(task_id, title):
    data = _load_tasks()
    task = data["tasks"].get(task_id)
    if not task:
        return None
    task["subtasks"].append({"id": _new_id(), "title": title, "done": False})
    task["updated_at"] = _now()
    _save_tasks(data)
    return task


def complete_subtask(task_id, subtask_title):
    data = _load_tasks()
    task = data["tasks"].get(task_id)
    if not task:
        return None
    for st in task["subtasks"]:
        if st["title"].lower() == subtask_title.lower():
            st["done"] = True
    task["updated_at"] = _now()
    _save_tasks(data)
    return task


def update_task(task_id, **fields):
    data = _load_tasks()
    task = data["tasks"].get(task_id)
    if not task:
        return None
    for k, v in fields.items():
        if k in task and v is not None:
            task[k] = v
    task["updated_at"] = _now()
    if fields.get("status") == "done" and not task.get("completed_at"):
        task["completed_at"] = _now()
    _save_tasks(data)
    return task


def set_status(task_id, status):
    if status not in STATUSES:
        return None
    return update_task(task_id, status=status)


def delete_task(task_id):
    data = _load_tasks()
    if task_id in data["tasks"]:
        del data["tasks"][task_id]
        _save_tasks(data)
        return True
    return False


def get_task(task_id):
    data = _load_tasks()
    return data["tasks"].get(task_id)


def list_tasks(assignee=None, status=None, team=None, project=None, priority=None):
    data = _load_tasks()
    items = list(data["tasks"].values())
    if assignee:
        items = [t for t in items if (t.get("assignee") or "").lower() == assignee.lower()]
    if status:
        items = [t for t in items if t.get("status") == status]
    if team:
        items = [t for t in items if (t.get("team") or "").lower() == team.lower()]
    if project:
        items = [t for t in items if (t.get("project") or "").lower() == project.lower()]
    if priority:
        items = [t for t in items if t.get("priority") == priority]
    order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    items.sort(key=lambda t: (order.get(t.get("priority"), 2), t.get("due_date") or "9999-99-99"))
    return items


def find_task_by_title(title, assignee=None):
    title = title.lower().strip()
    for t in list_tasks(assignee=assignee):
        if title in t["title"].lower():
            return t
    return None


def overdue_tasks(team=None):
    today = date.today().isoformat()
    items = list_tasks(team=team)
    return [t for t in items
            if t.get("due_date") and t["due_date"] < today and t.get("status") not in ("done", "cancelled")]


# ---------------------------------------------------------------------------
# Analytics / summaries
# ---------------------------------------------------------------------------

def workload_summary(team=None):
    """Per-assignee counts of open vs done tasks — for team dashboards."""
    items = list_tasks(team=team)
    summary = {}
    for t in items:
        who = t.get("assignee") or "Unassigned"
        s = summary.setdefault(who, {"open": 0, "done": 0, "overdue": 0, "urgent": 0})
        if t.get("status") == "done":
            s["done"] += 1
        else:
            s["open"] += 1
            if t.get("priority") == "urgent":
                s["urgent"] += 1
            if t.get("due_date") and t["due_date"] < date.today().isoformat():
                s["overdue"] += 1
    return summary


def format_task_line(t):
    due = " (due %s)" % t["due_date"] if t.get("due_date") else ""
    who = " -> %s" % t["assignee"] if t.get("assignee") else ""
    return "[%s] %s%s%s  {%s/%s}" % (
        t["priority"][:1].upper(), t["title"], who, due, t["status"], t["id"]
    )


def format_task_list(tasks, header="Tasks"):
    if not tasks:
        return "%s: koi nahi mila." % header
    lines = ["%s (%d):" % (header, len(tasks))]
    for t in tasks:
        lines.append("- " + format_task_line(t))
    return "\n".join(lines)


def format_workload(summary):
    if not summary:
        return "Koi task nahi hai abhi."
    lines = ["Team workload:"]
    for who, s in sorted(summary.items(), key=lambda kv: -kv[1]["open"]):
        lines.append(
            "- %s: %d open, %d done%s%s" % (
                who, s["open"], s["done"],
                (", %d overdue" % s["overdue"]) if s["overdue"] else "",
                (", %d urgent" % s["urgent"]) if s["urgent"] else "",
            )
        )
    return "\n".join(lines)
