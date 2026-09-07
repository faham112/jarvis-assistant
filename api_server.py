#!/usr/bin/env python3
"""MJ HTTP API for the React Native app and future clients."""

import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import ASSISTANT_NAME, OWNER_NAME, OLLAMA_MODEL
from core.llm import Brain
from core.commands import Router
from core import health
from core import logger

API_KEY = os.getenv("MJ_API_KEY", "change-me")
BLOCK = ("shutdown", "restart", "reboot", "lock screen", "close ", "volume")

app = FastAPI(title="MJ API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

brain = Brain()
router = Router(brain)


class ChatIn(BaseModel):
    text: str


class ChatOut(BaseModel):
    reply: str
    assistant: str = ASSISTANT_NAME


def _auth(x_api_key: Optional[str]):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(401, "Bad or missing X-API-Key")


@app.get("/health")
def health_ep(x_api_key: Optional[str] = Header(default=None)):
    _auth(x_api_key)
    return {
        "ok": True,
        "assistant": ASSISTANT_NAME,
        "owner": OWNER_NAME,
        "ollama": brain.online,
        "model": OLLAMA_MODEL,
        "system": health.system_health(),
    }


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, x_api_key: Optional[str] = Header(default=None)):
    _auth(x_api_key)
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(400, "text required")
    low = text.lower()
    if any(b in low for b in BLOCK):
        logger.log("api_block", text)
        return ChatOut(reply="Yeh command mobile API se band hai (safety).")
    reply = router.handle(text)
    if reply == "__EXIT__":
        reply = "API session yahan band nahi hoti. Local CLI use karo."
    logger.log("api_chat", text[:80])
    return ChatOut(reply=reply)


@app.get("/")
def root():
    return {"service": "mj-api", "docs": "/docs"}
