import os
import time
import math
import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus

import config
from YUKIIMUSIC import app
from YUKIIMUSIC.misc import mongodb

# --- DATABASE COLLECTIONS ---
game_db = mongodb["wordgame_leaderboard"]
wallet_db = mongodb["group_wallets"]

# --- SMM CONFIG ---
SMM_API_KEY = os.getenv("SMM_API_KEY", "")
SMM_API_URL = "https://fathersmm.com/api/v2"
SMM_SERVICE_ID = os.getenv("SMM_SERVICE_ID", "1") # Default 1, change from .env

TARGET_POINTS = 5000
REWARD_MEMBERS = 500

# --- AESTHETIC SMALL CAPS TEXT CONVERTER ---
def smallcaps(text):
    chars = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ', 
        'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 
        'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return ''.join(chars.get(c, c) for c in str(text))

# --- PREMIUM HACK INJECTION ---
async def inject_premium_markup(chat_id, message_id, markup):
    try:
        token = getattr(config, "BOT_TOKEN", getattr(app, "bot_token", None))
        url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
        payload = {"chat_id": chat_id, "message_id": message_id, "reply_markup": {"inline_keyboard": markup}}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        print(f"❌ Markup Injection Error: {e}")

# --- HELPER FUNCTIONS ---
async def get_wallet(chat_id):
    wallet = await wallet_db.find_one({"chat_id": chat_id})
    if not wallet:
        wallet = {"chat_id": chat_id, "points": 0, "history": []}
        await wallet_db.insert_one(wallet)
    return wallet

async def add_transaction(chat_id, log_msg):
    wallet = await get_wallet(chat_id)
    history = wallet.get("history", [])
    history.append(log_msg)
    if len(history) > 6:
        history = history[-6:]
    await wallet_db.update_one({"chat_id": chat_id}, {"$set": {"history": history}})

async def trigger_smm_reward(client, message: Message, chat_id):
    chat = await client.get_chat(chat_id)
    
    me = await chat.get_member(client.me.id)
    if me.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply(f"<emoji id='6073371665381724173'>❌</emoji> {smallcaps('Reward unlocked! But I am not an admin in this group, so I cannot add members. Make me an admin and try again!')}")
        return False

    link = f"https://t.me/{chat.username}" if chat.username else chat.invite_link
    if not link:
        link = await chat.export_invite_link()

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "key": SMM_API_KEY,
                "action": "add",
                "service": SMM_SERVICE_ID,
                "link": link,
                "quantity": REWARD_MEMBERS
            }
            async with session.post(SMM_API_URL, data=payload) as resp:
                result = await resp.json()
                if "error" in result:
                    await message.reply(f"<emoji id='6073371665381724173'>⚠️</emoji> {smallcaps('API Error:')} {result['error']}")
                    return False
    except Exception as e:
        print(f"SMM API Error: {e}")
        await message.reply(f"<emoji id='6073371665381724173'>⚠️</emoji> {smallcaps('Unable to connect to the SMM panel.')}")
        return False

    total_members = chat.members_count
    success_text = (
        f"<emoji id='6071046056555058251'>🎉</emoji> **{smallcaps('CONGRATULATIONS')} {smallcaps(chat.title)}!** <emoji id='6071046056555058251'>🎉</emoji>\n\n"
        f"<emoji id='6073117703965511893'>🏆</emoji> {smallcaps('The group has reached the')} {TARGET_POINTS} {smallcaps('points target!')}\n"
        f"<emoji id='6071252777625981483'>🚀</emoji> **{REWARD_MEMBERS} {smallcaps('New Members')}** {smallcaps('are being added to the group right now!')}\n\n"
        f"<emoji id='6073321555998282076'>📈</emoji> {smallcaps('Total Members now going up from:')} {total_members}\n\n"
        f"{smallcaps('Keep playing and growing!')} <emoji id='6073203332728491804'>🔥</emoji>"
    )
    
    markup = [[{"text": f"🤖 {smallcaps('Add Bot to Your GC')}", "url": f"https://t.me/{app.username}?startgroup=true", "style": "success", "icon_custom_emoji_id": "6073423432622544061"}]]
    
    run = await client.send_message(chat_id, success_text)
    await inject_premium_markup(chat_id, run.id, markup)
    try:
        await run.pin()
    except: pass
    
    await wallet_db.update_one({"chat_id": chat_id}, {"$inc": {"points": -TARGET_POINTS}})
    await add_transaction(chat_id, f"<emoji id='6073165416757203109'>🔄</emoji> {smallcaps('Wallet Reset after SMM Reward!')}")
    return True

# --- COMMANDS ---

