from pyrogram import filters
from pyrogram.types import Message
from SHUKLAMUSIC import app, YouTube
from SHUKLAMUSIC.utils.stream.stream import stream
from config import BANNED_USERS

# ✅ Hindi + Pop song URLs for autoplay
TRENDING_SONGS = [
    "https://www.youtube.com/watch?v=dvYMyqO2PZg",  # Saiyaara Lyrical – Ek Tha Tiger
    "https://www.youtube.com/watch?v=pbxgHqPizRg",  # Qatal – Guru Randhawa
    "https://www.youtube.com/watch?v=ZKzuh0AQSBI",  # Baby Doll Lyrics – Ragini MMS 2
    "https://www.youtube.com/watch?v=KJhL7U95Ug8",  # Pink Lips Lyrics – Hate Story 2
    "https://www.youtube.com/watch?v=WoBFeCRfV20",  # Tu Jaane Na Lyrics – Ajab Prem Ki Ghazab Kahani
    "https://www.youtube.com/watch?v=ghzMGkZC4nY",  # Offo Lyrics – 2 States
    "https://www.youtube.com/watch?v=j5uXpKoP_xk",  # Die With A Smile – Yashraj
    "https://www.youtube.com/watch?v=nfs8NYg7yQM",  # Attention – Charlie Puth
    "https://www.youtube.com/watch?v=az4R5G5v1bA",  # Pal Pal Dil Ke Paas – Arijit Singh
    "https://www.youtube.com/watch?v=GzU8KqOY8YA",  # Zaroorat – Ek Villain
]

@app.on_message(filters.command("autoplay", prefixes=["/", "!", "."]) & filters.group & ~BANNED_USERS)
async def autoplay_handler(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user
    user_id = user.id
    user_name = user.first_name

    msg = await message.reply_text("🎵 Fetching selected songs for autoplay...")

    for url in TRENDING_SONGS:
        try:
            details, _ = await YouTube.track(url)
        except Exception as e:
            await msg.edit_text(f"❌ Failed to fetch a song.\n`{e}`")
            continue

        try:
            await stream(
                _,
                msg,
                user_id,
                details,
                chat_id,
                user_name,
                chat_id,
                streamtype="youtube",
            )
        except Exception as e:
            await msg.edit_text(f"⚠️ Error streaming a song.\n`{e}`")
            continue

    await msg.edit_text("✅ Finished autoplay queue!")
