import json
from typing import Any

PATH = "data/config.json"

def read_config() -> dict[str, Any]:
    with open(PATH, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data

def update_config(target_key: str, new_value):
    data = read_config()
    data[target_key] = new_value

    with open(PATH, 'w', encoding="utf-8") as f:
        json.dump(data, f)
    return