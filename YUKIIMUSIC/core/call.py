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
import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

import config
from YUKIIMUSIC import LOGGER, YouTube, app
from YUKIIMUSIC.misc import db, mongodb
from YUKIIMUSIC.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from YUKIIMUSIC.utils.exceptions import AssistantErr
from YUKIIMUSIC.utils.formatters import check_duration, seconds_to_min, speed_converter
from YUKIIMUSIC.utils.inline.play import stream_markup_timer, music_end_markup
from YUKIIMUSIC.utils.stream.autoclear import auto_clean
from YUKIIMUSIC.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}

# 🔥 LINK PREVIEW OPTIONS (Theme 2 ke liye)
try:
    from pyrogram.types import LinkPreviewOptions
    HAS_PREVIEW_OPTIONS = True
except ImportError:
    HAS_PREVIEW_OPTIONS = False

# 🔥 THEME ENGINE SETUP
playerdb = mongodb.player_settings

async def get_player_style(chat_id):
    user = await playerdb.find_one({"chat_id": chat_id})
    if user and "style" in user:
        return user["style"]
    if chat_id != "GLOBAL":
        global_user = await playerdb.find_one({"chat_id": "GLOBAL"})
        if global_user and "style" in global_user:
            return global_user["style"]
    return 1


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

# 🔥 ORIGINAL PREMIUM EMOJI & TIMER HACK 🔥
async def inject_premium_markup(chat_id, message_id, markup):
    import aiohttp
    try:
        url = f"https://api.telegram.org/bot{app.bot_token}/editMessageReplyMarkup"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": markup}
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        print(f"❌ Markup Injection Error: {e}")

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="YUKIIAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        self.userbot2 = Client(
            name="YUKIIAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        self.userbot3 = Client(
            name="YUKIIAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        self.userbot4 = Client(
            name="YUKIIAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        self.userbot5 = Client(
            name="YUKIIAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        for ass in [self.one, self.two, self.three, self.four, self.five]:
            try:
                await ass.leave_group_call(chat_id)
            except:
                pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                vs = 1.0
                if str(speed) == "0.5": vs = 2.0
                elif str(speed) == "0.75": vs = 1.35
                elif str(speed) == "1.5": vs = 0.68
                elif str(speed) == "2.0": vs = 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=(f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} {out}"),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = (
            AudioVideoPiped(out, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(), additional_ffmpeg_parameters=f"-ss {played} -to {duration}")
            if playing[0]["streamtype"] == "video"
            else AudioPiped(out, audio_parameters=HighQualityAudio(), additional_ffmpeg_parameters=f"-ss {played} -to {duration}")
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.change_stream(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            db.get(chat_id).pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
        else:
            stream = AudioPiped(link, audio_parameters=HighQualityAudio())
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (
            AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
            if mode == "video"
            else AudioPiped(file_path, audio_parameters=HighQualityAudio(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
        )
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.join_group_call(config.LOGGER_ID, AudioVideoPiped(link), stream_type=StreamType().pulse_stream)
        await asyncio.sleep(0.2)
        await assistant.leave_group_call(config.LOGGER_ID)

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if video:
            stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
        else:
            stream = AudioPiped(link, audio_parameters=HighQualityAudio())
        try:
            await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            
            # 🔥 VAULT & KIDNAPPER AUTOPLAY ENGINE W/ SMART FETCH 🔥
            if not check:
                try:
                    from YUKIIMUSIC.utils.database import is_autoplay_on
                    auto_play = await is_autoplay_on(chat_id)
                    
                    if auto_play and popped and "vidid" in popped and popped["vidid"] not in ["telegram", "soundcloud"]:
                        import random
                        import os
                        from pymongo import MongoClient
                        import config
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
                            except Exception as db_e:
                                pass

                        if next_vidid and file_path and os.path.exists(file_path):
                            # 🔥 YOUTUBE SMART FETCH ENGINE 🔥
                            dur_min = "0:00"
                            dur_sec = 0
                            try:
                                from YUKIIMUSIC import YouTube
                                track_details, _ = await YouTube.track(next_vidid, videoid=True)
                                if track_details:
                                    title = track_details.get("title", title)
                                    dur_min = track_details.get("duration_min", "0:00")
                                    dur_sec = track_details.get("duration_sec", 0)
                            except Exception:
                                # Fallback to DB title if Youtube fails
                                if cache_col:
                                    try:
                                        song_info = cache_col.find_one({"video_id": next_vidid})
                                        if song_info and "title" in song_info: title = song_info["title"]
                                    except: pass

                            check.append({
                                "vidid": next_vidid,
                                "title": title,
                                "by": "Autoplay [Vault]",
                                "chat_id": chat_id,
                                "dur": dur_min,
                                "seconds": dur_sec,
                                "file": file_path, 
                                "streamtype": "audio",
                            })
                except Exception as e:
                    pass

            if not check:
                try:
                    if popped and "mystic" in popped:
                        language = await get_lang(chat_id)
                        from strings import get_string
                        _ = get_string(language)
                        end_msg = _["MUSIC_ENDED"]
                        from YUKIIMUSIC.utils.inline.play import music_end_markup
                        try:
                            await popped["mystic"].edit_caption(caption=end_msg, reply_markup=music_end_markup(_))
                        except:
                            await popped["mystic"].edit_text(text=end_msg, disable_web_page_preview=True, reply_markup=music_end_markup(_))
                except Exception:
                    pass
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
        except:
            try:
                if popped and "mystic" in popped:
                    language = await get_lang(chat_id)
                    from strings import get_string
                    _ = get_string(language)
                    end_msg = _["MUSIC_ENDED"]
                    from YUKIIMUSIC.utils.inline.play import music_end_markup
                    try:
                        await popped["mystic"].edit_caption(caption=end_msg, reply_markup=music_end_markup(_))
                    except:
                        await popped["mystic"].edit_text(text=end_msg, disable_web_page_preview=True, reply_markup=music_end_markup(_))
            except Exception:
                pass
            try:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
            except:
                return
        else:
            queued = check[0]["file"]
            language = await get_lang(chat_id)
            from strings import get_string
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            videoid = check[0]["vidid"]
            duration_min = check[0].get("dur", "0:00")
            db[chat_id][0]["played"] = 0
            exis = (check[0]).get("old_dur")
            if exis:
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = True if str(streamtype) == "video" else False
            
            # 🔥 THEMED VIP PLAYER SYNC LOGIC 🔥
            theme = await get_player_style(chat_id)
            button = stream_markup_timer(_, chat_id, "00:00", duration_min)
            video_file = getattr(config, "PLAYER_VIDEO", "https://files.catbox.moe/qxj5y2.mp4")
            
            try:
                caption_text = _[f"stream_{theme}"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], duration_min, user, video_file)
            except KeyError:
                caption_text = _["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], duration_min, user)

            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                if video:
                    stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
                else:
                    stream = AudioPiped(link, audio_parameters=HighQualityAudio())
                try:
                    await client.change_stream(chat_id, stream)
                except Exception:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                img = await get_thumb(videoid)
                
                if theme == 2:
                    if HAS_PREVIEW_OPTIONS:
                        run = await app.send_message(original_chat_id, text=caption_text, link_preview_options=LinkPreviewOptions(url=video_file, show_above_text=True))
                    else:
                        run = await app.send_message(original_chat_id, text=caption_text, disable_web_page_preview=False)
                else:
                    run = await app.send_photo(original_chat_id, photo=img, caption=caption_text)
                    
                await inject_premium_markup(original_chat_id, run.id, button)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
                
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                try:
                    file_path, direct = await YouTube.download(videoid, mystic, videoid=True, video=True if str(streamtype) == "video" else False)
                except:
                    return await mystic.edit_text(_["call_6"], disable_web_page_preview=True)
                if video:
                    stream = AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
                else:
                    stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                img = await get_thumb(videoid)
                await mystic.delete()
                
                if theme == 2:
                    if HAS_PREVIEW_OPTIONS:
                        run = await app.send_message(original_chat_id, text=caption_text, link_preview_options=LinkPreviewOptions(url=video_file, show_above_text=True))
                    else:
                        run = await app.send_message(original_chat_id, text=caption_text, disable_web_page_preview=False)
                else:
                    run = await app.send_photo(original_chat_id, photo=img, caption=caption_text)
                    
                await inject_premium_markup(original_chat_id, run.id, button)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
                
            elif "index_" in queued:
                stream = AudioVideoPiped(videoid, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if str(streamtype) == "video" else AudioPiped(videoid, audio_parameters=HighQualityAudio())
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                if theme == 2:
                    if HAS_PREVIEW_OPTIONS:
                        run = await app.send_message(original_chat_id, text=caption_text, link_preview_options=LinkPreviewOptions(url=video_file, show_above_text=True))
                    else:
                        run = await app.send_message(original_chat_id, text=caption_text, disable_web_page_preview=False)
                else:
                    run = await app.send_photo(original_chat_id, photo=config.STREAM_IMG_URL, caption=caption_text)
                    
                await inject_premium_markup(original_chat_id, run.id, button)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
                
            else:
                if video:
                    stream = AudioVideoPiped(queued, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
                else:
                    stream = AudioPiped(queued, audio_parameters=HighQualityAudio())
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                if videoid == "telegram":
                    if theme == 2:
                        run = await app.send_message(original_chat_id, text=caption_text, link_preview_options=LinkPreviewOptions(url=video_file, show_above_text=True) if HAS_PREVIEW_OPTIONS else None)
                    else:
                        run = await app.send_photo(original_chat_id, photo=config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL, caption=caption_text)
                    await inject_premium_markup(original_chat_id, run.id, button)
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    if theme == 2:
                        run = await app.send_message(original_chat_id, text=caption_text, link_preview_options=LinkPreviewOptions(url=video_file, show_above_text=True) if HAS_PREVIEW_OPTIONS else None)
                    else:
                        run = await app.send_photo(original_chat_id, photo=config.SOUNCLOUD_IMG_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL, caption=caption_text)
                    await inject_premium_markup(original_chat_id, run.id, button)
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    if theme == 2:
                        run = await app.send_message(original_chat_id, text=caption_text, link_preview_options=LinkPreviewOptions(url=video_file, show_above_text=True) if HAS_PREVIEW_OPTIONS else None)
                    else:
                        run = await app.send_photo(original_chat_id, photo=img, caption=caption_text)
                    await inject_premium_markup(original_chat_id, run.id, button)
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(await self.one.ping)
        if config.STRING2:
            pings.append(await self.two.ping)
        if config.STRING3:
            pings.append(await self.three.ping)
        if config.STRING4:
            pings.append(await self.four.ping)
        if config.STRING5:
            pings.append(await self.five.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.two.on_kicked()
        @self.three.on_kicked()
        @self.four.on_kicked()
        @self.five.on_kicked()
        @self.one.on_closed_voice_chat()
        @self.two.on_closed_voice_chat()
        @self.three.on_closed_voice_chat()
        @self.four.on_closed_voice_chat()
        @self.five.on_closed_voice_chat()
        @self.one.on_left()
        @self.two.on_left()
        @self.three.on_left()
        @self.four.on_left()
        @self.five.on_left()
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()
        async def stream_end_handler1(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            await self.change_stream(client, update.chat_id)

YUKII = Call()
