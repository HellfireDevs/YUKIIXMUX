from typing import Union
from SHUKLAMUSIC import app

# 🔥 HELLFIRE DEVS HACK: Raw API Button Generator (100% Safe)
def api_btn(text, callback_data=None, url=None, style=None, custom_emoji_id=None):
    btn = {"text": text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        url_str = str(url)
        if not url_str.startswith("http") and not url_str.startswith("tg://"):
            url_str = f"https://t.me/{url_str.replace('@', '')}"
        btn["url"] = url_str
    if style in ["primary", "danger", "success"]:
        btn["style"] = style  
    if custom_emoji_id:
        btn["icon_custom_emoji_id"] = str(custom_emoji_id) 
    return btn


def help_pannel(_, START: Union[bool, int] = None):
    # Close Button (Red + 💀)
    first = [api_btn(text=_["CLOSE_BUTTON"], callback_data=f"close", style="danger", custom_emoji_id="5999100917645841519")]
    
    # Next/Back Menu Buttons (Blue & Red)
    second = [
        api_btn(
            text=_["BACK_PAGE"],
            callback_data=f"mbot_cb",
            style="primary",
            custom_emoji_id="6001419401121765310"
        ),
        api_btn(
            text=_["BACK_BUTTON"],
            callback_data=f"settingsback_helper",
            style="danger",
            custom_emoji_id="5998834801472182366"
        ),
        api_btn(
            text=_["NEXT_PAGE"],
            callback_data=f"mbot_cb",
            style="primary",
            custom_emoji_id="6001483331709966655"
        ),
    ]
    
    # Original START logic kept EXACTLY as it is!
    mark = second if START else first
    
    upl = [
        [
            api_btn(text=_["H_B_1"], callback_data="help_callback hb1", style="primary"),
            api_btn(text=_["H_B_2"], callback_data="help_callback hb2", style="primary"),
            api_btn(text=_["H_B_3"], callback_data="help_callback hb3", style="primary"),
        ],
        [
            api_btn(text=_["H_B_4"], callback_data="help_callback hb4", style="primary"),
            api_btn(text=_["H_B_5"], callback_data="help_callback hb5", style="primary"),
            api_btn(text=_["H_B_6"], callback_data="help_callback hb6", style="primary"),
        ],
        [
            api_btn(text=_["H_B_7"], callback_data="help_callback hb7", style="primary"),
            api_btn(text=_["H_B_8"], callback_data="help_callback hb8", style="primary"),
            api_btn(text=_["H_B_9"], callback_data="help_callback hb9", style="primary"),
        ],
        [
            api_btn(text=_["H_B_10"], callback_data="help_callback hb10", style="primary"),
            api_btn(text=_["H_B_11"], callback_data="help_callback hb11", style="primary"),
            api_btn(text=_["H_B_12"], callback_data="help_callback hb12", style="primary"),
        ],
        [
            api_btn(text=_["H_B_13"], callback_data="help_callback hb13", style="primary"),
            api_btn(text=_["H_B_14"], callback_data="help_callback hb14", style="primary"),
            api_btn(text=_["H_B_15"], callback_data="help_callback hb15", style="primary"),
        ],
        mark,
    ]
    return upl


def help_back_markup(_):
    upl = [
        [
            api_btn(
                text=_["BACK_BUTTON"],
                callback_data=f"settings_back_helper",
                style="danger",
                custom_emoji_id="5998834801472182366"
            ),
        ]
    ]
    return upl


def private_help_panel(_):
    buttons = [
        [
            api_btn(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style="primary",
                custom_emoji_id="6001132493011425597"
            ),
        ],
    ]
    return buttons
    
