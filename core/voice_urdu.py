import asyncio, os, re, tempfile
from core.roman_urdu import to_urdu

URDU_VOICE = os.getenv("MJ_VOICE", "ur-PK-UzmaNeural")
ROMAN_VOICE = os.getenv("MJ_ROMAN_VOICE", "en-IN-NeerjaNeural")
RATE = os.getenv("MJ_VOICE_RATE", "-8%")
PITCH = os.getenv("MJ_VOICE_PITCH", "+8Hz")

def _urdu_ratio(s):
    if not s:
        return 0
    return len(re.findall(r"[\u0600-\u06FF]", s)) / max(len(s), 1)

def tts_mp3(text):
    raw = (text or "Theek hai.")[:500]
    script = to_urdu(raw)
    if _urdu_ratio(script) >= 0.35:
        spoken, voice = script, URDU_VOICE
    else:
        spoken, voice = raw, ROMAN_VOICE
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        import edge_tts
        async def _run():
            await edge_tts.Communicate(spoken, voice, rate=RATE, pitch=PITCH).save(path)
        asyncio.run(_run())
        if os.path.getsize(path) > 200:
            return path
    except Exception:
        pass
    from gtts import gTTS
    try:
        gTTS(text=spoken if _urdu_ratio(script) >= 0.35 else raw,
             lang="ur" if _urdu_ratio(script) >= 0.35 else "en").save(path)
    except Exception:
        gTTS(text=raw, lang="en").save(path)
    return path
