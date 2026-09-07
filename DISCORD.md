# MJ on Discord (voice)

VPS speaker ki zaroorat nahi. MJ VC mein gTTS se bolta hai.

## Discord portal (ek dafa)

1. https://discord.com/developers/applications → New Application `MJ`
2. Bot → Add Bot → Reset Token → copy
3. Privileged intents ON: MESSAGE CONTENT, SERVER MEMBERS optional
4. OAuth2 → URL Generator → scopes: `bot` `applications.commands`
5. Bot permissions: Send Messages, Connect, Speak, Attach Files, Read Message History
6. URL open karke apne server pe invite
7. Discord Advanced → Developer Mode ON → apni profile pe right click Copy User ID

## VPS

```bash
sudo apt install -y ffmpeg
cd jarvis-assistant
git pull
pip install -r requirements.txt
```

`.env`:

```
DISCORD_TOKEN=paste_token
DISCORD_OWNER_ID=your_numeric_id
DISCORD_PREFIX=!
MJ_API_KEY=change-me
```

```bash
chmod +x scripts/start-mj-discord
python3 discord_bot.py
```

## Use

1. Voice channel join
2. Text channel: `!join`
3. `!mj system health` ya `@MJ time`
4. Mobile: Discord **voice message** bhejo — MJ sunta hai, VC mein jawab bolta hai
5. `!leave`

Sirf OWNER_ID wala user chalata hai.
