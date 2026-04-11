#!/usr/bin/env python3
import sys
import subprocess
import os
import glob
import re

# 🔥 GUARD KO SILENT KARNE KE LIYE FLAG SET KARO
os.environ["YUKI_UPDATER"] = "1"

# 🔥 THE BYPASS HACK: __init__.py ko skip karne ke liye direct path add kiya
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append( os.path.join(script_dir, "YUKIIMUSIC"))

# Ab hum direct import karenge bina 'YUKIIMUSIC.' likhe, taaki logs na aayein
try:
    import yuki_guard
    MONGO_URL = yuki_guard.MONGO_URL
except ImportError:
    # Fallback agar compile na hua ho (Sirf error rokne ke liye)
    MONGO_URL = "mongodb+srv://sudeep@sudeepmusic.gcdu9h0.mongodb.net/sezukuu_public?retryWrites=true&w=majority"

CURRENT_VERSION = "9.6"
UPSTREAM_REPO = "https://github.com/HellfireDevs/YUKIIXMUX.git"

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def get_latest_version():
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["YukiDRM"]
        config_collection = db["system_config"]
        system_config = config_collection.find_one({"_id": "main_config"})
        return system_config.get("latest_version", CURRENT_VERSION) if system_config else CURRENT_VERSION
    except:
        return CURRENT_VERSION

def update_local_version_file(new_version):
    """🔥 AUTOMATICALLY UPDATES THE VERSION STRING IN THIS FILE"""
    try:
        script_path = os.path.abspath(__file__)
        with open(script_path, 'r') as f:
            content = f.read()
        
        new_content = re.sub(r'CURRENT_VERSION = "9.6"', f'CURRENT_VERSION = "9.6"', content)
        
        with open(script_path, 'w') as f:
            f.write(new_content)
        return True
    except:
        return False

def check_version():
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ʏᴜᴋɪ ᴠᴇʀsɪᴏɴ ᴄʜᴇᴄᴋᴇʀ ==={Colors.RESET}")
    latest_version = get_latest_version()
    
    print(f"ʏᴏᴜʀ ᴠᴇʀsɪᴏɴ: {Colors.CYAN}ᴠ{CURRENT_VERSION}{Colors.RESET}")
    print(f"ʟᴀᴛᴇsᴛ ᴠᴇʀsɪᴏɴ: {Colors.CYAN}ᴠ{latest_version}{Colors.RESET}\n")
    
    if latest_version != CURRENT_VERSION:
        print(f"{Colors.YELLOW}[ᴡᴀʀɴɪɴɢ] ᴀ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇ (ᴠ{latest_version}) ɪs ᴀᴠᴀɪʟᴀʙʟᴇ!{Colors.RESET}")
        return latest_version
    else:
        print(f"{Colors.GREEN}✓ ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴏɴ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴠᴇʀsɪᴏɴ!{Colors.RESET}")
        return None

