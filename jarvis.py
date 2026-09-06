#!/usr/bin/env python3
"""
Jarvis — a simple cross-platform voice assistant for Windows 10/11 and Linux.
"""

import sys

from config import ASSISTANT_NAME, WAKE_WORDS
from core.tts import Speaker
from core.stt import Listener
from core.commands import handle


def is_wake(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in WAKE_WORDS)


def main():
    speaker = Speaker()
    listener = Listener()

    speaker.say(f"{ASSISTANT_NAME} online. Say Jarvis, then give a command. Or type instead.")
    print("Text mode: type a command and press Enter. Empty line = listen on mic.")
    print("Quit: exit / quit / goodbye")

    while True:
        try:
            typed = input("\nYou (text, or Enter for voice): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down.")
            break

        if typed:
            command = typed.lower()
        else:
            heard = listener.listen("Listening...")
            if not heard:
                continue
            if is_wake(heard):
                speaker.say("Yes?")
                command = listener.listen("Command?")
                if not command:
                    speaker.say("I did not catch that.")
                    continue
            else:
                command = heard

        reply = handle(command)
        if reply == "__EXIT__":
            speaker.say("Going offline. Goodbye.")
            break
        speaker.say(reply)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
