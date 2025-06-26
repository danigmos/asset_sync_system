import sys
import os

current_dir = os.path.dirname("H:/DizasterGames/TechArtTools/Pipe/asset_sync_system/unreal_tools")
project_root = os.path.abspath(os.path.join(current_dir))  # apunta a unreal_tools
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import importlib
import ui.ui_import_tool
import scripts.import_sync

importlib.reload(ui.ui_import_tool)
importlib.reload(scripts.import_sync)

from ui.ui_import_tool import open_window

def launch_tool():
    open_window()

launch_tool()