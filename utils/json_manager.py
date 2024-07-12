# utils/json_manager.py
import json
import os

class JsonManager:
    @staticmethod
    def load_json(file_path, default=None):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default if default is not None else {}

    @staticmethod
    def save_json(file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)