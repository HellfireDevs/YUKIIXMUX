from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SHUKLAMUSIC import app
from config import BOT_USERNAME
from SHUKLAMUSIC.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """
❥ ωєℓ¢σмє тσ  ˹ 𝐓ɪᴅᴀʟ ꭙ 𝐌ᴜꜱɪᴄ˼ 🥀 

❥ ʀᴇᴘᴏ ᴄʜᴀᴀʜɪʏe ᴛᴏ ʙᴏᴛ ᴋᴏ 

❥ 3 ɢᴄ ᴍᴀɪ ᴀᴅᴅ ᴋᴀʀ ᴋᴇ 

❥ ᴀᴅᴍɪɴ ʙᴀɴᴏ ᴀᴜʀ sᴄʀᴇᴇɴsʜᴏᴛ 
     
❥ ᴏᴡɴᴇʀ @HEHE_STALKER ᴋᴏ ᴅᴏ ғɪʀ ʀᴇᴘᴏ ᴍɪʟ sᴀᴋᴛɪ ʜᴀɪ 

"""




@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("♡ α∂∂ иσω ♡", url=f"https://t.me/TIDALXMUSICBOT?startgroup=true")
        ],
        [
          InlineKeyboardButton("ѕυρρσɾƚ", url="https://t.me/TIDAL_SUPPORT"),
          InlineKeyboardButton("×͜×┊𝅃𝙎𝙏𝚲𝙇𝙆𝙀𝙍 ꭙ𒌋", url="https://t.me/HEHE_STALKER"),
          ],
               [
                InlineKeyboardButton("ᴏᴛʜᴇʀ ʙᴏᴛs", url=f"https://t.me/TIDALXUPDATES"),
],
[
InlineKeyboardButton("ᴄʜᴇᴄᴋ", url=f"https://t.me/TIDALXMUSICBOT"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://graph.org/file/90ef1bc444de679d65209-335d94a31975f4eda6.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
