import asyncio, os, tempfile

VOICE = os.getenv("MJ_VOICE", "ur-PK-UzmaNeural")

def tts_mp3(text):
    clean = (text or "Theek hai.")[:400]
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        import edge_tts
        async def _run():
            await edge_tts.Communicate(clean, VOICE).save(path)
        asyncio.run(_run())
        if os.path.getsize(path) > 200:
            return path
    except Exception:
        pass
    from gtts import gTTS
    try:
        gTTS(text=clean, lang="ur").save(path)
    except Exception:
        gTTS(text=clean, lang="hi").save(path)
    return path
