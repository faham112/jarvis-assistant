#!/usr/bin/env python3
"""MJ — local voice assistant. Wake phrase: Hey MJ."""

import sys
import time

from config import ASSISTANT_NAME, OWNER_NAME, SESSION_SECONDS
from core.tts import Speaker
from core.stt import Listener
from core.wake import contains_wake, strip_wake
from core.llm import Brain
from core.commands import Router


def main():
    speaker = Speaker()
    listener = Listener()
    brain = Brain()
    router = Router(brain)

    speaker.say(f"{ASSISTANT_NAME} online, {OWNER_NAME}. Say Hey MJ, then the command.")
    print("Text bhi chalega. Empty Enter = mic. Quit: goodbye")
    print("Wake: hey mj | hey jarvis | mj")

    session_until = 0.0

    while True:
        try:
            typed = input("\nYou (text / Enter=voice): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOffline.")
            break

        if typed:
            raw = typed.lower()
        else:
            raw = listener.listen("Listening...", timeout=8)
            if not raw:
                continue

        now = time.time()
        in_session = now < session_until

        if contains_wake(raw):
            leftover = strip_wake(raw)
            speaker.say("Yes?")
            session_until = time.time() + SESSION_SECONDS
            if leftover:
                command = leftover
            else:
                command = listener.listen("Command?", timeout=8)
                if not command:
                    speaker.say("Did not catch that.")
                    continue
        elif in_session:
            command = raw
            session_until = time.time() + SESSION_SECONDS
        elif typed:
            command = raw
        else:
            print("(Wake word nahi suna. Hey MJ bolo.)")
            continue

        reply = router.handle(command)
        if reply == "__EXIT__":
            speaker.say("Going offline.")
            break
        speaker.say(reply)
        session_until = time.time() + SESSION_SECONDS


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
