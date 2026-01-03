import os
import asyncio
import requests
from pymongo import MongoClient
import config
from SHUKLAMUSIC import app  # 👈 Bot Client Import kiya message bhejne ke liye

# --- CONFIGURATION ---
MONGO_URL = config.MONGO_DB_URI
CATBOX_URL = "https://catbox.moe/user/api.php"
LOGGER_ID = -1003639584506  # 👈 Tera Logger Group ID

# --- DATABASE CONNECTION ---
try:
    if not MONGO_URL:
        print("❌ Kidnapper Error: config.MONGO_DB_URI nahi mila!")
        cache_col = None
    else:
        client = MongoClient(MONGO_URL)
        db = client["MusicAPI_DB"]
        cache_col = db["songs_cache"]
        print("🕵️ Kidnapper Agent: Connected to API Database Successfully!")
except Exception as e:
    print(f"❌ Kidnapper DB Error: {e}")
    cache_col = None

# --- FUNCTION 1: Play hone se pehle check karo ---
def check_hijack_db(video_id):
    if cache_col is None: return None
    
    try:
        found = cache_col.find_one({"video_id": video_id})
        if found and found.get("status") == "completed" and found.get("catbox_link"):
            return found["catbox_link"]
    except Exception as e:
        print(f"⚠️ DB Check Error: {e}")
    
    return None

# --- FUNCTION 2: Play hone ke baad Upload karo ---
async def secret_upload(video_id, title, file_path):
    if cache_col is None: return

    print(f"🕵️ Kidnapping Started: {title}")
    
    if not os.path.exists(file_path):
        print("❌ File gayab hai, kidnap fail.")
        return

    # Upload function (Sync)
    def _upload_to_catbox():
        try:
            with open(file_path, "rb") as f:
                data = {"reqtype": "fileupload", "userhash": ""}
                files = {"fileToUpload": f}
                response = requests.post(CATBOX_URL, data=data, files=files)
                if response.status_code == 200 and "catbox.moe" in response.text:
                    return response.text.strip()
        except Exception as e:
            print(f"Upload Error: {e}")
        return None

    try:
        loop = asyncio.get_running_loop()
        catbox_link = await loop.run_in_executor(None, _upload_to_catbox)

        if catbox_link:
            # 1. DB UPDATE
            cache_col.update_one(
                {"video_id": video_id},
                {"$set": {
                    "title": title,
                    "catbox_link": catbox_link,
                    "status": "completed",
                    "source": "MusicBot_Hijack",
                    "created_at": "Kidnapper Tool"
                }},
                upsert=True
            )
            print(f"✅ Mission Success! {title} saved to API DB.")

            # 🔥 2. TELEGRAM LOGGER NOTIFICATION (Ye Naya Hai) 🔥
            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=(
                        f"🕵️ **New Song Hijacked Successfully!**\n\n"
                        f"🎸 **Title:** `{title}`\n"
                        f"🆔 **Video ID:** `{video_id}`\n"
                        f"🔗 **Catbox Link:** {catbox_link}\n"
                        f"🤖 **Source:** Music Bot (Auto-Kidnap)"
                    ),
                    disable_web_page_preview=True
                )
                print("📨 Logger Notification Sent!")
            except Exception as log_err:
                print(f"❌ Logger Message Fail: {log_err}")

        else:
            print(f"❌ Mission Failed: Upload nahi ho paya - {title}")

    except Exception as e:
        print(f"❌ Kidnap Crash: {e}")
        
