import sys
import os
import unreal
from PySide2 import QtWidgets, QtCore, QtGui

class SyncUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SyncUI, self).__init__(parent)
        self.setWindowTitle("Asset Sync Tool")
        self.setMinimumSize(400, 200)

        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.label = QtWidgets.QLabel("Bienvenido a Asset Sync Tool")
        self.import_button = QtWidgets.QPushButton("Importar Assets")

    def create_layouts(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.import_button)

# Lanzador

def openWindow():
    """
    Create tool window.
    """
    if QtWidgets.QApplication.instance():
        # Id any current instances of tool and destroy
        for win in (QtWidgets.QApplication.allWindows()):
            if 'toolWindow' in win.objectName():  # update this name to match name below
                win.destroy()
    else:
        QtWidgets.QApplication(sys.argv)

    # load UI into QApp instance
    SyncUI.window = SyncUI()
    SyncUI.window.show()
    SyncUI.window.setObjectName('toolWindow')  # update this with something unique to your tool
    SyncUI.window.setWindowTitle('Sample Tool')
    unreal.parent_external_window_to_slate(SyncUI.window.winId())

openWindow()