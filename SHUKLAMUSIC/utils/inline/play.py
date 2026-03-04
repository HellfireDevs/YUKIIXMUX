import math
from SHUKLAMUSIC import app
import config
from SHUKLAMUSIC.utils.formatters import time_to_seconds

# 🔥 HACK: Pyrogram bypass ke liye raw JSON dictionaries
def api_btn(text, callback_data=None, url=None, style=None):
    btn = {"text": text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        btn["url"] = url
    if style:
        btn["style"] = style  # 'primary' = Blue, 'danger' = Red
    return btn

def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            api_btn(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style="primary"),
            api_btn(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style="primary"),
        ],
        [
            api_btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style="danger")
        ],
    ]
    return buttons

def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    if 0 < umm <= 10:
        bar = "▰▱▱▱▱▱▱▱▱▱"
    elif 10 < umm < 20:
        bar = "▰▰▱▱▱▱▱▱▱▱"
    elif 20 <= umm < 30:
        bar = "▰▰▰▱▱▱▱▱▱▱"
    elif 30 <= umm < 40:
        bar = "▰▰▰▰▱▱▱▱▱▱"
    elif 40 <= umm < 50:
        bar = "▰▰▰▰▰▱▱▱▱▱"
    elif 50 <= umm < 60:
        bar = "▰▰▰▰▰▰▱▱▱▱"
    elif 60 <= umm < 70:
        bar = "▰▰▰▰▰▰▰▱▱▱"
    elif 70 <= umm < 80:
        bar = "▰▰▰▰▰▰▰▰▱▱"
    elif 80 <= umm < 95:
        bar = "▰▰▰▰▰▰▰▰▰▱" 
    else:
        bar = "▰▰▰▰▰▰▰▰▰▰"
        
    buttons = [
        [
            # Blue Timer Bar
            api_btn(text=f"{played} {bar} {dur}", callback_data="GetTimer", style="primary")
        ],
        [
            # Update Blue, Support Red
            api_btn(text=" ᴜᴘᴅᴀᴛᴇ ", url="https://t.me/heartstealer_x", style="primary"),
            api_btn(text=" sᴜᴘᴘᴏʀᴛ ", url="https://t.me/+N08m5L1mCTU2NTE1", style="danger"),
        ],
        [
            # Mimi Tunes Blue
            api_btn(text=" ˹ ᴍɪᴍɪ ᴛᴜɴᴇs ˼ ♪ ", url="https://t.me/SPSUPPORTT1", style="primary")
        ],
        [
            # Close Red
            api_btn(text=_["CLOSE_BUTTON"], callback_data="close", style="danger")
        ],
    ]
    return buttons

def stream_markup(_, chat_id):
    buttons = [
        [
            api_btn(text=" ᴜᴘᴅᴀᴛᴇ ", url="https://t.me/drxgiveway", style="primary"),
            api_btn(text=" sᴜᴘᴘᴏʀᴛ ", url="https://t.me/drx_supportchat", style="danger"),
        ],
        [
            api_btn(text=" ˹ ᴛιᴅᴀʟ ᴛᴜɴᴇs ˼ ♪ ", url="http://t.me/TidalXMusicBot/tidaltunes", style="primary")
        ], 
        [
            api_btn(text=_["CLOSE_BUTTON"], callback_data="close", style="danger")
        ],
    ]
    return buttons

def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            api_btn(text=_["P_B_1"], callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}", style="primary"),
            api_btn(text=_["P_B_2"], callback_data=f"SHUKLAPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}", style="primary"),
        ],
        [
            api_btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style="danger"),
        ],
    ]
    return buttons

def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            api_btn(text=_["P_B_3"], callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}", style="primary"),
        ],
        [
            api_btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}", style="danger"),
        ],
    ]
    return buttons

def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            api_btn(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style="primary"),
            api_btn(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style="primary"),
        ],
        [
            api_btn(text="◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}", style="primary"),
            api_btn(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}", style="danger"),
            api_btn(text="▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}", style="primary"),
        ],
    ]
    return buttons
    
