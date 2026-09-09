"""
MJ Humanize Layer
------------------
Small, dependency-free helpers that make MJ feel like a person typing/talking
instead of a bot firing instant, flat, uniform replies.

Three jobs:
1. typing_delay()   - how long a human would take to notice + type a reply
2. split_for_chat() - break a longer reply into 1-3 natural chat bubbles
3. speech_ssml()     - add natural pauses/breaths to text before TTS, and
                       jitter rate/pitch slightly so every line doesn't
                       sound identically paced
"""
import random
import re

# ---------------------------------------------------------------------------
# Typing delay — mimics human reaction + typing time, not instant bot replies
# ---------------------------------------------------------------------------

READING_DELAY_RANGE = (0.35, 0.9)   # time to "notice" the message and start typing
CHARS_PER_SECOND_RANGE = (11, 16)   # ~130-190 wpm typing speed, varies per "message"
MAX_DELAY = 4.5                     # never make someone wait forever for a reply
MIN_DELAY = 0.5


def typing_delay(text: str) -> float:
    """Seconds to wait before sending `text`, simulating human read+type time."""
    length = len(text or "")
    reading = random.uniform(*READING_DELAY_RANGE)
    cps = random.uniform(*CHARS_PER_SECOND_RANGE)
    typing = length / cps
    delay = reading + typing
    return max(MIN_DELAY, min(MAX_DELAY, delay))


# ---------------------------------------------------------------------------
# Chat bubble splitting — humans send 2 short texts more than 1 long paragraph
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?۔])\s+")


def split_for_chat(text: str, max_bubbles: int = 3) -> list:
    """
    Break a reply into up to `max_bubbles` short chat messages.
    Short replies (<=1 sentence or <90 chars) stay as a single bubble —
    only genuinely multi-idea replies get split, so it doesn't feel gimmicky.
    """
    text = (text or "").strip()
    if not text:
        return [text]
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    if len(sentences) <= 1 or len(text) < 90:
        return [text]

    bubbles = []
    current = ""
    for s in sentences:
        candidate = (current + " " + s).strip() if current else s
        if len(candidate) > 140 and current:
            bubbles.append(current)
            current = s
        else:
            current = candidate
    if current:
        bubbles.append(current)

    if len(bubbles) > max_bubbles:
        head = bubbles[:max_bubbles - 1]
        tail = " ".join(bubbles[max_bubbles - 1:])
        bubbles = head + [tail]
    return bubbles


def bubble_delay(bubble: str) -> float:
    """Shorter pause between consecutive bubbles in the same reply (already 'typing')."""
    length = len(bubble or "")
    return max(0.4, min(2.2, 0.2 + length / 22))


# ---------------------------------------------------------------------------
# Speech pacing — natural pauses + light jitter so TTS isn't machine-uniform
# ---------------------------------------------------------------------------

_PAUSE_MAP = (
    (re.compile(r"([.!?۔])(\s|$)"), r'\1<break time="380ms"/>\2'),
    (re.compile(r"([,،])(\s)"), r'\1<break time="160ms"/>\2'),
)


def add_natural_pauses(text: str) -> str:
    """Insert SSML <break> tags at sentence/comma boundaries for edge-tts."""
    out = text or ""
    for pattern, repl in _PAUSE_MAP:
        out = pattern.sub(repl, out)
    return out


def jittered_rate(base_pct: int = -8, spread: int = 4) -> str:
    """Small randomized rate so consecutive replies don't sound identically paced."""
    val = base_pct + random.randint(-spread, spread)
    sign = "+" if val >= 0 else ""
    return "%s%d%%" % (sign, val)


def jittered_pitch(base_hz: int = 8, spread: int = 3) -> str:
    val = base_hz + random.randint(-spread, spread)
    sign = "+" if val >= 0 else ""
    return "%s%dHz" % (sign, val)


# ---------------------------------------------------------------------------
# Light conversational texture — small, sparing touches, never overused
# ---------------------------------------------------------------------------

_ACK_STARTERS = ("hmm, ", "acha, ", "ok, ", "theek hai, ", "")  # empty = no starter, most common


def maybe_prefix_ack(text: str, chance: float = 0.15) -> str:
    """Occasionally (not always) prepend a small natural acknowledgment. Sparing on purpose."""
    if not text or text[0:1] in ("[", "{"):
        return text
    if random.random() < chance:
        starter = random.choice(_ACK_STARTERS[:-1])
        return starter + text[0].lower() + text[1:] if starter else text
    return text
