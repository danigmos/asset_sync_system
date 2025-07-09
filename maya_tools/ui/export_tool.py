import os
import maya.cmds as cmds
from maya.api import OpenMaya
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore, QtGui
from shiboken6 import wrapInstance
from core.sync_client import send_asset_data


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return None


class ExportToolUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(ExportToolUI, self).__init__(parent)
        self.setWindowTitle("Asset Sync | Maya")
        self.setMinimumWidth(500)

        self.asset_name = ""
        self.material_name = ""

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.adjustSize()
        self.setStyleSheet("background-color: #222;")

        self.selection_callback = OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.update_from_selection)


    def create_widgets(self):
        self.filepath = QtWidgets.QLineEdit()
        self.select_file_path = QtWidgets.QPushButton()
        self.select_file_path.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_file_path.setToolTip("Select Export folder")

        self.asset_name_label = QtWidgets.QLabel("No asset selected")
        self.material_label = QtWidgets.QLabel("No material found")

        self.export_button = QtWidgets.QPushButton("Export Selected")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        self.collision_label = QtWidgets.QLabel("No collisions detected")

    def create_layouts(self):

        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath)
        file_path_layout.addWidget(self.select_file_path)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Export Path", file_path_layout)
        form_layout.addRow("Asset:", self.asset_name_label)
        form_layout.addRow("Material:", self.material_label)
        form_layout.addRow("Collisions:", self.collision_label)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.select_file_path.clicked.connect(self.select_export_path)
        self.export_button.clicked.connect(self.export_selected)
        self.cancel_button.clicked.connect(self.close)

    def select_export_path(self):
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if file_path:
            self.filepath.setText(file_path)


    def export_selected(self):
        selection = cmds.ls(selection=True, long= True)
        if not selection:
            cmds.warning("No objects selected")
            return

        export_path = self.filepath.text()
        if not export_path or not os.path.exists(export_path):
            cmds.warning("Please choose a valid path")
            return

        asset_name = self.asset_name_label.text().strip()
        material_name = self.material_label.text().strip()

        if not asset_name:
            cmds.warning("No asset name, Please refresh selection")
            return

        full_path = os.path.join(export_path, f"{asset_name}.fbx").replace("\\", "/")

        try:
            cmds.select(selection, r=True)
            cmds.file(full_path, force=True, options="v=0", type="FBX export", pr=True, es=True)
        except Exception as e:
            cmds.warning(f"Export failed: {e}")
            return

        payload = {
            "asset_name" : self.asset_name,
            "asset_material" : material_name,
            "file_path" : full_path
        }
        success = send_asset_data(payload)
        if success:
            cmds.inViewMessage(amg=f"<h1>{self.asset_name}</h1> exported and synced", pos='midCentedTop', fade=True)
        else:
            cmds.warning("Failed to sync asset with server")


    def get_material_name_from_object(self, obj):
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if not shapes:
            return "default"
        for shape in shapes:
            shading_engines = cmds.listConnections(shape, type="shadingEngine") or []
            for sg in shading_engines:
                materials = cmds.listConnections(sg + ".surfaceShader", source=True) or []
                for mat in materials:
                    return mat
        return "default"

    def update_from_selection(self, *args):
        selection = cmds.ls(selection=True)
        if not selection:
            self.asset_name = "No asset selected"
            self.material_name = "No material_found"
            self.asset_name_label.setText(self.asset_name)
            self.material_label.setText(self.material_name)
            return

        primary_asset = next((obj for obj in selection if not os.path.basename(obj).lower().startswith("ucx_")), selection[0])
        self.asset_name = os.path.basename(primary_asset)
        self.asset_name_label.setText(self.asset_name)

        material_name = self.get_material_name_from_object(primary_asset)
        self.material_label.setText(material_name if material_name else "default")

        collisions = [os.path.basename(obj) for obj in selection if os.path.basename(obj).lower().startswith("ucx_")]
        if collisions:
            self.collision_label.setText(f"{len(collisions)} ({', '.join(collisions)})")
        else:
            self.collision_label.setText("No collisions detected")

    def closeEvent(self, event):
        try:
            OpenMaya.MMessage.removeCallback(self.selection_callback)
        except:
            pass
        event.accept()