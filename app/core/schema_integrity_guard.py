# schema_integrity_guard.py

import hashlib
import json

def snapshot_schema(path):
    with open(path, "r") as f:
        content = f.read()
    return hashlib.sha256(content.encode()).hexdigest()

def compare_schema_snapshots(current, baseline):
    return current == baseline