@app.on_message(filters.command(["wallet", "gcwallet", "gcbal"], prefixes=["/", "."]) & filters.group)
async def check_wallet(client, message: Message):
    chat_id = message.chat.id
    wallet = await get_wallet(chat_id)
    
    text = f"<emoji id='6073552504979722691'>🏦</emoji> **{smallcaps(message.chat.title)} {smallcaps('Group Wallet')}**\n"
    text += f"<emoji id='6071348606936289251'>🆔</emoji> {smallcaps('Wallet ID:')} `{chat_id}`\n"
    text += f"<emoji id='6073321555998282076'>💰</emoji> {smallcaps('Balance:')} **{wallet['points']} / {TARGET_POINTS}** {smallcaps('points')}\n"
    text += "➖" * 12 + "\n"
    
    if not wallet["history"]:
        text += f"<emoji id='6073117703965511893'>📝</emoji> {smallcaps('No transactions yet.')}"
    else:
        text += f"<emoji id='6071252777625981483'>📜</emoji> **{smallcaps('Last 6 Transactions:')}**\n"
        for log in reversed(wallet["history"]):
            text += f"➥ {log}\n"
            
    await message.reply(text)

@app.on_message(filters.command(["donate"], prefixes=["/", "."]) & filters.group)
async def donate_points(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(smallcaps("How to use: /donate [amount] or .donate [amount]"))
    
    try: amount = int(message.command[1])
    except: return await message.reply(smallcaps("Enter the amount in numbers!"))
    
    if amount <= 0: return await message.reply(smallcaps("Enter a valid amount!"))
        
    user_id = message.from_user.id
    user_data = await game_db.find_one({"user_id": user_id})
    
    if not user_data or user_data.get("points", 0) < amount:
        return await message.reply(f"<emoji id='6073371665381724173'>❌</emoji> {smallcaps('You do not have enough points!')}")
        
    chat_id = message.chat.id
    
    # Calculate 2% fee
    fee = math.ceil(amount * 0.02)
    final_amount = amount - fee
    
    await game_db.update_one({"user_id": user_id}, {"$inc": {"points": -amount}})
    await wallet_db.update_one({"chat_id": chat_id}, {"$inc": {"points": final_amount}}, upsert=True)
    
    log_msg = f"<emoji id='6073423432622544061'>➕</emoji> {smallcaps(message.from_user.first_name)} {smallcaps('donated')} {amount} {smallcaps('pts')} ({smallcaps('-2% fee')})"
    await add_transaction(chat_id, log_msg)
    
    reply_text = (
        f"<emoji id='6071046056555058251'>💖</emoji> **{smallcaps('Thanks for donating!')}**\n"
        f"{message.from_user.mention} {smallcaps('donated')} {amount} {smallcaps('points')}.\n\n"
        f"<emoji id='6073165416757203109'>📉</emoji> {smallcaps('2% Fee:')} {fee}\n"
        f"<emoji id='6073321555998282076'>💰</emoji> {smallcaps('Added to GC:')} {final_amount}"
    )
    
    await message.reply(reply_text)
    
    new_wallet = await get_wallet(chat_id)
    if new_wallet["points"] >= TARGET_POINTS:
        await trigger_smm_reward(client, message, chat_id)

@app.on_message(filters.command(["gtransfer"], prefixes=["/", "."]) & filters.group)
async def transfer_to_other_gc(client, message: Message):
    if len(message.command) < 3:
        return await message.reply(smallcaps("How to use: /gtransfer [Target_Wallet_ID] [Amount]"))
        
    try: 
        target_chat_id = int(message.command[1])
        amount = int(message.command[2])
    except: return await message.reply(smallcaps("Incorrect format!"))
    
    if amount <= 0: return await message.reply(smallcaps("Enter a valid amount!"))
    
    user_id = message.from_user.id
    user_data = await game_db.find_one({"user_id": user_id})
    
    if not user_data or user_data.get("points", 0) < amount:
        return await message.reply(f"<emoji id='6073371665381724173'>❌</emoji> {smallcaps('You do not have enough points!')}")
        
    fee = math.ceil(amount * 0.03)
    final_amount = amount - fee
    
    await game_db.update_one({"user_id": user_id}, {"$inc": {"points": -amount}})
    await wallet_db.update_one({"chat_id": target_chat_id}, {"$inc": {"points": final_amount}}, upsert=True)
    
    sender_name = smallcaps(message.from_user.first_name)
    await add_transaction(target_chat_id, f"<emoji id='6073321555998282076'>💸</emoji> {smallcaps('Received')} {final_amount} {smallcaps('pts from')} {sender_name} ({smallcaps('3% tax cut')})")
    
    await message.reply(f"<emoji id='6073423432622544061'>✅</emoji> {smallcaps('Transfer Successful!')}\n\n<emoji id='6073321555998282076'>💸</emoji> {smallcaps('Sent:')} {amount}\n<emoji id='6073165416757203109'>📉</emoji> {smallcaps('3% Tax:')} {fee}\n<emoji id='6073117703965511893'>🎯</emoji> {smallcaps('Target GC received:')} {final_amount}")
    
    target_wallet = await get_wallet(target_chat_id)
    if target_wallet["points"] >= TARGET_POINTS:
        try: await trigger_smm_reward(client, message, target_chat_id)
        except: pass
      
