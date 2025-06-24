from app import create_app
import os
import json

CONFIG_PATH = os.path.abspath('config.json')
with open(CONFIG_PATH, 'r') as f:
    config_data = json.load(f)


app = create_app()

if __name__ == "__main__":
    app.run(debug=config_data.get("DEBUG", False), port=config_data.get("PORT", 5001))