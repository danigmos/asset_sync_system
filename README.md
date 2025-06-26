# Asset Sync Tool – Cross-Platform Asset Sync System for Maya, Unreal & Flask

**Asset Sync Tool** is a pipeline utility built to accelerate and standardize asset transfer between **Maya**, **Unreal Engine**, and a centralized **Flask server**. this tool automates asset export, material assignment, and import.

---

## Features

- **Cross-software Asset Sync** (Maya → Flask → Unreal Engine)
- **Smart Material Instance Creation** based on asset type (`unique`, `trim`, `tile`)
- **Automatic Metadata Logging** via `.json` over HTTP POST
- 🖼**Custom UI in Maya and Unreal** using PySide2, embedded directly into each host
- **Clean Folder Structure** and reusable config system
- **Material Reuse Logic** avoids duplicate material instances

---

## Components

### 1. Maya Tool
- Built in **PySide2 + Maya.cmds**
- UI allows selection of mesh and auto-detection of material type.
- On export:
  - Saves `.fbx` in defined folder
  - Creates `.json` metadata file
  - Sends metadata to Flask server via HTTP

### 2. Flask Server
- Receives metadata at `/sync` endpoint
- Stores JSON logs with timestamps
- Renders a simple web interface for browsing assets
- Overwrites logs for repeated syncs of the same asset

### 3. Unreal Engine Tool
- Embedded PySide2 UI using `unreal.parent_external_window_to_slate()`
- Reads all synced JSONs
- Lets user select Master Materials for each asset
- On import:
  - FBX is imported into `/Game/Assets/...`
  - If Material Instance (MI_*) doesn't exist, it’s created and linked
  - Material naming rules:
    - `MI_assetName` for `unique`
    - `MI_trimXX` / `MI_tileXX` for `trim` or `tile`

---
