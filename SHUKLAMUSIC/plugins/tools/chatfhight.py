import time
import asyncio
import os
import random
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import mongodb

# 🔥 MONGODB COLLECTION FOR LEADERBOARD 🔥
game_db = mongodb["wordgame_leaderboard"]

# --- GLOBAL TRACKERS ---
last_message_time = {}
active_games = {}
INACTIVITY_LIMIT = 300  # 5 minutes in seconds

# --- FILE PATHS ---
TEMPLATE_PATH = "SHUKLAMUSIC/assets/template.jpg"
FONT_PATH = "SHUKLAMUSIC/assets/arial.ttf"

# --- 1. GROQ API WORD GENERATOR ---
async def get_random_word():
    # Fallback words in case API fails
    fallback_words = ["BACTERIAL", "GAMUT", "PANDEMIC", "AESTHETIC", "RESONATE", "ILLUSION", "HELLFIRE", "DEVELOPER"]
    
    # Check if GROQ API key is added in config, otherwise use fallback
    if not hasattr(config, "GROQ_API_KEY") or not config.GROQ_API_KEY:
        return random.choice(fallback_words)
        
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": "Reply with only ONE random difficult English word. Do not add punctuation or explanation. Just the word."}],
            "temperature": 0.9
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                word = data['choices'][0]['message']['content'].strip().upper()
                word = ''.join(e for e in word if e.isalnum()) # Clean special chars
                return word if word else random.choice(fallback_words)
    except Exception as e:
        return random.choice(fallback_words)

# --- 2. IMAGE GENERATOR ---
def create_game_image(word):
    output_path = f"game_{word}.jpg"
    
    # Check if template exists, if not create a dummy dark background
    if not os.path.exists(TEMPLATE_PATH):
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(TEMPLATE_PATH), exist_ok=True)
        img = Image.new('RGB', (800, 400), color=(15, 15, 15))
        img.save(TEMPLATE_PATH)

    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(FONT_PATH, 65) # Arial Bold font
    except:
        font = ImageFont.load_default()
    
    # Center text alignment
    bbox = draw.textbbox((0, 0), word, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    W, H = img.size
    x = (W - text_w) / 2
    y = ((H - text_h) / 2) - 10
    
    draw.text((x, y), word, fill="white", font=font)
    img.save(output_path)
    return output_path

# --- CORE GAME TRIGGER FUNCTION ---
async def start_word_game(chat_id):
    try:
        # Generate Word & Image
        word = await get_random_word()
        img_path = create_game_image(word)
        
        caption = (
            "⚡ Be the first to write the word shown in the photo to climb the mini-game leaderboard.\n\n"
            "⏱ **Time remaining:** 10 minutes"
        )
        
        # Send Game with SPOILER EFFECT
        sent_msg = await app.send_photo(
            chat_id, 
            photo=img_path, 
            caption=caption,
            has_spoiler=True  # 🔥 Spoiler effect added here!
        )
        
        # Clean up local storage
        if os.path.exists(img_path):
            os.remove(img_path) 
        
        # Store active game info
        active_games[chat_id] = {
            "word": word,
            "start_time": time.time(),
            "message_id": sent_msg.id
        }
        
        # Reset timer so it doesn't loop spam
        last_message_time[chat_id] = time.time()
    except Exception as e:
        print(f"Failed to start game in {chat_id}: {e}")


# --- 3. COMMAND: TEST GAME INSTANTLY ---
@app.on_message(filters.command("testgame") & filters.group)
async def test_game_cmd(client, message: Message):
    # Sirf admins use kar payenge testgame (optional safety)
    if message.from_user:
        await start_word_game(message.chat.id)


# --- 4. TRACKER & ANSWER CHECKER ---
# Group 10 ensures it runs in background and doesn't block your normal music commands
@app.on_message(filters.group & ~filters.bot, group=10)
async def chat_activity_tracker(client, message: Message):
    chat_id = message.chat.id
    
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    
    # 1. Update last message time for this group
    last_message_time[chat_id] = time.time()
    
    # 2. Check if there is an active game and someone answered
    if chat_id in active_games and message.text:
        correct_word = active_games[chat_id]["word"]
        
        if message.text.strip().upper() == correct_word:
            time_taken = round(time.time() - active_games[chat_id]["start_time"], 1)
            del active_games[chat_id] # End the game immediately so others can't claim it
            
            # 🔥 Send Reaction to the Correct Answer 🔥
            try:
                await client.send_reaction(chat_id=chat_id, message_id=message.id, emoji="❤️")
            except Exception:
                pass # Ignore if bot doesn't have reaction rights in the group
                
            # Update Points in MongoDB
            user_data = await game_db.find_one({"user_id": user_id})
            if user_data:
                new_points = user_data["points"] + 15
                await game_db.update_one({"user_id": user_id}, {"$set": {"points": new_points, "name": message.from_user.first_name}})
            else:
                await game_db.insert_one({"user_id": user_id, "name": message.from_user.first_name, "points": 15})
            
            # Send Success Message
            msg = (
                f"⚡ **How fast!** ({time_taken} seconds)\n"
                f"🎉 {message.from_user.mention} guessed the word in record time!\n"
                f"Correct Word: **{correct_word}**\n"
                f"*+15 in the global game ranking*"
            )
            await message.reply_text(msg)


# --- 5. LEADERBOARD COMMAND ---
@app.on_message(filters.command(["wordleaderboard", "gametop"]) & filters.group)
async def word_leaderboard(client, message: Message):
    top_users = game_db.find().sort("points", -1).limit(10)
    text = "🏆 **Word Game Global Leaderboard** 🏆\n\n"
    count = 1
    
    has_users = False
    async for user in top_users:
        has_users = True
        name = user.get('name', 'Unknown User')
        text += f"**{count}.** {name} - `{user['points']}` points\n"
        count += 1
    
    if not has_users:
        text += "No one has scored points yet! Wait for a game to start."
        
    await message.reply_text(text)


# --- 6. THE BACKGROUND GAME LOOP (Trigger on Inactivity) ---
async def inactivity_checker_loop():
    while True:
        await asyncio.sleep(60) # Checks every 1 minute
        current_time = time.time()
        
        for chat_id, last_time in list(last_message_time.items()):
            # Trigger if 5 mins passed and no active game is running in that chat
            if (current_time - last_time) > INACTIVITY_LIMIT and chat_id not in active_games:
                try:
                    # Send Warning first
                    warning = await app.send_message(chat_id, "⏱ Time passes. Tick tock, tick tock...")
                    await asyncio.sleep(3)
                    await warning.delete()
                    
                    # Start Game
                    await start_word_game(chat_id)
                except Exception as e:
                    pass

# Start the background loop when the plugin loads
asyncio.create_task(inactivity_checker_loop())
