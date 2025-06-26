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

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #3c3f41;
                alternate-background-color: #2b2b2b;
                gridline-color: #5c5c5c;
            }
            QHeaderView::section {
                background-color: #444;
                color: white;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #5c5c5c;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QComboBox {
                background-color: #444;
                color: white;
                border: 1px solid #5c5c5c;
                padding: 4px;
            }
            QPushButton {
                background-color: #555;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            """)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        master_mats = self.find_master_material()
        name_map = {}
        combo_path_map = {}

        for m in master_mats:
            pretty_name = os.path.basename(m).split(".")[-1]
            if pretty_name in name_map:
                count = name_map[pretty_name] + 1
                new_name = f"{pretty_name}_{count}"
                while new_name in name_map:
                    count += 1
                    new_name = f"{pretty_name}_{count}"
                pretty_name = new_name
                unreal.log_warning(f"[SYNC] Duplicate material name found. Renamed to: {pretty_name}")
            name_map[pretty_name] = name_map.get(pretty_name, 0)
            combo_path_map[pretty_name] = m

        for row, asset in enumerate(self.assets):
            asset_name = asset.get("asset_name", "").strip()
            material_asset = asset.get("asset_material", "default").strip()

            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(asset_name))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(material_asset))

            combo = QtWidgets.QComboBox()
            combo.addItems(combo_path_map.keys())
            combo.path_map = combo_path_map

            instance_name = f"MI_{material_asset}" if any(
                tag in material_asset.lower() for tag in ["trim", "tile"]) else f"MI_{asset_name}"
            instance_path = f"/Game/Materials/M_Instances/{instance_name}"

            if not instance_name or not instance_path.startswith("/Game/") or instance_path.strip() == "/":
                unreal.log_warning(f"[SYNC] Skipping invalid instance path: '{instance_path}' for asset: {asset_name}")
                continue

            if unreal.EditorAssetLibrary.does_asset_exist(instance_path):
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

            if not combo:
                unreal.log_warning(f"[SYNC] No combo found for asset {name}")
                continue

            selected_text = combo.currentText()
            if selected_text == "Instance Already Exists":
                continue

            master_path = combo.path_map.get(selected_text, None)
            if not master_path:
                unreal.log_warning(f"[SYNC] No master material path found for {selected_text}")
                continue

            unreal.log(f"[DEBUG] Selected Master Material: {selected_text} → {master_path}")
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

    SyncUI.window = SyncUI()
    SyncUI.window.show()
    SyncUI.window.setObjectName('toolWindow')  # update this with something unique to your tool
    SyncUI.window.setWindowTitle('Sample Tool')
    unreal.parent_external_window_to_slate(SyncUI.window.winId())


