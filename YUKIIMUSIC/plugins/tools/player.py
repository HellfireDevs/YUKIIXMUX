# Copyright (c) 2025 @SUDEEPBOTS <HellfireDevs>
# Location: delhi,noida
#
# All rights reserved.
#
# This code is the intellectual SUDEEPBOTS.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: sudeepgithub@gmail.com

import YUKIIMUSIC.yuki_guard
import os
from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message

import config
from YUKIIMUSIC import app
from YUKIIMUSIC.misc import SUDOERS, mongodb
from YUKIIMUSIC.utils.decorators.language import language, languageCB
from config import BANNED_USERS

# 🔥 AUTOPLAY DATABASE IMPORTS
from YUKIIMUSIC.utils.database import autoplay_on, autoplay_off, is_autoplay_on

# 🔥 PLAYER DATABASE SETUP
playerdb = mongodb.player_settings

# --- PLAYER STYLE DB ---
async def get_player_style(chat_id):
    user = await playerdb.find_one({"chat_id": chat_id})
    if user and "style" in user:
        return user["style"]
    if chat_id != "GLOBAL":
        global_user = await playerdb.find_one({"chat_id": "GLOBAL"})
        if global_user and "style" in global_user:
            return global_user["style"]
    return 1

async def set_player_style(chat_id, style: int):
    await playerdb.update_one({"chat_id": chat_id}, {"$set": {"style": style}}, upsert=True)

# --- PLAYER ON/OFF DB ---
async def is_player_on(chat_id):
    user = await playerdb.find_one({"chat_id": chat_id})
    if user and "is_on" in user:
        return user["is_on"]
    if chat_id != "GLOBAL":
        global_user = await playerdb.find_one({"chat_id": "GLOBAL"})
        if global_user and "is_on" in global_user:
            return global_user["is_on"]
    return True

async def set_player_on(chat_id, is_on: bool):
    await playerdb.update_one({"chat_id": chat_id}, {"$set": {"is_on": is_on}}, upsert=True)

# --- MUSIC ON/OFF DB (NEW) ---
async def is_music_on(chat_id):
    user = await playerdb.find_one({"chat_id": chat_id})
    if user and "music_on" in user:
        return user["music_on"]
    if chat_id != "GLOBAL":
        global_user = await playerdb.find_one({"chat_id": "GLOBAL"})
        if global_user and "music_on" in global_user:
            return global_user["music_on"]
    return True

async def set_music_on(chat_id, is_on: bool):
    await playerdb.update_one({"chat_id": chat_id}, {"$set": {"music_on": is_on}}, upsert=True)


# 🔥 KEYBOARD GENERATOR (UPDATED WITH AUTOPLAY TOGGLE)
def player_markup(style: int, is_on: bool, is_music: bool, is_autoplay: bool, target_id):
    status = "✅ ᴏɴ" if is_on else "❌ ᴏғғ"
    music_status = "✅ ᴏɴ" if is_music else "❌ ᴏғғ"
    autoplay_status = "✅ ᴏɴ" if is_autoplay else "❌ ᴏғғ"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"{'🔘' if style == 1 else ''} ᴅᴇsɪɢɴ 1", callback_data=f"set_player_1_{target_id}"),
                InlineKeyboardButton(f"{'🔘' if style == 2 else ''} ᴅᴇsɪɢɴ 2", callback_data=f"set_player_2_{target_id}"),
            ],
            [
                InlineKeyboardButton(f"{'🔘' if style == 3 else ''} ᴅᴇsɪɢɴ 3", callback_data=f"set_player_3_{target_id}"),
                InlineKeyboardButton(f"{'🔘' if style == 4 else ''} ᴅᴇsɪɢɴ 4", callback_data=f"set_player_4_{target_id}"),
            ],
            [
                InlineKeyboardButton(f"ᴘʟᴀʏᴇʀ sᴛᴀᴛᴜs : {status}", callback_data=f"toggle_player_{target_id}"),
            ],
            [
                InlineKeyboardButton(f"ᴍᴜsɪᴄ sᴛᴀᴛᴜs : {music_status}", callback_data=f"toggle_music_{target_id}"),
            ],
            [
                InlineKeyboardButton(f"ᴀᴜᴛᴏᴘʟᴀʏ sᴛᴀᴛᴜs : {autoplay_status}", callback_data=f"toggle_autoplay_{target_id}"),
            ],
            [
                InlineKeyboardButton("🗑 ᴄʟᴏsᴇ", callback_data="close_player_panel"),
            ]
        ]
    )

def get_digan_image(style: int):
    if style == 1:
        return getattr(config, "DIGAN_1", config.STATS_IMG_URL)
    elif style == 2:
        return getattr(config, "DIGAN_2", config.STATS_IMG_URL)
    elif style == 3:
        return getattr(config, "DIGAN_3", config.STATS_IMG_URL)
    elif style == 4:
        return getattr(config, "DIGAN_4", config.STATS_IMG_URL)
    return config.STATS_IMG_URL


