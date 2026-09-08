#!/usr/bin/env python3
import os
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import ASSISTANT_NAME, OWNER_NAME, OLLAMA_MODEL
from core.llm import Brain
from core.commands import Router
from core import health, logger
from core import task_manager as tm

API_KEY = os.getenv("MJ_API_KEY", "change-me")
BLOCK = ("shutdown", "restart", "reboot", "lock screen")
app = FastAPI(title="MJ API", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
brain = Brain()
router = Router(brain)

class ChatIn(BaseModel):
    text: str
class ChatOut(BaseModel):
    reply: str
    assistant: str = ASSISTANT_NAME

def _extract_key(x_api_key, authorization, key):
    if x_api_key:
        return x_api_key.strip()
    if key:
        return key.strip()
    if authorization:
        a = authorization.strip()
        if a.lower().startswith("bearer "):
            return a[7:].strip()
        return a
    return ""

def _auth(x_api_key=None, authorization=None, key=None):
    sent = _extract_key(x_api_key, authorization, key)
    if not sent:
        raise HTTPException(401, "API key chahiye: header X-API-Key")
    if sent != API_KEY:
        raise HTTPException(401, "Galat API key")

@app.get("/")
def root():
    return {"service": "mj-api", "activate": "/activate", "chat": "/chat"}

@app.get("/activate")
def activate(x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _auth(x_api_key, authorization, key)
    return {"ok": True, "activated": True, "assistant": ASSISTANT_NAME, "ollama": brain.online, "model": OLLAMA_MODEL, "message": "MJ activate ho gayi."}

@app.get("/health")
def health_ep(x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _auth(x_api_key, authorization, key)
    return {"ok": True, "assistant": ASSISTANT_NAME, "owner": OWNER_NAME, "ollama": brain.online, "model": OLLAMA_MODEL, "system": health.system_health()}

@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _auth(x_api_key, authorization, key)
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "text required")
    if any(b in text.lower() for b in BLOCK):
        return ChatOut(reply="Yeh command remote API se band hai.")
    reply = router.handle(text)
    if reply == "__EXIT__":
        reply = "API session band nahi hoti."
    logger.log("api_chat", text[:80])
    return ChatOut(reply=reply)


# ---------------------------------------------------------------------------
# Teams & Tasks — advanced multi-user task management
# ---------------------------------------------------------------------------

class TeamIn(BaseModel):
    name: str
    description: str = ""

class MemberIn(BaseModel):
    name: str
    role: str = "member"

class TaskIn(BaseModel):
    title: str
    assignee: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None
    project: Optional[str] = None
    team: Optional[str] = None
    notes: str = ""

class TaskUpdateIn(BaseModel):
    title: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    project: Optional[str] = None
    notes: Optional[str] = None


def _check(x_api_key, authorization, key):
    _auth(x_api_key, authorization, key)


# --- Teams ---

@app.get("/teams")
def teams_list(x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    return {"teams": tm.list_teams()}

@app.post("/teams")
def teams_create(body: TeamIn, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    team = tm.create_team(body.name, body.description)
    logger.log("api_team_create", body.name)
    return team

@app.get("/teams/{team_name}")
def teams_get(team_name: str, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    team = tm.get_team(team_name)
    if not team:
        raise HTTPException(404, "Team not found")
    return team

@app.delete("/teams/{team_name}")
def teams_delete(team_name: str, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    if not tm.delete_team(team_name):
        raise HTTPException(404, "Team not found")
    return {"ok": True}

@app.post("/teams/{team_name}/members")
def teams_add_member(team_name: str, body: MemberIn, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    team = tm.add_member(team_name, body.name, body.role)
    logger.log("api_team_add_member", "%s -> %s" % (body.name, team_name))
    return team

@app.delete("/teams/{team_name}/members/{member_name}")
def teams_remove_member(team_name: str, member_name: str, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    team = tm.remove_member(team_name, member_name)
    if not team:
        raise HTTPException(404, "Team not found")
    return team

@app.get("/teams/{team_name}/workload")
def teams_workload(team_name: str, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    return {"team": team_name, "workload": tm.workload_summary(team=team_name)}


# --- Tasks ---

@app.get("/tasks")
def tasks_list(assignee: Optional[str] = None, status: Optional[str] = None,
                team: Optional[str] = None, project: Optional[str] = None,
                priority: Optional[str] = None,
                x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    return {"tasks": tm.list_tasks(assignee=assignee, status=status, team=team, project=project, priority=priority)}

@app.post("/tasks")
def tasks_create(body: TaskIn, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    task = tm.create_task(title=body.title, assignee=body.assignee, priority=body.priority,
                           due_date=body.due_date, project=body.project, team=body.team, notes=body.notes)
    logger.log("api_task_create", body.title)
    return task

@app.get("/tasks/overdue")
def tasks_overdue(team: Optional[str] = None, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    return {"tasks": tm.overdue_tasks(team=team)}

@app.get("/tasks/{task_id}")
def tasks_get(task_id: str, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    task = tm.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@app.patch("/tasks/{task_id}")
def tasks_update(task_id: str, body: TaskUpdateIn, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    fields = {k: v for k, v in body.dict().items() if v is not None}
    if "status" in fields and fields["status"] not in tm.STATUSES:
        raise HTTPException(400, "Invalid status")
    task = tm.update_task(task_id, **fields)
    if not task:
        raise HTTPException(404, "Task not found")
    logger.log("api_task_update", task_id)
    return task

@app.delete("/tasks/{task_id}")
def tasks_delete(task_id: str, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    if not tm.delete_task(task_id):
        raise HTTPException(404, "Task not found")
    return {"ok": True}

@app.post("/tasks/{task_id}/subtasks")
def tasks_add_subtask(task_id: str, body: dict, x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    title = (body or {}).get("title", "").strip()
    if not title:
        raise HTTPException(400, "title required")
    task = tm.add_subtask(task_id, title)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@app.get("/workload")
def workload_all(x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None), key: Optional[str] = Query(default=None)):
    _check(x_api_key, authorization, key)
    return {"workload": tm.workload_summary()}
