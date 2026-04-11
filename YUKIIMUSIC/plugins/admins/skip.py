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
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

import config
from YUKIIMUSIC import YouTube, app
from YUKIIMUSIC.core.call import YUKII
from YUKIIMUSIC.misc import db
from YUKIIMUSIC.utils.database import get_loop
from YUKIIMUSIC.utils.decorators import AdminRightsCheck
from YUKIIMUSIC.utils.inline import close_markup, stream_markup
from YUKIIMUSIC.utils.stream.autoclear import auto_clean
from YUKIIMUSIC.utils.thumbnails import get_thumb
from config import BANNED_USERS


# 🔥 MAGIC BUTTON FIXER (PREMIUM EMOJI CRASH FIX) 🔥
def fix_markup(buttons):
    if not isinstance(buttons, list):
        return buttons
    fixed_buttons = []
    for row in buttons:
        fixed_row = []
        for btn in row:
            if isinstance(btn, dict):
                try:
                    fixed_row.append(InlineKeyboardButton(**btn))
                except TypeError:
                    safe_btn = {k: v for k, v in btn.items() if k in ["text", "callback_data", "url"]}
                    fixed_row.append(InlineKeyboardButton(**safe_btn))
            else:
                fixed_row.append(btn)
        fixed_buttons.append(fixed_row)
    return InlineKeyboardMarkup(fixed_buttons)


# 🔥 THE VAULT + KIDNAPPER ENGINE FOR SKIP COMMAND 🔥
async def apply_autoplay(chat_id, popped, check_list):
    from YUKIIMUSIC.utils.database import is_autoplay_on, get_lang
    if not await is_autoplay_on(chat_id): 
        return False
    if not popped or "vidid" not in popped or popped["vidid"] in ["telegram", "soundcloud"]: 
        return False

    # Downloading Message (Premium Emojis wala)
    try:
        language = await get_lang(chat_id)
        from strings import get_string
        _ = get_string(language)
        msg = await app.send_message(chat_id, _["play_1"])
    except:
        msg = None

    import random
    import os
    from pymongo import MongoClient
    import aiohttp

    vault_dir = "/home/ubuntu/Hellfire_Vault"
    next_vidid = None
    file_path = None
    title = "Autoplay Track"
    prev_vidid = popped.get("vidid", "")

    try:
        mongo_client = MongoClient(config.MONGO_DB_URI)
        music_db = mongo_client["MusicAPI_DB"]
        cache_col = music_db["songs_cache"]
    except:
        cache_col = None

    # 1. 🛡️ TRY VAULT FIRST
    if os.path.exists(vault_dir):
        files = os.listdir(vault_dir)
        valid_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.mp4', '.mkv', '.webm'))]
        if valid_files:
            random.shuffle(valid_files)
            for f in valid_files:
                vidid = f.rsplit('.', 1)[0]
                if vidid != prev_vidid:
                    next_vidid = vidid
                    file_path = os.path.join(vault_dir, f)
                    break

    if next_vidid and cache_col is not None:
        try:
            song_info = cache_col.find_one({"video_id": next_vidid})
            if song_info and "title" in song_info: 
                title = song_info["title"]
        except: 
            pass

    # 2. 🕵️ KIDNAPPER DB FALLBACK (Agar Vault khali ho)
    if not next_vidid and cache_col is not None:
        try:
            pipeline = [{"$match": {"status": "completed", "video_id": {"$ne": prev_vidid}}}, {"$sample": {"size": 1}}]
            random_song = list(cache_col.aggregate(pipeline))
            if random_song:
                song = random_song[0]
                next_vidid = song.get("video_id")
                title = song.get("title", "Kidnapped Track")
                catbox_link = song.get("catbox_link")
                
                dl_dir = "downloads"
                if not os.path.exists(dl_dir): 
                    os.makedirs(dl_dir)
                fallback_path = os.path.join(dl_dir, f"{next_vidid}_kidnap.mp3")

                if not os.path.exists(fallback_path) and catbox_link:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    async with aiohttp.ClientSession(headers=headers) as session:
                        async with session.get(catbox_link) as resp:
                            if resp.status == 200:
                                with open(fallback_path, "wb") as f: 
                                    f.write(await resp.read())
                                file_path = fallback_path
                elif os.path.exists(fallback_path):
                    file_path = fallback_path
        except: 
            pass

    # 3. 🎵 INJECT INTO QUEUE
    if next_vidid and file_path and os.path.exists(file_path):
        check_list.append({
            "vidid": next_vidid,
            "title": title,
            "by": "Autoplay [Vault]",
            "chat_id": chat_id,
            "dur": "0:00",
            "seconds": 0,
            "file": file_path,
            "streamtype": "audio",
        })
        if msg:
            try:
                await msg.delete()
            except:
                pass
        return True
        
    if msg:
        try:
            await msg.delete()
        except:
            pass
    return False


