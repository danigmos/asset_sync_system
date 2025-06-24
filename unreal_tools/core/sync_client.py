import os
import json
from config.config import LOG_DIR

def get_asset_logs():
    assets = []
    if not os.path.exists(LOG_DIR):
        return assets

    for file in sorted(os.listdir(LOG_DIR), reverse=True):
        if file.endswith(".json"):
            filepath = os.path.join(LOG_DIR, file)

            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    assets.append(data)
            except Exception as e:
                continue
    return assets



