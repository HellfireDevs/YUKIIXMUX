from typing import Union
import aiohttp # 🔥 ADDED FOR API INJECTION
from pyrogram import filters, types, enums # 🔥 ADDED ENUMS FOR PARSE MODE
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils import help_pannel
from SHUKLAMUSIC.utils.database import get_lang
from SHUKLAMUSIC.utils.decorators.language import LanguageStart, languageCB
from SHUKLAMUSIC.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers
from SHUKLAMUSIC.utils.stuffs.buttons import BUTTONS
from SHUKLAMUSIC.utils.stuffs.helper import Helper

# 🔥 THE BYPASS INJECTION FUNCTION (For replacing markup on existing messages)
async def inject_premium_markup(chat_id, message_id, markup):
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
        pass

# 🔥 FAST TEXT + MARKUP EDITOR (Prevents flickering during pagination)
async def edit_premium_text(chat_id, message_id, text, markup):
    try:
        url = f"https://api.telegram.org/bot{app.bot_token}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {"inline_keyboard": markup}
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        pass


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        
        # 🔥 HACK IN ACTION: Edit Text & Buttons directly via API
        await edit_premium_text(
            chat_id=chat_id,
            message_id=update.message.id,
            text=_["help_1"].format(SUPPORT_CHAT),
            markup=keyboard
        )
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        
        # 🔥 HACK IN ACTION: Pyrogram sends photo, API injects buttons
        run = await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
        )
        await inject_premium_markup(update.chat.id, run.id, keyboard)


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    # 🔥 HACK IN ACTION
    run = await message.reply_text(_["help_2"])
    await inject_premium_markup(message.chat.id, run.id, keyboard)


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)
    
    # Text mapping
    if cb == "hb1": text = helpers.HELP_1
    elif cb == "hb2": text = helpers.HELP_2
    elif cb == "hb3": text = helpers.HELP_3
    elif cb == "hb4": text = helpers.HELP_4
    elif cb == "hb5": text = helpers.HELP_5
    elif cb == "hb6": text = helpers.HELP_6
    elif cb == "hb7": text = helpers.HELP_7
    elif cb == "hb8": text = helpers.HELP_8
    elif cb == "hb9": text = helpers.HELP_9
    elif cb == "hb10": text = helpers.HELP_10
    elif cb == "hb11": text = helpers.HELP_11
    elif cb == "hb12": text = helpers.HELP_12
    elif cb == "hb13": text = helpers.HELP_13
    elif cb == "hb14": text = helpers.HELP_14
    elif cb == "hb15": text = helpers.HELP_15
    
    # 🔥 HACK IN ACTION: Smooth transition via API
    await edit_premium_text(
        chat_id=CallbackQuery.message.chat.id,
        message_id=CallbackQuery.message.id,
        text=text,
        markup=keyboard
    )


@app.on_callback_query(filters.regex("mbot_cb") & ~BANNED_USERS)
async def helper_cb_mbot(client, CallbackQuery): # 🔥 Renamed to fix duplicate function bug
    # Default Pyrogram buttons for ManageBot (Bina chhed-chhad)
    await CallbackQuery.edit_message_text(Helper.HELP_M, reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON))


@app.on_callback_query(filters.regex('managebot123'))
async def on_back_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    
    # 🔥 FIX: Language definition added taaki bot crash na ho
    language = await get_lang(CallbackQuery.message.chat.id)
    _ = get_string(language)
    keyboard = help_pannel(_, True)
    
    if cb == "settings_back_helper":
        # 🔥 HACK IN ACTION
        await edit_premium_text(
            chat_id=CallbackQuery.message.chat.id,
            message_id=CallbackQuery.message.id,
            text=_["help_1"].format(SUPPORT_CHAT),
            markup=keyboard
        )

@app.on_callback_query(filters.regex('mplus'))      
async def mb_plugin_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"mbot_cb")]])
    if cb == "Okieeeeee":
        await CallbackQuery.edit_message_text(f"`something errors`", reply_markup=keyboard, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await CallbackQuery.edit_message_text(getattr(Helper, cb), reply_markup=keyboard)
    
