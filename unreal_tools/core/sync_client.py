import os
import json
from config.config import LOG_DIR

def get_asset_logs():
    assets = []

    if not os.path.exists(LOG_DIR):
        return assets

    asset_map = {}

    for file in sorted(os.listdir(LOG_DIR), reverse=True):
        if not file.endswith(".json"):
            continue

        filepath = os.path.join(LOG_DIR, file)

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            if data.get("imported", False):
                continue

            asset_name = data.get("asset_name", "")
            timestamp = data.get("timestamp", "")
            if not asset_name:
                continue

            data["json_path"] = filepath

            if asset_name not in asset_map or asset_map[asset_name][0] < timestamp:
                asset_map[asset_name] = (timestamp, data)

        except Exception as e:
            continue

    return [item[1] for item in asset_map.values()]




