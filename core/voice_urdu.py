import asyncio, os, tempfile
from core.roman_urdu import to_urdu

VOICE = os.getenv("MJ_VOICE", "ur-PK-UzmaNeural")
RATE = os.getenv("MJ_VOICE_RATE", "-12%")

def tts_mp3(text):
    spoken = to_urdu(text or "Theek hai.")[:500]
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        import edge_tts
        async def _run():
            await edge_tts.Communicate(spoken, VOICE, rate=RATE).save(path)
        asyncio.run(_run())
        if os.path.getsize(path) > 200:
            return path
    except Exception:
        pass
    from gtts import gTTS
    try:
        gTTS(text=spoken, lang="ur", slow=False).save(path)
    except Exception:
        gTTS(text=spoken, lang="hi", slow=False).save(path)
    return path