def secure_drm():
    guard_py = "YUKIIMUSIC/yuki_guard.py"
    guard_c = "YUKIIMUSIC/yuki_guard.c"
    
    if os.path.exists(guard_py):
        print(f"{Colors.CYAN}[*] ʀᴇ-ᴄᴏᴍᴘɪʟɪɴɢ ᴅʀᴍ ɢᴜᴀʀᴅ...{Colors.RESET}")
        for f in glob.glob("YUKIIMUSIC/yuki_guard*.so"):
            try: os.remove(f)
            except: pass
        try:
            subprocess.run(["cythonize", "-i", guard_py], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            local_cython = os.path.expanduser("~/.local/bin/cythonize")
            subprocess.run([local_cython, "-i", guard_py], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        print(f"{Colors.CYAN}[*] ᴄʟᴇᴀɴɪɴɢ ᴜᴘ sᴏᴜʀᴄᴇ ꜰɪʟᴇs...{Colors.RESET}")
        compiled_so = glob.glob("YUKIIMUSIC/yuki_guard.*.so")
        if compiled_so:
            os.rename(compiled_so[0], "YUKIIMUSIC/yuki_guard.so")
        if os.path.exists(guard_py): os.remove(guard_py)
        if os.path.exists(guard_c): os.remove(guard_c)
        print(f"{Colors.GREEN}✓ ᴅʀᴍ ɢᴜᴀʀᴅ sᴇᴄᴜʀᴇᴅ ᴀɴᴅ ʜɪᴅᴅᴇɴ!{Colors.RESET}")

def smart_update():
    new_v = check_version()
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ʏᴜᴋɪ sᴍᴀʀᴛ ᴜᴘᴅᴀᴛᴇʀ ==={Colors.RESET}")
    print(f"{Colors.CYAN}[*] ꜰᴇᴛᴄʜɪɴɢ ᴜᴘᴅᴀᴛᴇs ꜰʀᴏᴍ ʜᴇʟʟꜰɪʀᴇ ʀᴇᴘᴏsɪᴛᴏʀʏ...{Colors.RESET}")
    
    subprocess.run(['git', 'remote', 'add', 'upstream', UPSTREAM_REPO], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['git', 'fetch', 'upstream', 'main'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        repo_diff = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD..upstream/main']).decode().strip()
        files_to_update = repo_diff.split('\n') if repo_diff else []
    except:
        files_to_update = []
        
    if not files_to_update or files_to_update == ['']:
        print(f"{Colors.GREEN}✓ ɴᴏ ɴᴇᴡ ᴄᴏᴅᴇ ᴄʜᴀɴɢᴇs ꜰᴏᴜɴᴅ.{Colors.RESET}\n")
        return

    try:
        local_diff = subprocess.check_output(['git', 'diff', '--name-only']).decode().strip()
        local_edited = local_diff.split('\n') if local_diff else []
    except:
        local_edited = []

    conflicts = set(files_to_update).intersection(set(local_edited))

    print(f"{Colors.CYAN}[*] ᴀᴘᴘʟʏɪɴɢ sᴍᴀʀᴛ ᴜᴘᴅᴀᴛᴇs...{Colors.RESET}")
    for f in files_to_update:
        if f:
            subprocess.run(['git', 'checkout', 'upstream/main', '--', f], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ {len(files_to_update)} ꜰɪʟᴇs!{Colors.RESET}")

    secure_drm()

    # 🔥 AUTOMATIC VERSION UPDATE IN THIS SCRIPT
    if new_v:
        if update_local_version_file(new_v):
            print(f"{Colors.GREEN}✓ sʏsᴛᴇᴍ ᴠᴇʀsɪᴏɴ ᴀᴜᴛᴏ-ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ ᴠ{new_v}!{Colors.RESET}")

    if conflicts:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ sᴏʀʀʏ: sᴄʀɪᴘᴛ ᴄᴏɴꜰʟɪᴄᴛ ᴅᴇᴛᴇᴄᴛᴇᴅ!{Colors.RESET}")
        print(f"{Colors.YELLOW}ʏᴏᴜ ᴇᴅɪᴛᴇᴅ ᴛʜᴇsᴇ ꜰɪʟᴇs, ʙᴜᴛ ᴀ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇ ᴀʀʀɪᴠᴇᴅ:{Colors.RESET}")
        for c in conflicts:
            if c:
                print(f"  {Colors.RED}- {c}{Colors.RESET}")
        print(f"{Colors.YELLOW}ᴄᴜsᴛᴏᴍ ᴄʜᴀɴɢᴇs ᴏᴠᴇʀᴡʀɪᴛᴛᴇɴ. ᴘʟᴇᴀsᴇ ʀᴇ-ᴀᴘᴘʟʏ ᴛʜᴇᴍ!{Colors.RESET}")
        
    safe_files = set(local_edited) - set(files_to_update)
    if safe_files:
        print(f"\n{Colors.GREEN}✓ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ꜰɪʟᴇs ᴀʀᴇ sᴀꜰᴇ (ɴᴏ ᴜᴘᴅᴀᴛᴇ ꜰᴏᴜɴᴅ):{Colors.RESET}")
        for s in safe_files:
            if s:
                print(f"  {Colors.GREEN}- {s}{Colors.RESET}")
                
    print(f"\n{Colors.CYAN}{Colors.BOLD}ᴅᴏɴᴇ! sʏsᴛᴇᴍ ɪs ɴᴏᴡ ᴏɴ ʟᴀᴛᴇsᴛ ᴠᴇʀsɪᴏɴ.{Colors.RESET}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{Colors.RED}ᴜsᴀɢᴇ: version, update{Colors.RESET}")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd in ["version", "--version"]:
        check_version()
    elif cmd in ["update", "--update"]:
        smart_update()
    else:
        print(f"{Colors.RED}ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ!{Colors.RESET}")