# 🔥 MUSIC ENABLE/DISABLE COMMAND HANDLER (NEW)
@app.on_message(filters.command(["music", "song"], prefixes=["/", ".", "!"]) & ~BANNED_USERS)
async def music_on_off_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ <b>ᴜsᴀɢᴇ:</b> `/music on` ᴏʀ `/music off`")
    
    state = message.command[1].lower()
    if state not in ["on", "off", "enable", "disable"]:
        return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ sᴛᴀᴛᴇ. ᴜsᴇ `on` ᴏʀ `off`.</b>")

    if message.sender_chat:
        return await message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴅɪsᴀʙʟᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ ғɪʀsᴛ!")

    if message.chat.type == ChatType.PRIVATE:
        if message.from_user.id in SUDOERS:
            target_id = "GLOBAL"
        else:
            return await message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs!")
    else:
        if message.from_user.id not in SUDOERS:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀs!")
        target_id = message.chat.id

    is_turning_on = state in ["on", "enable"]
    await set_music_on(target_id, is_turning_on)
    
    status_text = "ᴇɴᴀʙʟᴇᴅ ✅" if is_turning_on else "ᴅɪsᴀʙʟᴇᴅ ❌"
    panel_type = "ɢʟᴏʙᴀʟ" if target_id == "GLOBAL" else "ɢʀᴏᴜᴘ"
    
    await message.reply_text(
        f"<blockquote><b>✨ {panel_type} ᴍᴜsɪᴄ sᴛᴀᴛᴜs ✨</b>\n\n"
        f"ᴍᴜsɪᴄ ᴘʟᴀʏ sʏsᴛᴇᴍ ʜᴀs ʙᴇᴇɴ <b>{status_text}</b> ғᴏʀ ᴛʜɪs {panel_type.lower()}!</blockquote>"
    )


# 🔥 PLAYER COMMAND HANDLER
@app.on_message(filters.command(["player", "gcplayer", "songplayer", "globalplayer"]) & ~BANNED_USERS)
@language
async def player_command(client, message: Message, _):
    # Anonymous Admin Check for the command
    if message.sender_chat:
        return await message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴅɪsᴀʙʟᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ ғɪʀsᴛ!")

    # DM Check & Global Logic
    if message.chat.type == ChatType.PRIVATE:
        if message.from_user.id in SUDOERS:
            target_id = "GLOBAL"
        else:
            return await message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs!")
    else:
        # Group Admin Check
        if message.from_user.id not in SUDOERS:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀs!")
        target_id = message.chat.id

    style = await get_player_style(target_id)
    is_on = await is_player_on(target_id)
    is_music = await is_music_on(target_id)
    is_autoplay = await is_autoplay_on(target_id)
    img = get_digan_image(style)
    
    panel_type = "ɢʟᴏʙᴀʟ" if target_id == "GLOBAL" else "ɢʀᴏᴜᴘ"
    
    # 🔥 UPDATED CAPTION WITH BLOCKQUOTE
    caption = (
        f"<blockquote><b>✨ {panel_type} ᴘʟᴀʏᴇʀ sᴇᴛᴛɪɴɢs ✨</b>\n\n"
        "ғʀᴏᴍ ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜᴇ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴅᴇsɪɢɴ. "
        "sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ᴅᴇsɪɢɴ ғʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ!</blockquote>\n\n"
        f"<blockquote><b>🔘 ᴄᴜʀʀᴇɴᴛ sᴛʏʟᴇ:</b> ᴅᴇsɪɢɴ {style}</blockquote>"
    )

    await message.reply_photo(
        photo=img,
        caption=caption,
        reply_markup=player_markup(style, is_on, is_music, is_autoplay, target_id)
    )


