import YUKIIMUSIC.yuki_guard
from pyrogram import filters
from YUKIIMUSIC import app
from YUKIIMUSIC.misc import SUDOERS

@app.on_message(filters.video & filters.private & SUDOERS)
async def get_video_id(client, message):
    # Jaise hi tu video bhejega, bot uski file_id reply kar dega
    file_id = message.video.file_id
    await message.reply_text(f"**Yᴇ ʀᴀʜɪ Tᴇʀɪ Fɪʟᴇ ID:**\n\n`{file_id}`")
    
