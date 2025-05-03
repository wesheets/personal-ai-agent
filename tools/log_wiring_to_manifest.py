
import json
import os
from datetime import datetime

MANIFEST_PATH = "logs/wiring_manifest.json"
FILE_TREE_PATH = "app/memory/file_tree.json"

def load_file_tree():
    if not os.path.exists(FILE_TREE_PATH):
        raise FileNotFoundError("file_tree.json not found")
    with open(FILE_TREE_PATH, "r") as f:
        return json.load(f)

def validate_file_in_tree(file_path, file_tree):
    return any(entry.get("path") == file_path for entry in file_tree)

def log_wiring_to_manifest(file_path, imports=None, status="wired"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")

    file_tree = load_file_tree()
    if not validate_file_in_tree(file_path, file_tree):
        raise ValueError(f"{file_path} is not declared in file_tree.json")

    entry = {
        "file": file_path,
        "status": status,
        "registered_imports": imports or [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "validated_against": "file_tree.json"
    }

    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)

    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(entry)

    with open(MANIFEST_PATH, "w") as f:
        json.dump(data, f, indent=2)

    return True
