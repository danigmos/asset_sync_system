from flask import Blueprint, request, jsonify, render_template, current_app
import os
import json
from datetime import datetime


main = Blueprint('main', __name__)


def get_log_dir():
    log_dir = os.path.abspath(current_app.config["LOG_DIR"])
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


@main.route('/')
def index():
    log_dir = get_log_dir()
    json_files = [f for f in os.listdir(log_dir) if f.endswith(".json")]
    json_files.sort(reverse=True)

    assets = []
    for file in json_files:
        with open(os.path.join(log_dir, file), "r") as f:
            try:
                data = json.load(f)
                assets.append(data)
            except Exception:
                continue
    return render_template("index.html", assets = assets)


@main.route("/sync", methods=["POST"])
def sync_asset():
    data = request.get_json()
    if not data or "asset_name" not in data or "file_path" not in data:
        return jsonify({"error": "Invalid data"}), 400

    asset_name = data["asset_name"]
    file_path = data["file_path"]
    log_dir = get_log_dir()

    existing_file = None

    for file in os.listdir(log_dir):
        if file.endswith(".json") and file.startswith(asset_name):
            full_path = os.path.join(log_dir, file)
            try:
                with open(full_path, "r") as f:
                    existing_data = json.load(f)
                    if existing_data.get("file_path") == file_path:
                        existing_file = full_path
                        break
            except:
                continue

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data["timestamp"] = timestamp

    if existing_file:
        filepath = existing_file
    else:
        filename = f"{asset_name}_{timestamp}.json"
        filepath = os.path.join(log_dir, filename)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

    return jsonify({"status": f"Asset '{data['asset_name']}' saved. "}), 200