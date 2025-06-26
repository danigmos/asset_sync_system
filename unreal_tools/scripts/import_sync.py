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

    unreal.log(f"[DEBUG] Calling create_material_instance with: {asset_name}, {master_math_path}, {material_type}")
    create_material_instance(asset_name, master_math_path, material_type)


def create_material_instance(asset_name, master_mat_path, material_type):
    if "trim" in material_type or "tile" in material_type:
        instance_name = f"MI_{material_type}"
    else:
        instance_name = f"MI_{asset_name}"

        # Asegurar que no estamos duplicando MI_
    if instance_name.startswith("MI_MI_"):
        instance_name = instance_name.replace("MI_MI_", "MI_")

    instance_path = f"/Game/Materials/M_Instances/{instance_name}"

    # Validar que el path es válido
    if not instance_path.startswith("/Game/") or instance_path.strip() == "/":
        unreal.log_warning(f"[SYNC] Invalid instance path: '{instance_path}' for {asset_name}")
        return

    if unreal.EditorAssetLibrary.does_asset_exist(instance_path):
        unreal.log(f"[SYNC] Material Instance already exists: {instance_path}")
        return

    # Asegurarse que el master path tiene nombre completo para load_asset
    if "." not in master_mat_path:
        base_name = os.path.basename(master_mat_path)
        master_mat_path = f"{master_mat_path}.{base_name}"

    master_material = unreal.load_asset(master_mat_path)
    if not master_material:
        unreal.log_warning(f"[SYNC] Master Material not found: {master_mat_path}")
        return

    # Crear la instancia
    factory = unreal.MaterialInstanceConstantFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    try:
        mi = asset_tools.create_asset(instance_name, "/Game/Materials/M_Instances", unreal.MaterialInstanceConstant,
                                      factory)
        if mi:
            mi.set_editor_property("parent", master_material)
            static_mesh_path = f"/Game/ImportAssets/{asset_name}.{asset_name}"
            static_mesh = unreal.load_asset(static_mesh_path)

            if not static_mesh:
                unreal.log_warning(f"[SYNC] Could not find StaticMesh to assign material: {static_mesh_path}")
                return

            # Asignar el MI al primer slot
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
