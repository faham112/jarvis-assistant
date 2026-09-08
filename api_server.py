#!/usr/bin/env python3
import os
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import ASSISTANT_NAME, OWNER_NAME, OLLAMA_MODEL
from core.llm import Brain
from core.commands import Router
from core import health, logger

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
