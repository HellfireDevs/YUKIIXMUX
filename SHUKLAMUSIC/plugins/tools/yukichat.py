import os
import aiohttp
import random
import base64
from datetime import datetime
from PIL import Image
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from SHUKLAMUSIC import app
from config import BANNED_USERS

# ─────────────────────────────
# YUKI AI MEMORY & SETTINGS
# ─────────────────────────────
chat_history = {}
sticker_pack = [] # Store custom stickers here

# Get Nvidia API Key from .env
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
KIMI_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Vision ke liye tera local Ollama hi use hoga (Moondream)
OLLAMA_VISION = "http://localhost:11434/api/generate"

# Premium Peach Goma Emojis
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
# HELPER FUNCTIONS
# ─────────────────────────────
async def get_kimi_response(messages_list):
    """
    Ab ye function Kimi 2.5 (Nvidia API) se chat karega
    """
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }
        payload = {
        "model": "moonshotai/kimi-k2.5",
        "messages": messages_list,
        "max_tokens": 1024, 
        "temperature": 1.00,
        "top_p": 1.00,
        "stream": False
        }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(KIMI_API_URL, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Kimi ka reply nikalna
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"Nvidia API Error: {await resp.text()}")
                    return "Yaar mera internet thoda slow chal raha hai, Sudeep ko bolo API check kare! 😅"
    except Exception as e:
        print(f"Kimi Request Error: {e}")
        return "Oops! Kuch gadbad ho gayi yaar."

async def analyze_image_moondream(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        jpg_path = image_path + ".jpg"
        img.save(jpg_path, "JPEG")
        
        with open(jpg_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {
            "model": "moondream",
            "prompt": "Describe this image in one short, funny sentence. What is happening?",
            "images": [img_b64],
            "stream": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_VISION, json=payload) as resp:
                data = await resp.json()
                os.remove(jpg_path)
                return data["response"]
    except Exception as e:
        print(f"Vision Error: {e}")
        return "a weird looking sticker"

def get_system_prompt(user_name):
    current_time = datetime.now().strftime("%I:%M %p")
    return {
        "role": "system",
        "content": f"Your name is Yuki. You are an 18-year-old school girl living in Delhi, India. "
                   f"You are a real human girl, NOT an AI, NOT a bot. Act like a cool Delhi teenager. "
                   f"Speak naturally in Hinglish (Hindi + English). Be funny, engaging, and friendly. "
                   f"Your creator and owner is Sudeep (also known as Kaito from HellfireDevs), but ONLY mention him if someone asks who made you or who your owner is. "
                   f"Current time in Delhi is {current_time}. You are talking to a person named {user_name}. "
                   f"Keep replies short like WhatsApp messages. Don't be boring."
    }

# ─────────────────────────────
# STICKER PACK COMMAND
# ─────────────────────────────
@app.on_message(filters.command("setpack") & filters.reply & ~BANNED_USERS)
async def set_sticker_pack(client, message: Message):
    global sticker_pack
    if not message.reply_to_message.sticker:
        return await message.reply("Bhai, kisi sticker par reply karke /setpack likh!")
    
    set_name = message.reply_to_message.sticker.set_name
    if not set_name:
        return await message.reply("Ye sticker kisi pack ka nahi hai!")
    
    msg = await message.reply("Sticker pack load kar rahi hu, 1 min ruk...")
    stickers = await client.get_sticker_set(set_name)
    
    sticker_pack = [s.file_id for s in stickers.stickers]
    await msg.edit(f"Done! {len(sticker_pack)} stickers load ho gaye. Ab mai bhi cool stickers bhejungi!")

# ─────────────────────────────
# MAIN CHAT LOGIC
# ─────────────────────────────
@app.on_message((filters.text | filters.sticker) & ~BANNED_USERS & filters.group)
async def yuki_chat(client, message: Message):
    bot_id = (await client.get_me()).id
    is_mentioned = message.text and f"@{app.username}" in message.text
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_id
    
    if not (is_mentioned or is_reply_to_bot):
        return

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if user_id not in chat_history:
        chat_history[user_id] = []

    user_input = message.text if message.text else ""

    if message.sticker:
        dl_path = await message.download()
        await client.send_chat_action(message.chat.id, ChatAction.CHOOSE_STICKER)
        
        if len(chat_history[user_id]) > 2 and chat_history[user_id][-1].get("is_sticker"):
            if sticker_pack:
                await message.reply_sticker(random.choice(sticker_pack))
            else:
                await message.reply("Kitne sticker bhejega? Text mein baat kar na!")
            os.remove(dl_path)
            return

        sticker_desc = await analyze_image_moondream(dl_path)
        os.remove(dl_path)
        user_input = f"[User sent a sticker that looks like: {sticker_desc}. React to this playfully in your Delhi girl style.]"
        
        chat_history[user_id].append({"role": "user", "content": user_input, "is_sticker": True})
    else:
        user_input = user_input.replace(f"@{app.username}", "").strip()
        chat_history[user_id].append({"role": "user", "content": user_input})

    history_to_send = chat_history[user_id][-8:]
    messages_payload = [get_system_prompt(user_name)] + [{"role": msg["role"], "content": msg["content"]} for msg in history_to_send]

    # Ab Yaha par Ollama ki jagah Kimi function call ho raha hai
    yuki_reply = await get_kimi_response(messages_payload)
    
    # Save the plain text to memory so the bot doesn't get confused by its own HTML tags later
    chat_history[user_id].append({"role": "assistant", "content": yuki_reply})

    # Add random premium emojis to the end of the text
    num_emojis = random.randint(1, 2)
    chosen_emojis = "".join(random.sample(PREMIUM_EMOJIS, k=num_emojis))
    final_reply = f"{yuki_reply} {chosen_emojis}"

    if random.choice([True, False, False, False, False]):
        try:
            await message.react(emoji="❤")
        except: pass

    if sticker_pack and random.choice([True, False, False, False, False, False, False]):
        await message.reply_sticker(random.choice(sticker_pack))

    await message.reply(final_reply, parse_mode=ParseMode.HTML)
    
