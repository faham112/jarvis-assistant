#!/usr/bin/env python3
import asyncio, os, subprocess, tempfile
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
import speech_recognition as sr
from core.voice_urdu import tts_mp3
from core import humanize
load_dotenv()
from core.llm import Brain
from core.commands import Router
from config import MJ_DISCORD_VOLUME, MJ_URDU_MODE_DEFAULT

TOKEN = os.getenv("DISCORD_TOKEN", "")
OWNER_ID = os.getenv("DISCORD_OWNER_ID", "").strip()
PREFIX = os.getenv("DISCORD_PREFIX", "!")
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
brain = Brain()
router = Router(brain)

# Per-channel pure-Urdu toggle ("!mj urdu on" / "!mj urdu off"), defaults from env.
URDU_MODE = {}

def urdu_on(channel_id):
    return URDU_MODE.get(channel_id, MJ_URDU_MODE_DEFAULT)

def allowed(user):
    if not OWNER_ID:
        return True
    return str(user.id) == OWNER_ID

def _normalize_input_audio(wav_path):
    """Boost/normalize a recorded voice note before STT — fixes quiet mics
    producing garbled or empty transcriptions ('voice level not fine' cuts
    both ways: playback AND recognition input)."""
    out = wav_path + ".norm.wav"
    cmd = ["ffmpeg", "-y", "-i", wav_path, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
           "-ar", "16000", "-ac", "1", out]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        timeout=15, check=True)
        if os.path.getsize(out) > 200:
            return out
    except Exception:
        pass
    return wav_path

def transcribe(path, urdu_only=False):
    r = sr.Recognizer()
    wav = path
    if not path.endswith(".wav"):
        out = path + ".wav"
        os.system('ffmpeg -y -i "%s" -ar 16000 -ac 1 "%s" >/dev/null 2>&1' % (path, out))
        wav = out
    wav = _normalize_input_audio(wav)
    with sr.AudioFile(wav) as src:
        audio = r.record(src)
    try:
        return r.recognize_google(audio, language="ur-PK")
    except Exception:
        if urdu_only:
            return ""
        try:
            return r.recognize_google(audio, language="en-US")
        except Exception:
            return ""

async def ensure_voice(ctx):
    author = getattr(ctx, "author", None)
    if not author or not getattr(author, "voice", None):
        return
    ch = author.voice.channel
    vc = ctx.voice_client
    try:
        if vc and vc.is_connected():
            if vc.channel != ch:
                await vc.move_to(ch)
        else:
            await ch.connect()
    except Exception:
        pass

async def speak(ctx, text):
    force_urdu = urdu_on(ctx.channel.id if ctx.channel else None)
    path = await asyncio.to_thread(tts_mp3, text, force_urdu)
    await ensure_voice(ctx)
    played = False
    if ctx.voice_client and ctx.voice_client.is_connected():
        try:
            raw_src = discord.FFmpegPCMAudio(path)
            # Explicit playback gain on top of source loudness normalization —
            # this is what actually fixes low/inconsistent voice levels in-call.
            src = discord.PCMVolumeTransformer(raw_src, volume=MJ_DISCORD_VOLUME)
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            done = asyncio.Event()
            ctx.voice_client.play(src, after=lambda e: done.set())
            await asyncio.wait_for(done.wait(), timeout=60)
            played = True
        except Exception:
            played = False
    extra = "" if played else " Play mj-reply.mp3"
    try:
        await ctx.send("**MJ:** " + text[:1500] + extra, file=discord.File(path, filename="mj-reply.mp3"))
    except Exception:
        await ctx.send("**MJ:** " + text[:1900])
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass

async def _send_humanized(ctx, reply):
    """Split long replies into natural chat bubbles with human-like typing pauses."""
    bubbles = humanize.split_for_chat(reply)
    for i, bubble in enumerate(bubbles):
        delay = humanize.typing_delay(bubble) if i == 0 else humanize.bubble_delay(bubble)
        try:
            async with ctx.channel.typing():
                await asyncio.sleep(delay)
        except Exception:
            await asyncio.sleep(delay)
        await ctx.send("**MJ:** " + bubble[:1900])

async def handle_line(ctx, line, voice=False):
    async with ctx.channel.typing():
        reply = await asyncio.to_thread(router.handle, line)
    if reply == "__EXIT__":
        reply = "Discord pe main yahin rehti hoon."
    if voice:
        await asyncio.sleep(humanize.typing_delay(reply))
        await speak(ctx, reply)
    else:
        await _send_humanized(ctx, reply)

@bot.event
async def on_ready():
    print("[Discord] logged in as", bot.user)

@bot.command(name="join")
async def cmd_join(ctx):
    if not allowed(ctx.author):
        return
    if not ctx.author.voice:
        await ctx.send("Pehle voice channel mein jao, phir !join")
        return
    ch = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(ch)
    else:
        await ch.connect()
    await ctx.send("Voice note = awaz. Type = text.")

@bot.command(name="leave")
async def cmd_leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    await ctx.send("Nikal gayi.")

@bot.command(name="mj")
async def cmd_mj(ctx, *, text: str = ""):
    if not allowed(ctx.author):
        return
    text = text.strip()
    low = text.lower()
    if low in ("urdu on", "urdu mode on", "pure urdu on"):
        URDU_MODE[ctx.channel.id] = True
        await ctx.send("Theek hai, ab main sirf Urdu mein bolungi.")
        return
    if low in ("urdu off", "urdu mode off", "pure urdu off"):
        URDU_MODE[ctx.channel.id] = False
        await ctx.send("Ok, wapas normal (Roman Urdu/English mix).")
        return
    if text:
        await handle_line(ctx, text, voice=False)

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    await bot.process_commands(msg)
    if not allowed(msg.author):
        return
    if msg.content.startswith(PREFIX):
        return
    for att in msg.attachments:
        name = (att.filename or "").lower()
        ctype = (att.content_type or "")
        if "audio" in ctype or name.endswith((".ogg", ".mp3", ".wav", ".m4a", ".webm")):
            path = str(Path(tempfile.gettempdir()) / (att.filename or "voice.ogg"))
            await att.save(path)
            urdu_only = urdu_on(msg.channel.id)
            text = await asyncio.to_thread(transcribe, path, urdu_only)
            ctx = await bot.get_context(msg)
            if not text:
                await msg.channel.send("Awaz samajh nahi aayi — thoda paas se aur zor se bolo.")
                return
            await msg.channel.send("*suna:* " + text)
            await handle_line(ctx, text, voice=True)
            return
    if isinstance(msg.channel, discord.DMChannel) or (bot.user and bot.user in msg.mentions):
        line = msg.content
        for m in msg.mentions:
            line = line.replace(m.mention, "")
        line = line.strip()
        if line:
            ctx = await bot.get_context(msg)
            await handle_line(ctx, line, voice=False)

def main():
    if not TOKEN:
        print("Set DISCORD_TOKEN")
        return
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

