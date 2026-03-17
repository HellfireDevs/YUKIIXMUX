import os
import aiohttp
import base64
import random
from PIL import Image
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode

from SHUKLAMUSIC import app
from config import BANNED_USERS

# ─────────────────────────────
# 🔥 NSFW STATE & EMOJIS
# ─────────────────────────────
chat_nsfw_state = {}

OLLAMA_VISION = "http://localhost:11434/api/generate"

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
# ✨ SMALL CAPS FONT CONVERTER
# ─────────────────────────────
SMALL_CAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
    'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ',
    'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
    'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ',
    'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
}

def to_small_caps(text: str) -> str:
    return "".join(SMALL_CAPS_MAP.get(c, c) for c in text)

# ─────────────────────────────
# 🛠️ ON/OFF COMMAND
# ─────────────────────────────
@app.on_message(filters.command(["nsfw", "vision"]) & filters.group & ~BANNED_USERS)
async def toggle_nsfw(client, message: Message):
    chat_id = message.chat.id
    emo = random.choice(PREMIUM_EMOJIS)
    
    if len(message.command) < 2:
        state = chat_nsfw_state.get(chat_id, True) # Default True
        status = "ᴏɴ ✅" if state else "ᴏғғ ❌"
        msg = f"ᴠɪsɪᴏɴ sᴄᴀɴɴᴇʀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ **{status}**.\nᴛᴏ ᴄʜᴀɴɢᴇ, ᴛʏᴘᴇ: `/nsfw on` ᴏʀ `/nsfw off` {emo}"
        return await message.reply(msg, parse_mode=ParseMode.HTML)
    
    cmd = message.command[1].lower()
    if cmd == "on":
        chat_nsfw_state[chat_id] = True
        msg = f"✅ ᴠɪsɪᴏɴ sᴄᴀɴɴᴇʀ ɪs ɴᴏᴡ ᴏɴ. ᴀʟʟ ᴍᴇᴅɪᴀ ᴡɪʟʟ ʙᴇ ᴄʜᴇᴄᴋᴇᴅ! {emo}"
        await message.reply(msg, parse_mode=ParseMode.HTML)
    elif cmd == "off":
        chat_nsfw_state[chat_id] = False
        msg = f"❌ ᴠɪsɪᴏɴ sᴄᴀɴɴᴇʀ ɪs ɴᴏᴡ ᴏғғ. {emo}"
        await message.reply(msg, parse_mode=ParseMode.HTML)
    else:
        msg = f"ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ! ᴜsᴇ `/nsfw on` ᴏʀ `/nsfw off` {emo}"
        await message.reply(msg, parse_mode=ParseMode.HTML)

# ─────────────────────────────
# 👁️ VISION ENGINE (MOONDREAM)
# ─────────────────────────────
async def analyze_media_fast(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        jpg_path = image_path + ".jpg"
        img.save(jpg_path, "JPEG")
        
        with open(jpg_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {
            "model": "moondream",
            "prompt": "Analyze this image. Is it safe or 18+/NSFW? Tell me what it is in EXACTLY 2 to 5 words in English. Example: 'Safe, a cute cat' or '18+ NSFW content detected'. Do not write long sentences.",
            "images": [img_b64],
            "stream": False
        }
        
        # 🔥 TIMEOUT BADHA DIYA HAI (60 Seconds)
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_VISION, json=payload, timeout=60) as resp:
                data = await resp.json()
                os.remove(jpg_path)
                return data.get("response", "error analyzing media.")
                
    except Exception as e:
        error_name = type(e).__name__
        print(f"Vision API Error: {error_name} - {str(e)}")
        # 🔥 AB KHALI ERROR NAHI, ERROR KA ASLI NAAM AAYEGA
        return f"ᴇʀʀᴏʀ: {to_small_caps(error_name)}"

# ─────────────────────────────
# 🚨 MAIN SCANNER (PHOTOS & STICKERS)
# ─────────────────────────────
@app.on_message((filters.photo | filters.sticker) & filters.group & ~BANNED_USERS)
async def nsfw_scanner(client, message: Message):
    chat_id = message.chat.id
    
    if not chat_nsfw_state.get(chat_id, True):
        return

    # Ignore Animated and Video Stickers
    if message.sticker and (message.sticker.is_animated or message.sticker.is_video):
        return

    await client.send_chat_action(chat_id, ChatAction.TYPING)
    
    dl_path = None
    try:
        dl_path = await message.download()
        
        raw_result = await analyze_media_fast(dl_path)
        
        if os.path.exists(dl_path):
            os.remove(dl_path)
            
        raw_lower = raw_result.lower()
        if "18+" in raw_lower or "nsfw" in raw_lower:
            try:
                await message.delete()
            except Exception as e:
                print(f"Delete permission error: {e}")
            
            emo = random.choice(PREMIUM_EMOJIS)
            user_mention = message.from_user.mention if message.from_user else "ᴜsᴇʀ"
            warn_msg = f"⚠️ ᴡᴀʀɴɪɴɢ {user_mention}!\nʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ ʙᴇᴄᴀᴜsᴇ ɪᴛ ᴄᴏɴᴛᴀɪɴᴇᴅ 18+/ɴsғᴡ ᴄᴏɴᴛᴇɴᴛ. {emo}"
            await client.send_message(chat_id, warn_msg, parse_mode=ParseMode.HTML)
            
        else:
            styled_result = to_small_caps(raw_result)
            emo = random.choice(PREMIUM_EMOJIS)
            final_msg = f"👁️ **sᴄᴀɴ:** {styled_result} {emo}"
            await message.reply(final_msg, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        print(f"Scanner crash: {e}")
        error_name = type(e).__name__
        if dl_path and os.path.exists(dl_path):
            os.remove(dl_path)
        await message.reply(f"❌ **sᴄᴀɴɴᴇʀ ᴄʀᴀsʜ:** {to_small_caps(error_name)}", parse_mode=ParseMode.HTML)
        
