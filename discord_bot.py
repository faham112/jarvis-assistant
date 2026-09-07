#!/usr/bin/env python3
import asyncio, os, tempfile
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
import speech_recognition as sr

load_dotenv()
from core.llm import Brain
from core.commands import Router

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

def allowed(user):
    if not OWNER_ID:
        return True
    return str(user.id) == OWNER_ID

def tts_mp3(text):
    clean = (text or "Okay.")[:400]
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    gTTS(text=clean, lang="en").save(path)
    return path

def transcribe(path):
    r = sr.Recognizer()
    wav = path
    if not path.endswith(".wav"):
        out = path + ".wav"
        os.system('ffmpeg -y -i "%s" -ar 16000 -ac 1 "%s" >/dev/null 2>&1' % (path, out))
        wav = out
    with sr.AudioFile(wav) as src:
        audio = r.record(src)
    try:
        return r.recognize_google(audio)
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
    path = await asyncio.to_thread(tts_mp3, text)
    await ensure_voice(ctx)
    played = False
    if ctx.voice_client and ctx.voice_client.is_connected():
        try:
            src = discord.FFmpegPCMAudio(path)
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

async def handle_line(ctx, line):
    reply = await asyncio.to_thread(router.handle, line)
    if reply == "__EXIT__":
        reply = "Discord pe main yahin rehta hoon."
    await speak(ctx, reply)

@bot.event
async def on_ready():
    print("[Discord] logged in as", bot.user)

@bot.command(name="join")
async def cmd_join(ctx):
    if not allowed(ctx.author):
        return
    if not ctx.author.voice:
        await ctx.send("Voice channel mein jao phir !join")
        return
    ch = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(ch)
    else:
        await ch.connect()
    await ctx.send("MJ voice pe. Voice note bhejo ya !mj time")

@bot.command(name="leave")
async def cmd_leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    await ctx.send("Nikal gaya.")

@bot.command(name="mj")
async def cmd_mj(ctx, *, text: str = ""):
    if not allowed(ctx.author):
        return
    if text.strip():
        await handle_line(ctx, text.strip())

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
            text = await asyncio.to_thread(transcribe, path)
            ctx = await bot.get_context(msg)
            if not text:
                await msg.channel.send("Awaz samajh nahi aayi. Voice note dobara.")
                return
            await msg.channel.send("*suna:* " + text)
            await handle_line(ctx, text)
            return
    if isinstance(msg.channel, discord.DMChannel) or (bot.user and bot.user in msg.mentions):
        line = msg.content
        for m in msg.mentions:
            line = line.replace(m.mention, "")
        line = line.strip()
        if line:
            ctx = await bot.get_context(msg)
            await handle_line(ctx, line)

def main():
    if not TOKEN:
        print("Set DISCORD_TOKEN")
        return
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
