import os
import sys
from PySide2 import QtWidgets, QtCore, QtGui
import unreal
from core.sync_client import get_asset_logs
from scripts.import_sync import import_fbx


class SyncUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SyncUI, self).__init__(parent)

        self.setWindowTitle("Asset Sync Importer")
        self.setMinimumWidth(700)

        self.assets = get_asset_logs()
        self.widgets = {}
        self.table = QtWidgets.QTableWidget(len(self.assets), 3)
        self.table.setHorizontalHeaderLabels(["Asset", "Material", "Master Material"])
        self.import_button = QtWidgets.QPushButton("Import Assets")
        self.create_ui()

    def create_ui(self):

        for row, asset in enumerate(self.assets):
            asset_name = asset.get("asset_name", "Unnamed")
            material_asset = asset.get("asset_material", "default")

            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(asset_name))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(material_asset))

            combo = QtWidgets.QComboBox()
            master_mats = self.find_master_material()
            combo.addItems(master_mats)

            instance_name = f"MI_{material_asset}" if any(
                tag in material_asset.lower() for tag in ["trim", "tile"]) else f"MI_{asset_name}"
            instance_path = f"/Game/Materials/M_Instances/{instance_name}"
            if unreal.EditorAssetLibrary.do_assets_exist(instance_path):
                combo.setCurrentText("Instance Already Exists")
                combo.setEnabled(False)

            self.table.setCellWidget(row, 2, combo)
            self.widgets[asset_name] = combo

        self.import_button.clicked.connect(self.import_assets)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.import_button)


    def find_master_material(self):
        all_assets = unreal.EditorAssetLibrary.list_assets("/Game/Materials/M_Master", recursive=True)
        return [path for path in all_assets if "MM_" in os.path.basename(path)]


    def import_assets(self):
        for asset in self.assets:
            name = asset["asset_name"]
            mat_type = asset.get("asset_material", "unique").lower()
            combo = self.widgets.get(name)

            if combo and combo.currentText() != "Instance Already Exists":
                master_path = combo.currentText()
                import_fbx(asset, master_path, mat_type)




def open_window():
    """
    Create tool window.
    """
    if QtWidgets.QApplication.instance():
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


#open_window()

