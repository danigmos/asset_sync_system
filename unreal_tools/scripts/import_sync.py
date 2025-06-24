import unreal
import os
from config.config import UNREAL_IMPORT_PATH
from core.sync_client import get_asset_logs

def import_fbx(asset_data):
    asset_name = asset_data.get("asset_name", "")
    fbx_file = asset_data.get("file_path", "").replace("\\", "/")

    if not os.path.exists(fbx_file):
        unreal.log_warning(f"[SYNC] fbx not found: {fbx_file}")
        return

    destination_path = UNREAL_IMPORT_PATH

    task = unreal.AssetImportTask()
    task.filename = fbx_file
    task.destination_path = destination_path
    task.automated = True
    task.save = True
    task.replace_existing = True

    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal= False
    options.import_materials = False
    options.import_textures = False
    task.options = options

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    unreal.log(f"[SYNC] IMPORTED : {asset_name}")

def import_all_assets():
    logs = get_asset_logs()
    imported = 0

    for log in logs:
        if "asset_name" not in log or "file_path" not in log:
            continue

        import_fbx(log)
        imported +=1

    unreal.log(f"[SYNC] Total assets imported: {imported}")
