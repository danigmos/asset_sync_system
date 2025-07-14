import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import importlib
import config.config
import core.sync_client
import scripts.import_sync
import ui.ui_import_tool

importlib.reload(config.config)
importlib.reload(core.sync_client)
importlib.reload(scripts.import_sync)
importlib.reload(ui.ui_import_tool)

importlib.reload(ui.ui_import_tool)
importlib.reload(scripts.import_sync)

from ui.ui_import_tool import open_window
def launch_tool():
    open_window()

launch_tool()