# 🔥 CALLBACK HANDLERS (SETTINGS PANEL)
@app.on_callback_query(filters.regex(r"^(set_player_|toggle_player_|toggle_music_|toggle_autoplay_)") & ~BANNED_USERS)
async def player_callbacks(client, CallbackQuery: CallbackQuery):
    data = CallbackQuery.data.split("_")
    action = data[0]
    
    # Target ID extraction
    if action == "set":
        new_style = int(data[2])
        target_id = data[3]
    else: # toggle
        sub_action = data[1] # 'player', 'music' or 'autoplay'
        target_id = data[2]

    if target_id != "GLOBAL":
        target_id = int(target_id)

    # Security Checks
    if target_id == "GLOBAL":
        if CallbackQuery.from_user.id not in SUDOERS:
            return await CallbackQuery.answer("❌ ᴏɴʟʏ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴄʜᴀɴɢᴇ ɢʟᴏʙᴀʟ sᴇᴛᴛɪɴɢs!", show_alert=True)
    else:
        if CallbackQuery.from_user.id not in SUDOERS:
            member = await client.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await CallbackQuery.answer("❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜᴇsᴇ sᴇᴛᴛɪɴɢs!", show_alert=True)

    # Execute Actions
    current_style = await get_player_style(target_id)
    is_on = await is_player_on(target_id)
    is_music = await is_music_on(target_id)
    is_autoplay = await is_autoplay_on(target_id)
    panel_type = "ɢʟᴏʙᴀʟ" if target_id == "GLOBAL" else "ɢʀᴏᴜᴘ"

    if action == "set":
        if new_style == current_style:
            return await CallbackQuery.answer(f"ᴅᴇsɪɢɴ {new_style} ɪs ᴀʟʀᴇᴀᴅʏ sᴇᴛ!", show_alert=True)
        
        await set_player_style(target_id, new_style)
        await CallbackQuery.answer(f"✅ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴛᴏ ᴅᴇsɪɢɴ {new_style}!")
        
        img = get_digan_image(new_style)
        
        caption = (
            f"<blockquote><b>✨ {panel_type} ᴘʟᴀʏᴇʀ sᴇᴛᴛɪɴɢs ✨</b>\n\n"
            "ғʀᴏᴍ ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜᴇ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ᴅᴇsɪɢɴ. "
            "sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ᴅᴇsɪɢɴ ғʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ!</blockquote>\n\n"
            f"<blockquote><b>🔘 ᴄᴜʀʀᴇɴᴛ sᴛʏʟᴇ:</b> ᴅᴇsɪɢɴ {new_style}</blockquote>"
        )
        
        med = InputMediaPhoto(media=img, caption=caption)
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=player_markup(new_style, is_on, is_music, is_autoplay, target_id))
        except MessageIdInvalid:
            pass

    elif action == "toggle":
        if sub_action == "player":
            new_status = not is_on
            await set_player_on(target_id, new_status)
            status_text = "ᴏɴ ✅" if new_status else "ᴏғғ ❌"
            await CallbackQuery.answer(f"✅ {panel_type} ᴘʟᴀʏᴇʀ sᴛᴀᴛᴜs ɪs ɴᴏᴡ {status_text}!")
            try:
                await CallbackQuery.edit_message_reply_markup(reply_markup=player_markup(current_style, new_status, is_music, is_autoplay, target_id))
            except MessageIdInvalid:
                pass
                
        elif sub_action == "music":
            new_music_status = not is_music
            await set_music_on(target_id, new_music_status)
            status_text = "ᴏɴ ✅" if new_music_status else "ᴏғғ ❌"
            await CallbackQuery.answer(f"✅ {panel_type} ᴍᴜsɪᴄ sᴛᴀᴛᴜs ɪs ɴᴏᴡ {status_text}!")
            try:
                await CallbackQuery.edit_message_reply_markup(reply_markup=player_markup(current_style, is_on, new_music_status, is_autoplay, target_id))
            except MessageIdInvalid:
                pass
                
        elif sub_action == "autoplay":
            new_autoplay_status = not is_autoplay
            if new_autoplay_status:
                await autoplay_on(target_id)
            else:
                await autoplay_off(target_id)
            
            status_text = "ᴏɴ ✅" if new_autoplay_status else "ᴏғғ ❌"
            await CallbackQuery.answer(f"✅ {panel_type} ᴀᴜᴛᴏᴘʟᴀʏ sᴛᴀᴛᴜs ɪs ɴᴏᴡ {status_text}!")
            try:
                await CallbackQuery.edit_message_reply_markup(reply_markup=player_markup(current_style, is_on, is_music, new_autoplay_status, target_id))
            except MessageIdInvalid:
                pass

@app.on_callback_query(filters.regex("close_player_panel") & ~BANNED_USERS)
async def close_player_cb(client, CallbackQuery: CallbackQuery):
    if CallbackQuery.message.chat.type != ChatType.PRIVATE and CallbackQuery.from_user.id not in SUDOERS:
        member = await client.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await CallbackQuery.answer("❌ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴄʟᴏsᴇ ᴛʜɪs!", show_alert=True)

    try:
        await CallbackQuery.message.delete()
    except:
        pass


# 🔥 CALLBACK HANDLER (INLINE MUSIC PLAYER AUTOPLAY BUTTON)
@app.on_callback_query(filters.regex(r"^Player_Autoplay_") & ~BANNED_USERS)
async def music_player_autoplay_cb(client, CallbackQuery: CallbackQuery):
    chat_id = int(CallbackQuery.data.split("_")[2])
    
    # Admin Check
    if CallbackQuery.from_user.id not in SUDOERS:
        member = await client.get_chat_member(chat_id, CallbackQuery.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await CallbackQuery.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)

    is_autoplay = await is_autoplay_on(chat_id)
    
    # Toggle Logic with Popup Alert
    if is_autoplay:
        await autoplay_off(chat_id)
        await CallbackQuery.answer("❌ ᴀᴜᴛᴏᴘʟᴀʏ ᴅɪsᴀʙʟᴇᴅ!", show_alert=True)
    else:
        await autoplay_on(chat_id)
        await CallbackQuery.answer("✅ ᴀᴜᴛᴏᴘʟᴀʏ ᴇɴᴀʙʟᴇᴅ!", show_alert=True)
                                 
