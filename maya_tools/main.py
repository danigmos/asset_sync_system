import sys
from .ui.export_tool import ExportToolUI
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance


def launch_tool():
    global export_tool_window
    try:
        export_tool_window.close()
    except:
        pass

    export_tool_window = ExportToolUI()
    export_tool_window.show()