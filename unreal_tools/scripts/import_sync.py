import unreal
import os
from config.config import UNREAL_IMPORT_PATH
from core.sync_client import get_asset_logs

def import_fbx(asset_data, master_math_path, material_type):
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

    create_material_instance(asset_name, master_math_path, material_type)


def create_material_instance(asset_name, master_mat_path, material_type):
    if "trim" in material_type or "tile" in material_type:
        instance_name = f"MI_{material_type}"
    else:
        instance_name = f"MI_{asset_name}"


    inst_path = f"/Game/Materials/M_Instances/MI_{asset_name}"

    if unreal.EditorAssetLibrary.do_assets_exist(inst_path):
        unreal.log(f"[SYNC] Material instance already exist {inst_path} ")
        return

    master_material : unreal.load_asset(master_mat_path)
    if not master_material:
        unreal.log_warning(f"[SYNC] Master Material not found {master_mat_path}")
        return

    factory = unreal.MaterialInstanceConstantFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.create_asset(instance_name, "/Game/Materials/M_Instances", unreal.MaterialInstanceConstant, factory)

    instance_path = f"/Game/Materials/M_Instances/MI_{instance_name}"
    mi = unreal.load_asset(instance_path)
    if mi:
        mi.set_editor_property("parent", master_material)
        unreal.EditorAssetLibrary.save_asset(instance_path)
        unreal.log(f"[SYNC] Created Material Instance {instance_path}")

# def import_all_assets():
#     logs = get_asset_logs()
#     imported = 0
#
#     for log in logs:
#         if "asset_name" not in log or "file_path" not in log:
#             continue
#
#         import_fbx(log)
#         imported +=1
#
#     unreal.log(f"[SYNC] Total assets imported: {imported}")
