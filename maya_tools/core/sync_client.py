import requests
from config.config import SERVER_URL


def send_asset_data(payload):
    try:
        response= requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"[SYNC ERROR] Server returned status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[SYNC ERROR] {e}")
        return False