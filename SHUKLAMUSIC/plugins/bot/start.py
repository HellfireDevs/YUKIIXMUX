import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch
from pyrogram.types import CallbackQuery

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import _boot_
from SHUKLAMUSIC.plugins.sudo.sudoers import sudoers_list
from SHUKLAMUSIC.utils.database import get_served_chats, get_served_users, get_sudoers
from SHUKLAMUSIC.utils import bot_sys_stats
from SHUKLAMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from SHUKLAMUSIC.utils.decorators.language import LanguageStart
from SHUKLAMUSIC.utils.formatters import get_readable_time
from SHUKLAMUSIC.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string



YUMI_PICS = [
"https://files.catbox.moe/v0v41s.jpg",
"https://files.catbox.moe/v0v41s.jpg",
"https://files.catbox.moe/sbaei4.jpg",
"https://files.catbox.moe/csyzob.jpg",

]

PROMO =  "───────────────────────\n❖ ᴘᴧɪᴅ ᴘʀσϻσᴛɪση ᴧᴠᴧɪʟᴧʙʟє ❖\n───────────────────────\n<blockquote>❍ ᴄʜᴧᴛᴛɪηɢ ɢʀσυᴘ's\n❍ ᴄσʟσʀ ᴛʀᴧᴅɪηɢ ɢᴧϻє's\n❍ ᴄʜᴧηηєʟ's | ɢʀσυᴘ's .....\n❍ ʙєᴛᴛɪηɢ ᴧᴅs σʀ ᴧηʏᴛʜɪηɢ</blockquote>\n\n───────────────────────\nᴘʟᴧηꜱ-\n<blockquote>||● ᴅᴧɪʟʏ\n● ᴡєєᴋʟʏ\n● ϻσηᴛʜʟʏ||</blockquote>\n───────────────────────\n❍ ᴄσηᴛᴧᴄᴛ - [愛 | 𝗦𝗧么𝗟𝗞𝚵𝗥](https://t.me/hehe_stalker)\n───────────────────────"
GREET = [
    "💞", "🥂", "🔍", "🧪", "🥂", "⚡️", "🔥",
]



@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):

    loading_1 = await message.reply_text(random.choice(GREET))
    await add_served_user(message.from_user.id)
    
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴅɪηɢ ᴅᴏηɢ.❤️‍🔥</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴅɪηɢ ᴅᴏηɢ..❤️‍🔥</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴅɪηɢ ᴅᴏηɢ...❤️‍🔥</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>sᴛᴧʀᴛɪηɢ.❤️‍🔥</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>sᴛᴧʀᴛɪηɢ..❤️‍🔥</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>sᴛᴧʀᴛɪηɢ...❤️‍🔥</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ʜєʏ ʙᴧʙʏ! 💞</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴍɪᴍɪ</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴍɪᴍɪ ꭙ</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴍɪᴍɪ ꭙ ϻᴜsɪᴄ ♪</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<b>ᴍɪᴍɪ ꭙ ϻᴜsɪᴄ♪\nsᴛᴧʀᴛed❤️‍🔥!🥀</b>")
    await asyncio.sleep(0.1)
    await loading_1.delete()
    
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(YUMI_PICS),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<blockquote>✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>✦ ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n<b>✦ ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}<\blockquote>",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        await message.reply_photo(
            random.choice(YUMI_PICS),
            caption=_["start_2"].format(message.from_user.mention, app.mention, UP, DISK, CPU, RAM,served_users,served_chats),
            reply_markup=InlineKeyboardMarkup(out),
        )
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"✦ {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n✦ <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n✦ <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
            )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(YUMI_PICS),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )

@app.on_message(filters.command("promo") & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_photo(
        random.choice(YUMI_PICS),
        caption= await message.reply_text(random.choice(PROMO)).format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(message.PROMO)
    )
   


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    random.choice(YUMI_PICS),
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)
