import json

import unreal
import os
from config.config import UNREAL_IMPORT_PATH, BASE_SOURCE
from core.sync_client import get_asset_logs


def import_fbx(asset_data, master_math_path, material_type):
    asset_name = asset_data.get("asset_name", "")
    source_path = asset_data.get("file_path", "").replace("\\", "/")
    base_source = BASE_SOURCE

    if source_path.startswith(base_source):
        relative_path = source_path[len(base_source):]
        folder_structure = os.path.dirname(relative_path)
        destination_path = f"/Game/Meshes/{folder_structure.replace(os.sep, '/')}"

    else:
        destination_path = UNREAL_IMPORT_PATH

    task = unreal.AssetImportTask()
    task.filename = source_path
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

    unreal.log(f"[DEBUG] Calling create_material_instance with: {asset_name}, {master_math_path}, {material_type}")
    if master_math_path:
        create_material_instance(asset_name, master_math_path, material_type, destination_path)
    else:
        unreal.log(f"f[SYNC] Imported mesh only (no material) {asset_name}")

    try:
        with open(asset_data["json_path"], "r+") as f:
            data = json.load(f)
            data["imported"] = True
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        unreal.log(f"[SYNC] Marked as imported {os.path.basename(asset_data['json_path'])}")
    except Exception as e:
        unreal.log_warning(f"[SYNC] Could not set imported flag {e}")


def create_material_instance(asset_name, master_mat_path, material_type, destination_path):
    if "trim" in material_type or "tile" in material_type:
        instance_name = f"MI_{material_type}"
    else:
        instance_name = f"MI_{asset_name}"

    if instance_name.startswith("MI_MI_"):
        instance_name = instance_name.replace("MI_MI_", "MI_")

    instance_path = f"/Game/Materials/M_Instances/{instance_name}"

    if not instance_path.startswith("/Game/") or instance_path.strip() == "/":
        unreal.log_warning(f"[SYNC] Invalid instance path: '{instance_path}' for {asset_name}")
        return

    if unreal.EditorAssetLibrary.does_asset_exist(instance_path):
        unreal.log(f"[SYNC] Material Instance already exists: {instance_path}")
        return

    if "." not in master_mat_path:
        base_name = os.path.basename(master_mat_path)
        master_mat_path = f"{master_mat_path}.{base_name}"

    master_material = unreal.load_asset(master_mat_path)
    if not master_material:
        unreal.log_warning(f"[SYNC] Master Material not found: {master_mat_path}")
        return

    factory = unreal.MaterialInstanceConstantFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    try:
        mi = asset_tools.create_asset(instance_name, "/Game/Materials/M_Instances", unreal.MaterialInstanceConstant,
                                      factory)
        if mi:
            mi.set_editor_property("parent", master_material)
            static_mesh_path = f"{destination_path}/{asset_name}.{asset_name}"
            static_mesh = unreal.load_asset(static_mesh_path)

            if not static_mesh:
                unreal.log_warning(f"[SYNC] Could not find StaticMesh to assign material: {static_mesh_path}")
                return

            try:
                static_mesh.set_material(0, mi)
                unreal.EditorAssetLibrary.save_asset(static_mesh_path)
                unreal.log(f"[SYNC] Assigned material {instance_path} to mesh {static_mesh_path}")
            except Exception as e:
                unreal.log_error(f"[SYNC] Failed to assign material to mesh {asset_name}: {e}")

            unreal.EditorAssetLibrary.save_asset(instance_path)
            unreal.log(f"[SYNC] Created Material Instance: {instance_path} with parent: {master_mat_path}")
        else:
            unreal.log_warning(f"[SYNC] Failed to create Material Instance {instance_path}")
    except Exception as e:
        unreal.log_error(f"[SYNC] Error creating Material Instance {instance_path}: {e}")
