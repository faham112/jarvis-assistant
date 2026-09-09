import asyncio, os, re, subprocess, tempfile
import requests
from core.roman_urdu import to_urdu
from config import (
    OLLAMA_HOST, OLLAMA_MODEL,
    MJ_TTS_TARGET_LUFS, MJ_URDU_VOICE_FEMALE, MJ_URDU_VOICE_MALE,
)

URDU_VOICE = os.getenv("MJ_VOICE", MJ_URDU_VOICE_FEMALE)
ROMAN_VOICE = os.getenv("MJ_ROMAN_VOICE", "en-IN-NeerjaNeural")
RATE = os.getenv("MJ_VOICE_RATE", "-8%")
PITCH = os.getenv("MJ_VOICE_PITCH", "+8Hz")


def _urdu_ratio(s):
    if not s:
        return 0
    return len(re.findall(r"[\u0600-\u06FF]", s)) / max(len(s), 1)


# ---------------------------------------------------------------------------
# Real Urdu translation via the local LLM (Ollama) — used for "pure Urdu"
# mode instead of the crude word-by-word roman->Urdu substitution map, which
# produces broken grammar. Falls back to the old heuristic if Ollama is down,
# so this never hard-fails.
# ---------------------------------------------------------------------------

_TRANSLATE_PROMPT = (
    "Translate the following into natural, fluent Urdu script (not "
    "transliteration, not word-by-word). Reply with ONLY the Urdu "
    "translation, nothing else, no quotes, no explanation:\n\n"
)


def translate_to_urdu(text: str, timeout: float = 8.0) -> str:
    text = (text or "").strip()
    if not text:
        return "ٹھیک ہے۔"
    if _urdu_ratio(text) >= 0.6:
        return text  # already Urdu script, nothing to do
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": _TRANSLATE_PROMPT + text}],
                "stream": False,
            },
            timeout=timeout,
        )
        r.raise_for_status()
        out = (r.json().get("message") or {}).get("content", "").strip()
        out = out.strip('"').strip()
        if out and _urdu_ratio(out) >= 0.4:
            return out
    except Exception:
        pass
    # Fallback: old heuristic word map (better than nothing if Ollama is down)
    return to_urdu(text)


# ---------------------------------------------------------------------------
# Loudness normalization — fixes inconsistent / too-quiet playback in Discord.
# Two-pass-style ffmpeg loudnorm to a broadcast-style target, independent of
# whatever raw level edge-tts/gTTS happened to produce.
# ---------------------------------------------------------------------------

def normalize_loudness(path: str, target_lufs: float = None) -> str:
    target_lufs = MJ_TTS_TARGET_LUFS if target_lufs is None else target_lufs
    out_path = path + ".norm.mp3"
    cmd = [
        "ffmpeg", "-y", "-i", path,
        "-af", "loudnorm=I=%s:TP=-1.5:LRA=11" % target_lufs,
        "-ar", "48000", "-b:a", "128k",
        out_path,
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        timeout=20, check=True)
        if os.path.getsize(out_path) > 200:
            try:
                os.unlink(path)
            except OSError:
                pass
            return out_path
    except Exception:
        pass
    # normalization failed for any reason — just use the original clip
    try:
        os.unlink(out_path)
    except OSError:
        pass
    return path


# ---------------------------------------------------------------------------
# TTS entry point
# ---------------------------------------------------------------------------

def tts_mp3(text, force_urdu=False, voice_gender="female"):
    raw = (text or "Theek hai.")[:500]

    if force_urdu:
        script = translate_to_urdu(raw)
        voice = MJ_URDU_VOICE_MALE if voice_gender == "male" else MJ_URDU_VOICE_FEMALE
        spoken = script
    else:
        script = to_urdu(raw)
        if _urdu_ratio(script) >= 0.35:
            spoken, voice = script, URDU_VOICE
        else:
            spoken, voice = raw, ROMAN_VOICE

    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    ok = False
    try:
        import edge_tts
        async def _run():
            await edge_tts.Communicate(spoken, voice, rate=RATE, pitch=PITCH).save(path)
        asyncio.run(_run())
        if os.path.getsize(path) > 200:
            ok = True
    except Exception:
        ok = False

    if not ok:
        try:
            from gtts import gTTS
            is_urdu = force_urdu or _urdu_ratio(script) >= 0.35
            try:
                gTTS(text=spoken if is_urdu else raw, lang="ur" if is_urdu else "en").save(path)
            except Exception:
                gTTS(text=raw, lang="en").save(path)
            if os.path.getsize(path) > 200:
                ok = True
        except Exception:
            ok = False

    if not ok:
        # Both TTS engines failed (e.g. offline/outage) — never crash the bot.
        # Generate a short local tone so callers always get a playable file back.
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
                 "-b:a", "128k", path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=True,
            )
        except Exception:
            # last resort: touch an empty file so downstream code doesn't crash on missing path
            open(path, "wb").close()

    return normalize_loudness(path)
