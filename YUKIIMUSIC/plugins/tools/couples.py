import YUKIIMUSIC.yuki_guard
import os 
import random
from datetime import datetime 
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType

#BOT FILE NAME
from YUKIIMUSIC import app

POLICE = [
    [
        InlineKeyboardButton(
            text="❖ ᴘᴏᴡᴇʀᴇᴅ  ➥ 🌝",
            url=f"https://t.me/Zcziiy",
        ),
    ],
]


def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list
    

def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a

tomorrow = str(dt_tom())
today = str(dt()[0])

# Tumhari static safe image
STATIC_COUPLE_PIC = "https://files.catbox.moe/ty6zcs.jpg"

@app.on_message(filters.command("couples"))
async def ctest(client, message):
    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")
        
    try:
        msg = await message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ...")
        
        # GET LIST OF USERS
        list_of_users = []
        async for i in app.get_chat_members(message.chat.id, limit=50):
            if not i.user.is_bot:
                list_of_users.append(i.user.id)

        # Agar group mein 2 se kam log hain
        if len(list_of_users) < 2:
            return await msg.edit_text("ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴄᴏᴜᴘʟᴇ ʙᴀɴᴀɴᴇ ᴋᴇ ʟɪʏᴇ ᴋᴀᴍ sᴇ ᴋᴀᴍ 2 ʟᴏɢ ᴄʜᴀʜɪʏᴇ!")

        c1_id = random.choice(list_of_users)
        c2_id = random.choice(list_of_users)
        while c1_id == c2_id:
            c2_id = random.choice(list_of_users)

        N1 = (await app.get_users(c1_id)).mention 
        N2 = (await app.get_users(c2_id)).mention
         
        TXT = f"""
**ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :

{N1} + {N2} = 💚

ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""
        # Seedha tumhari di hui image bhej dega
        await message.reply_photo(
            photo=STATIC_COUPLE_PIC, 
            caption=TXT, 
            reply_markup=InlineKeyboardMarkup(POLICE)
        )
        await msg.delete()
        
    except Exception as e:
        print(str(e))
        try:
            await msg.edit_text("❌ Kuch error aa gaya bhai couples generate karne mein.")
        except:
            pass

__mod__ = "COUPLES"
__help__ = """
**» /couples** - Get Todays Couples Of The Group In Interactive View
"""

