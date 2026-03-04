from typing import Union
import aiohttp # 🔥 ADDED FOR API INJECTION
import config
from pyrogram import filters, types, enums # 🔥 ADDED ENUMS TO FIX YOUR ERROR
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
        token = getattr(config, "BOT_TOKEN", getattr(app, "bot_token", None))
        url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": markup}
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        pass

# 🔥 FAST TEXT + MARKUP EDITOR (API SE)
async def edit_premium_text(chat_id, message_id, text, markup):
    try:
        token = getattr(config, "BOT_TOKEN", getattr(app, "bot_token", None))
        url = f"https://api.telegram.org/bot{token}/editMessageText"
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
        # 🔥 HACK IN ACTION: API Edit
        await edit_premium_text(chat_id, update.message.id, _["help_1"].format(SUPPORT_CHAT), keyboard)
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        # 🔥 HACK IN ACTION: Injection
        run = await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
        )
        await inject_premium_markup(update.chat.id, run.id, keyboard)


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    # 🔥 HACK IN ACTION: Group Help Injection
    run = await message.reply_text(_["help_2"])
    await inject_premium_markup(message.chat.id, run.id, keyboard)


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)
    chat_id = CallbackQuery.message.chat.id
    msg_id = CallbackQuery.message.id
    
    # 🔥 TERA EXACT LOGIC BINA CUT KIYE API SE CHALAYA HAI
    if cb == "hb1":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_1, keyboard)
    elif cb == "hb2":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_2, keyboard)
    elif cb == "hb3":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_3, keyboard)
    elif cb == "hb4":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_4, keyboard)
    elif cb == "hb5":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_5, keyboard)
    elif cb == "hb6":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_6, keyboard)
    elif cb == "hb7":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_7, keyboard)
    elif cb == "hb8":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_8, keyboard)
    elif cb == "hb9":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_9, keyboard)
    elif cb == "hb10":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_10, keyboard)
    elif cb == "hb11":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_11, keyboard)
    elif cb == "hb12":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_12, keyboard)
    elif cb == "hb13":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_13, keyboard)
    elif cb == "hb14":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_14, keyboard)
    elif cb == "hb15":
        await edit_premium_text(chat_id, msg_id, helpers.HELP_15, keyboard)
        
        
@app.on_callback_query(filters.regex("mbot_cb") & ~BANNED_USERS)
async def helper_cb(client, CallbackQuery): # TERA NAMING SAME RAKHA HAI
    # ⚠️ NO HACK HERE: Ye Pyrogram ka asli markup use kar raha hai
    await CallbackQuery.edit_message_text(Helper.HELP_M, reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON))


@app.on_callback_query(filters.regex('managebot123'))
async def on_back_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    
    # 🔥 TERA ERROR FIX KIYA (language _ variable define karke)
    language = await get_lang(CallbackQuery.message.chat.id)
    _ = get_string(language)
    keyboard = help_pannel(_, True)
    
    if cb == "settings_back_helper":
        await edit_premium_text(
            CallbackQuery.message.chat.id, CallbackQuery.message.id, _["help_1"].format(SUPPORT_CHAT), keyboard
        )

@app.on_callback_query(filters.regex('mplus'))      
async def mb_plugin_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    # ⚠️ NO HACK HERE EITHER: Native pyrogram buttons
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"mbot_cb")]])
    if cb == "Okieeeeee":
        await CallbackQuery.edit_message_text(f"`something errors`",reply_markup=keyboard,parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await CallbackQuery.edit_message_text(getattr(Helper, cb), reply_markup=keyboard)

