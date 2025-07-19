import os
import subprocess
import shutil
import pygetwindow as gw  # type: ignore
import time
import json
from typing import Dict, Optional
from typing import TypedDict
from pygetwindow._pygetwindow_win import Win32Window  # type: ignore

class CurrentApp(TypedDict):
    name: Optional[str]
    window: Optional[Win32Window]

current_app: CurrentApp = {"name": None, "window": None}
INDEX_FILE = "app_index.json"
indexed_apps: Dict[str, str] = {}

def index_installed_apps() -> Dict[str, str]:
    app_paths: Dict[str, str] = {}
    common_dirs = [
        os.environ.get('ProgramFiles', 'C:\\Program Files'),
        os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'),
        os.path.expanduser('~\\AppData\\Local\\Programs'),
        'C:\\Windows\\System32',
        os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs'),
        'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs'
    ]

    for base_dir in common_dirs:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.exe'):
                    name = file.lower().replace('.exe', '')
                    if name not in app_paths:
                        app_paths[name] = os.path.join(root, file)
    return app_paths

def load_or_build_index() -> Dict[str, str]:
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    else:
        index = index_installed_apps()
        with open(INDEX_FILE, "w") as f:
            json.dump(index, f)
        return index

indexed_apps = load_or_build_index()

def bring_window_to_front(title_contains: str) -> bool:
    time.sleep(1.0)  # Let app window spawn
    for window_title in gw.getAllTitles():
        if title_contains.lower() in window_title.lower():
            win = gw.getWindowsWithTitle(window_title)[0]
            try:
                win.minimize()
                win.maximize()
                win.activate()
            except Exception as e:
                print(f"[WARN] Could not bring window to front: {e}")
            current_app["window"] = win
            return True
    return False

def launch_app(app_name: str) -> str:
    try:
        app_name_clean = app_name.lower().strip()
        exe_path: Optional[str] = None

        # Step 1: Try system PATH
        exe_path = shutil.which(app_name_clean)

        # Step 2: Try indexed apps
        if not exe_path:
            exe_path = indexed_apps.get(app_name_clean)

        if not exe_path:
            return f"❌ Couldn't find any executable for '{app_name}' on your system."

        subprocess.Popen(exe_path)
        current_app["name"] = app_name_clean

        focused = bring_window_to_front(app_name_clean)
        return f"✅ {app_name.capitalize()} opened." if focused else f"ℹ️ {app_name.capitalize()} launched, but window not focused."

    except Exception as e:
        print(f"[ERROR] Failed to launch app: {e}")
        return f"❌ Error while opening {app_name}: {str(e)}"
