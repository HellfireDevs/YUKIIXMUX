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
import config
from YUKIIMUSIC import app
from pyrogram.types import InlineKeyboardButton

# HELLFIRE DEVS HACK: Fixed for Pyrogram Objects
def api_btn(text, callback_data=None, url=None, style=None, custom_emoji_id=None):
    if url:
        url_str = str(url)
        if not url_str.startswith("http") and not url_str.startswith("tg://"):
            url_str = f"https://t.me/{url_str.replace('@', '')}"
        btn = InlineKeyboardButton(text=text, url=url_str)
    else:
        btn = InlineKeyboardButton(text=text, callback_data=callback_data)
        
    if style in ["primary", "danger", "success"]:
        setattr(btn, "style", style)
        
    if custom_emoji_id:
        setattr(btn, "icon_custom_emoji_id", str(custom_emoji_id))
        
    return btn


def start_panel(_):
    buttons = [
        [
            # Add to Group (Green/Success)
            api_btn(
                text=_["S_B_1"], 
                url=f"https://t.me/{app.username}?startgroup=true", 
                style="success", 
                custom_emoji_id="5235682785863153026"
            ),
            # Support Chat (Red/Danger)
            api_btn(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT, 
                style="danger", 
                custom_emoji_id="5206523956537865948"
            ),
        ],
    ]
    return buttons


def private_panel(_):
    safe_owner_id = config.OWNER_ID[0] if isinstance(config.OWNER_ID, list) else config.OWNER_ID
    
    buttons = [
        [
            # Tap To See Magic (Green/Success) - Akela Bada Button
            api_btn(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style="success",
                custom_emoji_id="5249244862359812334"
            )
        ],
        [
            # Help & Commands (Blue/Primary)
            api_btn(
                text=_["S_B_4"], 
                callback_data="settings_back_helper", 
                style="primary", 
                custom_emoji_id="5238162283368035495"
            ),
            # Version Button (Blue/Primary) - Aesthetic Font Match
            api_btn(
                text="˹ 𝚼єʀsιᴏη ˼", 
                callback_data="yuki_version_info", 
                style="primary", 
                custom_emoji_id="5296631769112525274"
            ),
        ],
        [
            # Yuki Tunes / Updates Channel (Blue/Primary)
            api_btn(
                text=_["S_B_6"], 
                url=config.SUPPORT_CHANNEL, 
                style="primary", 
                custom_emoji_id="5253539825360843975"
            ),
            # Chating Hub / Support Chat (Red/Danger)
            api_btn(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT, 
                style="danger", 
                custom_emoji_id="5258208871423425369"
            ),
        ],
        [
            # NEW: Website Button (Normal Color, Full Width) - Bada Wala
            api_btn(
                text="˹ 𝚼єʙsιᴛє ˼", 
                url="https://nex0-1.vercel.app", 
                custom_emoji_id="5262770659267735289" # No style given, defaults to normal color
            ),
        ],
        [
            # My Master (Red/Danger) - Akela Bada Button Niche
            api_btn(
                text=_["S_B_5"], 
                url=f"tg://user?id={safe_owner_id}", 
                style="danger", 
                custom_emoji_id="5201875852735820002"
            ),
        ],
    ]
    return buttons
    