@app.on_message(
    filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_8"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                            except:
                                return await message.reply_text(_["admin_12"])
                            if popped:
                                await auto_clean(popped)
                            if not check:
                                success = await apply_autoplay(chat_id, popped, check)
                                if not success:
                                    try:
                                        await message.reply_text(
                                            text=_["admin_6"].format(
                                                message.from_user.mention,
                                                message.chat.title,
                                            ),
                                            reply_markup=close_markup(_),
                                        )
                                        await YUKII.stop_stream(chat_id)
                                    except:
                                        return
                                    break
                    else:
                        return await message.reply_text(_["admin_11"].format(count))
                else:
                    return await message.reply_text(_["admin_10"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_9"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                await auto_clean(popped)
            if not check:
                success = await apply_autoplay(chat_id, popped, check)
                if not success:
                    await message.reply_text(
                        text=_["admin_6"].format(
                            message.from_user.mention, message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    try:
                        return await YUKII.stop_stream(chat_id)
                    except:
                        return
        except:
            try:
                await message.reply_text(
                    text=_["admin_6"].format(
                        message.from_user.mention, message.chat.title
                    ),
                    reply_markup=close_markup(_),
                )
                return await YUKII.stop_stream(chat_id)
            except:
                return
                
    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    db[chat_id][0]["played"] = 0
    exis = (check[0]).get("old_dur")
    if exis:
        db[chat_id][0]["dur"] = exis
        db[chat_id][0]["seconds"] = check[0]["old_second"]
        db[chat_id][0]["speed_path"] = None
        db[chat_id][0]["speed"] = 1.0
        
    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await message.reply_text(_["admin_7"].format(title))
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await YUKII.skip_stream(chat_id, link, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])
        button = stream_markup(_, chat_id)
        img = await get_thumb(videoid)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            reply_markup=fix_markup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    elif "vid_" in queued:
        mystic = await message.reply_text(_["call_7"], disable_web_page_preview=True)
        try:
            file_path, direct = await YouTube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )
        except:
            return await mystic.edit_text(_["call_6"])
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await YUKII.skip_stream(chat_id, file_path, video=status, image=image)
        except:
            return await mystic.edit_text(_["call_6"])
        button = stream_markup(_, chat_id)
        img = await get_thumb(videoid)
        run = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            reply_markup=fix_markup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"
        await mystic.delete()
    elif "index_" in queued:
        try:
            await YUKII.skip_stream(chat_id, videoid, video=status)
        except:
            return await message.reply_text(_["call_6"])
        button = stream_markup(_, chat_id)
        run = await message.reply_photo(
            photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(user),
            reply_markup=fix_markup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"
    else:
        if videoid == "telegram":
            image = None
        elif videoid == "soundcloud":
            image = None
        else:
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
        try:
            await YUKII.skip_stream(chat_id, queued, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])
        if videoid == "telegram":
            button = stream_markup(_, chat_id)
            run = await message.reply_photo(
                photo=config.TELEGRAM_AUDIO_URL
                if str(streamtype) == "audio"
                else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_1"].format(
                    config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                ),
                reply_markup=fix_markup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif videoid == "soundcloud":
            button = stream_markup(_, chat_id)
            run = await message.reply_photo(
                photo=config.SOUNCLOUD_IMG_URL
                if str(streamtype) == "audio"
                else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_1"].format(
                    config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                ),
                reply_markup=fix_markup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        else:
            button = stream_markup(_, chat_id)
            img = await get_thumb(videoid)
            run = await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                reply_markup=fix_markup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
                                
