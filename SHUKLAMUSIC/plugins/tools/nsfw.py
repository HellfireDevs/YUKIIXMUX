import os
import aiohttp
import base64
import random
import asyncio
from PIL import Image
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from SHUKLAMUSIC import app
from config import BANNED_USERS, NSFWAPI

# ─────────────────────────────
# 🔥 NSFW STATE, EMOJIS & DATABASE
# ─────────────────────────────
chat_nsfw_state = {}
BANNED_STICKERS = set() # Fatafat block karne ke liye in-memory database

PREMIUM_EMOJIS = [
    '<emoji id="6334598469746952256">🎀</emoji>',
    '<emoji id="6334672948774831861">🎀</emoji>',
    '<emoji id="6334648089504122382">🎀</emoji>',
    '<emoji id="6334333036473091884">🎀</emoji>',
    '<emoji id="6334696528145286813">🎀</emoji>',
    '<emoji id="6334789677396002338">🎀</emoji>',
    '<emoji id="6334471179801200139">🎀</emoji>',
    '<emoji id="6334381440754517833">🎀</emoji>'
]

# ─────────────────────────────
# 🛠️ MANUAL BAN COMMAND (For Stickers)
# ─────────────────────────────
@app.on_message(filters.command("bansticker") & filters.reply & filters.group)
async def ban_manual_sticker(client, message: Message):
    if not message.reply_to_message.sticker:
        return await message.reply("<blockquote>⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ʙᴀɴ ɪᴛ!</blockquote>", parse_mode=ParseMode.HTML)
    
    sticker_id = message.reply_to_message.sticker.file_unique_id
    BANNED_STICKERS.add(sticker_id)
    
    try:
        await message.reply_to_message.delete()
    except: pass
    
    emo = random.choice(PREMIUM_EMOJIS)
    msg = await message.reply(f"<blockquote>✅ sᴛɪᴄᴋᴇʀ ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ! ɪᴛ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ɴᴏᴡ. {emo}</blockquote>", parse_mode=ParseMode.HTML)
    await asyncio.sleep(15)
    await msg.delete()

# ─────────────────────────────
# 🛠️ ON/OFF COMMAND
# ─────────────────────────────
@app.on_message(filters.command(["nsfw", "vision"]) & filters.group & ~BANNED_USERS)
async def toggle_nsfw(client, message: Message):
    chat_id = message.chat.id
    emo = random.choice(PREMIUM_EMOJIS)
    
    if len(message.command) < 2:
        state = chat_nsfw_state.get(chat_id, True)
        status = "ᴏɴ ✅" if state else "ᴏғғ ❌"
        msg_text = f"<blockquote>ᴠɪsɪᴏɴ sᴄᴀɴɴᴇʀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ **{status}**.\nᴛᴏ ᴄʜᴀɴɢᴇ, ᴛʏᴘᴇ: `/nsfw on` ᴏʀ `/nsfw off` {emo}</blockquote>"
        return await message.reply(msg_text, parse_mode=ParseMode.HTML)
    
    cmd = message.command[1].lower()
    if cmd == "on":
        chat_nsfw_state[chat_id] = True
        msg_text = f"<blockquote>✅ ᴠɪsɪᴏɴ sᴄᴀɴɴᴇʀ ɪs ɴᴏᴡ ᴏɴ. {emo}</blockquote>"
        msg = await message.reply(msg_text, parse_mode=ParseMode.HTML)
        await asyncio.sleep(15)
        await msg.delete()
    elif cmd == "off":
        chat_nsfw_state[chat_id] = False
        msg_text = f"<blockquote>❌ ᴠɪsɪᴏɴ sᴄᴀɴɴᴇʀ ɪs ɴᴏᴡ ᴏғғ. {emo}</blockquote>"
        msg = await message.reply(msg_text, parse_mode=ParseMode.HTML)
        await asyncio.sleep(15)
        await msg.delete()

# ─────────────────────────────
# 👁️ GROQ VISION ENGINE
# ─────────────────────────────
async def analyze_media_groq(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        jpg_path = image_path + ".jpg"
        img.save(jpg_path, "JPEG")
        
        with open(jpg_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        headers = {
            "Authorization": f"Bearer {NSFWAPI}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.2-11b-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Is this image safe or 18+/NSFW? Reply ONLY with '18+' if it has nudity, adult content, or is highly suggestive. Otherwise reply ONLY with 'SAFE'."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20) as resp:
                data = await resp.json()
                os.remove(jpg_path)
                
                if "choices" in data:
                    return data["choices"][0]["message"]["content"].strip().lower()
                else:
                    return "error"
                    
    except Exception as e:
        print(f"Groq Vision Crash: {e}")
        return "error"

# ─────────────────────────────
# 🚨 MAIN SCANNER (SILENT & DEADLY)
# ─────────────────────────────
@app.on_message((filters.photo | filters.sticker) & filters.group & ~BANNED_USERS)
async def nsfw_scanner(client, message: Message):
    chat_id = message.chat.id
    
    if not chat_nsfw_state.get(chat_id, True):
        return

    # 1. DATABASE CHECK (Superfast Auto-Delete, Completely Silent)
    if message.sticker:
        sticker_id = message.sticker.file_unique_id
        if sticker_id in BANNED_STICKERS:
            try:
                await message.delete()
            except Exception as e:
                # Permission warning if bot is not admin
                if "MESSAGE_DELETE_FORBIDDEN" in str(e) or "chat_admin_required" in str(e).lower():
                     emo = random.choice(PREMIUM_EMOJIS)
                     perm_msg = await client.send_message(chat_id, f"<blockquote>⚠️ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴍᴇ 'ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs' ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴡᴏʀᴋ ᴘʀᴏᴘᴇʀʟʏ! {emo}</blockquote>", parse_mode=ParseMode.HTML)
                     await asyncio.sleep(15)
                     await perm_msg.delete()
            return

    # 2. DOWNLOAD & SCAN (Thumbnail Bypass + Silent Delete)
    dl_path = None
    try:
        # Check if animated/video sticker and extract thumbnail
        if message.sticker and (message.sticker.is_animated or message.sticker.is_video):
            if message.sticker.thumbs:
                thumb_id = message.sticker.thumbs[0].file_id
                dl_path = await client.download_media(thumb_id)
            else:
                return # Skip if no thumbnail
        else:
            dl_path = await message.download()
        
        if dl_path:
            result = await analyze_media_groq(dl_path)
            
            if os.path.exists(dl_path):
                os.remove(dl_path)
                
            if "18+" in result or "nsfw" in result:
                if message.sticker:
                    BANNED_STICKERS.add(message.sticker.file_unique_id)
                    
                try:
                    await message.delete() # SILENT DELETE
                except Exception as e:
                    if "MESSAGE_DELETE_FORBIDDEN" in str(e) or "chat_admin_required" in str(e).lower():
                         emo = random.choice(PREMIUM_EMOJIS)
                         perm_msg = await client.send_message(chat_id, f"<blockquote>⚠️ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴍᴇ 'ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs' ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴡᴏʀᴋ ᴘʀᴏᴘᴇʀʟʏ! {emo}</blockquote>", parse_mode=ParseMode.HTML)
                         await asyncio.sleep(15)
                         await perm_msg.delete()
                
        # IF SAFE -> DO NOTHING
        
    except Exception as e:
        print(f"Scanner crash: {e}")
        if dl_path and os.path.exists(dl_path):
            os.remove(dl_path)
            
